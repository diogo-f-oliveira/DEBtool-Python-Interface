import pytest
from DEBtoolPyIF import MultiTierResults


@pytest.mark.integration
@pytest.mark.slow
@pytest.mark.matlab
def test_bos_taurus_angus_load_estimation_results_uses_saved_metadata(
    estimated_multitier,
    import_example_estimation_module,
):
    multitier, output_folder = estimated_multitier
    if multitier.species_name != "Bos_taurus_Angus":
        pytest.skip("This loader contract test is specific to the Bos_taurus_Angus example.")

    estimation_module = import_example_estimation_module("Bos_taurus_Angus")

    assert output_folder.is_dir()

    loaded_results = estimation_module.load_estimation_results(output_folder)

    assert isinstance(loaded_results, MultiTierResults)
    assert set(loaded_results.tiers) == set(multitier.tier_names)
    for tier_name in multitier.tier_names:
        live_tier = multitier.tiers[tier_name]
        tier_result = loaded_results.tiers[tier_name]
        assert tier_result.metadata is not None
        assert tier_result.summary is not None
        assert tier_result.estimation_settings == live_tier.estimation_settings
        assert tier_result.estim_start_time == live_tier.estim_start_time
        assert tier_result.estim_end_time == live_tier.estim_end_time
        assert tier_result.metadata["elapsed_duration_seconds"] == live_tier.result_metadata["elapsed_duration_seconds"]
        assert tier_result.estimation_iterations == live_tier.estimation_iterations
        assert tier_result.estim_start_time is not None
        assert tier_result.estim_end_time is not None
        assert tier_result.estimation_iterations
