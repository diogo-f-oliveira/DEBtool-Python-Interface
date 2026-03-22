import pandas as pd
import pytest

from DEBtoolPyIF.multitier import TierHierarchy, TierHierarchyError


@pytest.fixture
def hierarchy():
    return TierHierarchy(
        tier_names=["breed", "diet", "individual"],
        entities={
            "breed": ["male"],
            "diet": ["CTRL", "TMR"],
            "individual": ["PT1", "PT2", "PT3"],
        },
        parents={
            "diet": {"CTRL": "male", "TMR": "male"},
            "individual": {"PT1": "CTRL", "PT2": "CTRL", "PT3": "TMR"},
        },
    )


def test_tier_hierarchy_supports_basic_tree_navigation(hierarchy):
    assert hierarchy.root_tier == "breed"
    assert hierarchy.get_entities("diet") == ("CTRL", "TMR")
    assert hierarchy.get_matlab_entities("diet") == ("CTRL", "TMR")
    assert hierarchy.get_parent("breed", "male") is None
    assert hierarchy.get_parent("individual", "PT1") == "CTRL"
    assert hierarchy.get_matlab_entity_id("individual", "PT1") == "PT1"
    assert hierarchy.get_children("breed", "male") == ("CTRL", "TMR")
    assert hierarchy.get_children("diet", "CTRL") == ("PT1", "PT2")
    assert hierarchy.get_children("individual", "PT1") == tuple()


def test_tier_hierarchy_returns_ordered_paths_and_descendants(hierarchy):
    assert hierarchy.get_path("diet", "CTRL") == {
        "breed": "male",
        "diet": "CTRL",
    }
    assert hierarchy.get_path("individual", "PT3") == {
        "breed": "male",
        "diet": "TMR",
        "individual": "PT3",
    }
    assert hierarchy.get_descendants("breed", "male", "individual") == ("PT1", "PT2", "PT3")
    assert hierarchy.get_descendants("diet", "CTRL", "individual") == ("PT1", "PT2")


def test_tier_hierarchy_can_be_built_from_complete_paths():
    hierarchy = TierHierarchy.from_paths(
        tier_names=["breed", "diet", "individual"],
        paths=[
            {"breed": "male", "diet": "CTRL", "individual": "PT1"},
            {"breed": "male", "diet": "CTRL", "individual": "PT2"},
            {"breed": "male", "diet": "TMR", "individual": "PT3"},
        ],
    )

    assert hierarchy.get_entities("breed") == ("male",)
    assert hierarchy.get_entities("diet") == ("CTRL", "TMR")
    assert hierarchy.get_children("diet", "CTRL") == ("PT1", "PT2")


def test_tier_hierarchy_can_build_paths_that_terminate_early():
    hierarchy = TierHierarchy.from_paths(
        tier_names=["sex", "diet", "individual"],
        paths=[
            {"sex": "male", "diet": "CTRL", "individual": "M1"},
            {"sex": "female"},
        ],
    )

    assert hierarchy.get_entities("sex") == ("male", "female")
    assert hierarchy.get_children("sex", "female") == tuple()
    assert hierarchy.get_descendants("sex", "female", "individual") == tuple()


def test_tier_hierarchy_rejects_non_contiguous_paths():
    with pytest.raises(TierHierarchyError, match="contiguous root-to-entity lineage"):
        TierHierarchy.from_paths(
            tier_names=["sex", "diet", "individual"],
            paths=[
                {"sex": "female", "individual": "F1"},
            ],
        )


def test_tier_hierarchy_can_export_materialized_path_dataframe(hierarchy):
    expected = pd.DataFrame(
        [
            {"tier": "breed", "entity": "male", "breed": "male", "diet": None, "individual": None},
            {"tier": "diet", "entity": "CTRL", "breed": "male", "diet": "CTRL", "individual": None},
            {"tier": "diet", "entity": "TMR", "breed": "male", "diet": "TMR", "individual": None},
            {"tier": "individual", "entity": "PT1", "breed": "male", "diet": "CTRL", "individual": "PT1"},
            {"tier": "individual", "entity": "PT2", "breed": "male", "diet": "CTRL", "individual": "PT2"},
            {"tier": "individual", "entity": "PT3", "breed": "male", "diet": "TMR", "individual": "PT3"},
        ]
    ).set_index(["tier", "entity"])

    actual = hierarchy.to_dataframe()

    pd.testing.assert_frame_equal(actual, expected[["breed", "diet", "individual"]])


def test_tier_hierarchy_can_be_built_from_materialized_path_dataframe(hierarchy):
    dataframe = hierarchy.to_dataframe()

    rebuilt = TierHierarchy.from_dataframe(dataframe)

    assert rebuilt.tier_names == hierarchy.tier_names
    assert rebuilt.entities == hierarchy.entities
    assert rebuilt.parents == hierarchy.parents
    pd.testing.assert_frame_equal(rebuilt.to_dataframe(), dataframe)


def test_tier_hierarchy_sanitizes_entity_names_for_matlab_usage():
    hierarchy = TierHierarchy(
        tier_names=["diet", "individual"],
        entities={
            "diet": ["TMR High", "123-CTRL"],
            "individual": ["PT 1", "PT-2"],
        },
        parents={
            "individual": {"PT 1": "TMR High", "PT-2": "123-CTRL"},
        },
    )

    assert hierarchy.get_matlab_entity_id("diet", "TMR High") == "TMR_High"
    assert hierarchy.get_matlab_entity_id("diet", "123-CTRL") == "x123_CTRL"
    assert hierarchy.get_matlab_entity_id("individual", "PT 1") == "PT_1"
    assert hierarchy.get_matlab_entities("individual") == ("PT_1", "PT_2")


def test_tier_hierarchy_rejects_sanitization_collisions():
    with pytest.raises(TierHierarchyError, match="sanitize to the same MATLAB field name"):
        TierHierarchy(
            tier_names=["individual"],
            entities={
                "individual": ["PT-1", "PT 1"],
            },
        )


def test_tier_hierarchy_rejects_missing_parent_mapping():
    with pytest.raises(TierHierarchyError, match="Missing parent mapping for tier 'individual'"):
        TierHierarchy(
            tier_names=["breed", "diet", "individual"],
            entities={
                "breed": ["male"],
                "diet": ["CTRL", "TMR"],
                "individual": ["PT1", "PT2"],
            },
            parents={
                "diet": {"CTRL": "male", "TMR": "male"},
            },
        )


def test_tier_hierarchy_rejects_unknown_parent_entity():
    with pytest.raises(TierHierarchyError, match="does not exist in tier 'breed'"):
        TierHierarchy(
            tier_names=["breed", "diet"],
            entities={
                "breed": ["male"],
                "diet": ["CTRL"],
            },
            parents={
                "diet": {"CTRL": "female"},
            },
        )


def test_tier_hierarchy_rejects_inconsistent_parents_across_paths():
    with pytest.raises(TierHierarchyError, match="inconsistent parents"):
        TierHierarchy.from_paths(
            tier_names=["breed", "diet", "individual"],
            paths=[
                {"breed": "male", "diet": "CTRL", "individual": "PT1"},
                {"breed": "male", "diet": "TMR", "individual": "PT1"},
            ],
        )


def test_tier_hierarchy_rejects_invalid_dataframe_shape():
    dataframe = pd.DataFrame(
        [
            {"tier": "diet", "entity": "CTRL", "breed": "male", "diet": None},
        ]
    )

    with pytest.raises(TierHierarchyError, match="deepest populated tier is 'breed'"):
        TierHierarchy.from_dataframe(dataframe)
