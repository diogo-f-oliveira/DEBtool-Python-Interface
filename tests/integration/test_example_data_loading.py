import pytest

from DEBtoolPyIF.data_sources.collection import DataCollection


@pytest.mark.integration
def test_example_data_folder_contains_csv_files(example_name, examples_root):
    data_folder = examples_root / example_name / "data"
    files = [p for p in data_folder.iterdir() if p.is_file()]

    assert files, f"No files found in data folder: {data_folder}"
    assert all(p.suffix.lower() == ".csv" for p in files), f"Non-CSV files found in: {data_folder}"


@pytest.mark.integration
def test_example_load_data_returns_dict_of_data_collections(example_name, examples_root, import_example_data_module):
    data_module = import_example_data_module(example_name)
    assert hasattr(data_module, "load_data"), f"Missing load_data() in examples/{example_name}/data.py"

    data = data_module.load_data(str(examples_root / example_name / "data"))

    assert isinstance(data, dict)
    assert data, f"load_data() returned empty dict for example {example_name}"
    assert all(isinstance(k, str) for k in data.keys())
    assert all(isinstance(v, DataCollection) for v in data.values())
