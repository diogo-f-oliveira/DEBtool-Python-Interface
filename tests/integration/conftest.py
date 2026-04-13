from importlib import import_module
from pathlib import Path
import sys

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
EXAMPLES_ROOT = REPO_ROOT / "examples"

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def discover_examples() -> list[str]:
    """Find example folders that match the expected interface layout."""
    example_names = []
    for folder in EXAMPLES_ROOT.iterdir():
        if not folder.is_dir():
            continue
        if (
            (folder / "data.py").is_file()
            and (folder / "tier_structure.py").is_file()
            and (folder / "estimation.py").is_file()
            and (folder / "data").is_dir()
        ):
            example_names.append(folder.name)
    return sorted(example_names)


EXAMPLE_NAMES = discover_examples()
ESTIMATION_RESULTS_CACHE = {}


def pytest_generate_tests(metafunc):
    if "example_name" in metafunc.fixturenames:
        metafunc.parametrize("example_name", EXAMPLE_NAMES, ids=EXAMPLE_NAMES)


@pytest.fixture(scope="session")
def examples_root() -> Path:
    return EXAMPLES_ROOT


@pytest.fixture(scope="session")
def example_names() -> list[str]:
    return EXAMPLE_NAMES


@pytest.fixture
def import_example_data_module():
    def _import(example_name: str):
        return import_module(f"examples.{example_name}.data")

    return _import


@pytest.fixture
def import_example_tier_module():
    def _import(example_name: str):
        return import_module(f"examples.{example_name}.tier_structure")

    return _import


@pytest.fixture
def import_example_estimation_module():
    def _import(example_name: str):
        return import_module(f"examples.{example_name}.estimation")

    return _import


@pytest.fixture
def estimated_multitier(
    example_name,
    examples_root,
    import_example_data_module,
    import_example_tier_module,
    import_example_estimation_module,
    tmp_path_factory,
):
    cache_key = example_name
    if cache_key in ESTIMATION_RESULTS_CACHE:
        return ESTIMATION_RESULTS_CACHE[cache_key]

    pytest.importorskip("matlab.engine")

    data_module = import_example_data_module(example_name)
    tier_module = import_example_tier_module(example_name)
    estimation_module = import_example_estimation_module(example_name)

    output_folder = tmp_path_factory.mktemp(f"{example_name}_multitier_outputs")
    original_output_folder = tier_module.ESTIMATION_FOLDER
    tier_module.ESTIMATION_FOLDER = str(output_folder)

    try:
        data = data_module.load_data(str(examples_root / example_name / "data"))

        try:
            multitier = tier_module.create_tier_structure(data, matlab_session="auto")
        except Exception as exc:
            pytest.skip(f"MATLAB-backed estimation setup is unavailable: {exc}")

        estimation_settings = getattr(
            estimation_module,
            "NELDER_MEAD_ESTIMATION_TEST_SETTINGS",
            estimation_module.FAST_TEST_ESTIMATION_SETTINGS,
        )

        estimation_module.run_multitier_estimation(
            multitier,
            estimation_settings=estimation_settings,
        )

        result = (multitier, Path(output_folder))
        ESTIMATION_RESULTS_CACHE[cache_key] = result
        return result
    finally:
        tier_module.ESTIMATION_FOLDER = original_output_folder
