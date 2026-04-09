"""Validation and writing for rendered estimation files."""

from __future__ import annotations

from pathlib import Path

from .config import FILE_KEYS, EstimationTemplates


def get_output_filename(file_key: str, species_name: str) -> str:
    return f"{file_key}_{species_name}.m"


def render_estimation_file(file_key: str, template, context) -> str:
    if file_key not in FILE_KEYS:
        raise ValueError(f"Unknown estimation file key '{file_key}'.")
    template.validate(context)
    return template.render(context)


def write_estimation_file(file_key: str, template, context) -> Path:
    context.output_folder.mkdir(parents=True, exist_ok=True)
    output_path = context.output_folder / get_output_filename(file_key, context.species_name)
    output_path.write_text(render_estimation_file(file_key, template, context), encoding="utf-8")
    return output_path


def write_tier_estimation_files(
    estimation_files: EstimationTemplates,
    context,
) -> dict[str, Path]:
    return {
        file_key: write_estimation_file(file_key, template, context)
        for file_key, template in estimation_files.items()
    }
