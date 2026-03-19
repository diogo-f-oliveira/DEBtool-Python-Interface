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
