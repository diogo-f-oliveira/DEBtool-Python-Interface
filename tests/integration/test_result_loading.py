import pytest


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
    for tier in multitier.tiers.values():
        tier.result_metadata = None
        tier.estimation_settings = None
        tier.estim_start_time = None
        tier.estim_end_time = None
        tier.estimation_iterations = []

    loaded_results = estimation_module.load_estimation_results(multitier)

    assert set(loaded_results) == set(multitier.tier_names)
    for tier_name in multitier.tier_names:
        tier = multitier.tiers[tier_name]
        tier_summary = loaded_results[tier_name]
        assert tier_summary["result_metadata"] is not None
        assert tier_summary["estimation_settings"] == tier.estimation_settings
        assert tier_summary["estimation_start_time"] == tier.estim_start_time
        assert tier_summary["estimation_end_time"] == tier.estim_end_time
        assert tier_summary["elapsed_duration_seconds"] == tier.result_metadata["elapsed_duration_seconds"]
        assert tier_summary["estimation_iterations"] == tier.estimation_iterations
        assert tier.estim_start_time is not None
        assert tier.estim_end_time is not None
        assert tier.estimation_iterations
