"""Integration tests for the single-species (regular Add-my-Pet) Danio rerio example.

The multitier example contract in ``conftest.py`` does not apply here: this example has no tiers, so it is
tested directly through its ``estimation`` module.
"""

import math

import pytest

from DEBtoolPyIF.estimation_files import write_estimation_files

from examples.Danio_rerio import estimation as danio_estimation
from examples.Danio_rerio.data import MOCK_TRUE_PARS
from examples.Danio_rerio.templates import SPECIES_NAME, build_estimation_templates


def _generated_file(folder, prefix: str):
    return folder / f"{prefix}_{SPECIES_NAME}.m"


@pytest.mark.integration
def test_danio_rerio_example_renders_species_estimation_files(tmp_path):
    context = danio_estimation.build_context("fast", output_folder=tmp_path)
    write_estimation_files(build_estimation_templates(), context)

    for prefix in ("mydata", "pars_init", "predict", "run"):
        assert _generated_file(tmp_path, prefix).is_file(), f"Missing generated {prefix} file"

    mydata = _generated_file(tmp_path, "mydata").read_text()
    assert "data.ab = 4.0;" in mydata
    assert "data.tL = [" in mydata
    assert "data.LW = [" in mydata
    # References use the AmP bibkey idiom, so they must come after txtData.bibkey is packed.
    assert mydata.index("txtData.bibkey = bibkey;") < mydata.index("bibkey = 'mock';")

    pars_init = _generated_file(tmp_path, "pars_init").read_text()
    for par in danio_estimation.FREE_PARS:
        assert f"free.{par} = 1;" in pars_init
    for par in set(danio_estimation.INITIAL_PARS) - set(danio_estimation.FREE_PARS):
        assert f"free.{par} = 0;" in pars_init


@pytest.mark.integration
@pytest.mark.slow
@pytest.mark.matlab
def test_danio_rerio_example_estimation_moves_towards_mock_parameters(tmp_path):
    pytest.importorskip("matlab.engine")

    try:
        estimated = danio_estimation.run_estimation("fast", output_folder=tmp_path)
    except RuntimeError as exc:
        pytest.fail(f"Danio rerio estimation failed: {exc}")

    assert (tmp_path / f"results_{SPECIES_NAME}.mat").is_file()
    assert set(estimated) == set(danio_estimation.FREE_PARS)
    assert all(math.isfinite(value) and value > 0 for value in estimated.values())

    def total_relative_error(pars: dict) -> float:
        return sum(abs(pars[par] / MOCK_TRUE_PARS[par] - 1) for par in danio_estimation.FREE_PARS)

    # The mock data are generated from MOCK_TRUE_PARS, so the fit should end closer to them than it started.
    assert total_relative_error(estimated) < total_relative_error(danio_estimation.INITIAL_PARS)
