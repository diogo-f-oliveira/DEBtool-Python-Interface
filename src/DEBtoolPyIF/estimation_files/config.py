"""Configuration containers and normalization for estimation_files."""

from __future__ import annotations

from dataclasses import dataclass

from .templates import CopyFileTemplate, EstimationFileTemplate


FILE_KEYS = ("mydata", "pars_init", "predict", "run")


def _coerce_template(template: EstimationFileTemplate | str) -> EstimationFileTemplate:
    if isinstance(template, EstimationFileTemplate):
        return template
    if isinstance(template, str):
        if template.endswith(".m"):
            return CopyFileTemplate(template)
        raise TypeError(
            "Estimation template strings must be MATLAB '.m' file paths to copy verbatim."
        )
    raise TypeError(
        "Estimation templates must be EstimationFileTemplate instances or MATLAB '.m' path strings."
    )


@dataclass(frozen=True)
class EstimationTemplates:
    """The four species-file templates used to render one estimation target."""

    mydata: EstimationFileTemplate
    pars_init: EstimationFileTemplate
    predict: EstimationFileTemplate
    run: EstimationFileTemplate

    @classmethod
    def from_mapping(
        cls,
        mapping: dict[str, EstimationFileTemplate | str] | "EstimationTemplates",
    ) -> "EstimationTemplates":
        if isinstance(mapping, cls):
            return mapping
        if not isinstance(mapping, dict):
            raise TypeError(
                "Estimation templates must be provided as an EstimationFiles instance or a mapping."
            )

        unknown_keys = sorted(set(mapping) - set(FILE_KEYS))
        if unknown_keys:
            raise ValueError(
                f"Unknown estimation template keys: {', '.join(unknown_keys)}. "
                f"Expected only: {', '.join(FILE_KEYS)}."
            )

        missing_keys = [file_key for file_key in FILE_KEYS if file_key not in mapping]
        if missing_keys:
            raise ValueError(
                f"Missing estimation template keys: {', '.join(missing_keys)}."
            )

        return cls(**{file_key: _coerce_template(mapping[file_key]) for file_key in FILE_KEYS})

    def items(self):
        for file_key in FILE_KEYS:
            yield file_key, getattr(self, file_key)


def normalize_estimation_templates(
    estimation_templates: dict[str, EstimationTemplates | dict[str, EstimationFileTemplate | str]],
    tier_names: list[str] | tuple[str, ...],
) -> dict[str, EstimationTemplates]:
    if not isinstance(estimation_templates, dict):
        raise TypeError("estimation_templates must be a dict keyed by tier name.")

    tier_names = list(tier_names)
    extra_tiers = sorted(set(estimation_templates) - set(tier_names))
    if extra_tiers:
        raise ValueError(
            f"Unknown tiers in estimation_templates: {', '.join(extra_tiers)}."
        )

    missing_tiers = [tier_name for tier_name in tier_names if tier_name not in estimation_templates]
    if missing_tiers:
        raise ValueError(
            f"Missing tiers in estimation_templates: {', '.join(missing_tiers)}."
        )

    return {
        tier_name: EstimationTemplates.from_mapping(estimation_templates[tier_name])
        for tier_name in tier_names
    }
