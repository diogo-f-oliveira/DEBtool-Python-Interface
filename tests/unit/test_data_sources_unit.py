from pathlib import Path

import pytest

from DEBtoolPyIF.data_sources.base import DataSourceBase


class ExampleDataSource(DataSourceBase):
    TYPE = "example"


def create_csv(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("entity,value\nentity_1,1\n", encoding="utf-8")


@pytest.mark.parametrize("use_string", [True, False])
def test_csv_filename_is_stored_as_path(tmp_path, use_string):
    csv_path = tmp_path / "measurements.csv"
    create_csv(csv_path)
    csv_filename = str(csv_path) if use_string else csv_path

    data_source = ExampleDataSource(csv_filename, "entity", "value", "kg")

    assert data_source.csv_filename == csv_path
    assert isinstance(data_source.csv_filename, Path)


def test_default_name_uses_csv_path_stem(tmp_path):
    csv_path = tmp_path / "nested" / "animal.measurements.csv"
    create_csv(csv_path)

    data_source = ExampleDataSource(csv_path, "entity", "value", "kg")

    assert data_source.name == "animal.measurements_example"


def test_explicit_name_overrides_default_name(tmp_path):
    csv_path = tmp_path / "measurements.csv"
    create_csv(csv_path)

    data_source = ExampleDataSource(csv_path, "entity", "value", "kg", name="custom_name")

    assert data_source.name == "custom_name"
