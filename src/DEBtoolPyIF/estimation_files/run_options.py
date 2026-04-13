"""Typed helpers for rendering DEBtool ``estim_options`` calls."""

from __future__ import annotations

from numbers import Real

import numpy as np

from .run_sections import RunSection
from ..utils.data_conversion import convert_numeric_array_to_matlab, convert_string_to_matlab
from ..utils.mydata_code_generation import is_valid_matlab_field_name

_MISSING_OPTION_VALUE = object()


class RunSetting:
    """Reference a render-time value from ``context.estimation_settings``."""

    def __init__(self, key: str) -> None:
        if not isinstance(key, str) or not key:
            raise ValueError("RunSetting requires a non-empty string key.")
        self.key = key


def resolve_run_value(value, context):
    if not isinstance(value, RunSetting):
        return value
    return resolve_run_setting(context, value.key)


def resolve_run_setting(context, key: str):
    settings = getattr(context, "estimation_settings", {}) or {}
    if key not in settings:
        raise ValueError(
            f"Missing run setting '{key}' required by render_key='{key}'. "
            "Provide it in context.estimation_settings."
        )
    return settings[key]


class EstimOption:
    """Render one typed DEBtool ``estim_options`` call.

    A construction-time value is rendered literally. A ``RunSetting`` value, or
    the convenience ``render_key=...`` argument, is resolved from
    ``context.estimation_settings`` before type-specific validation.
    """

    argument_name: str = ""

    def __init__(
        self,
        value=_MISSING_OPTION_VALUE,
        *,
        argument_name: str | None = None,
        render_key: str | None = None,
        create_variable: bool = False,
        create_global_variable: bool = False,
    ) -> None:
        self.argument_name = self._resolve_argument_name(argument_name)
        if value is not _MISSING_OPTION_VALUE and render_key is not None:
            raise ValueError("Set either a construction-time value or render_key, not both.")
        if value is _MISSING_OPTION_VALUE:
            self.value = RunSetting(render_key if render_key is not None else self.argument_name)
        else:
            self.value = value
        self.render_key = self.value.key if isinstance(self.value, RunSetting) else None
        self.create_variable = create_variable
        self.create_global_variable = create_global_variable
        if self.create_variable or self.create_global_variable:
            self._validate_variable_name()

    def _resolve_argument_name(self, argument_name: str | None) -> str:
        resolved_argument_name = argument_name if argument_name is not None else self.argument_name
        if not isinstance(resolved_argument_name, str) or not resolved_argument_name:
            raise ValueError("EstimOption requires a non-empty argument_name.")
        return resolved_argument_name

    def _validate_variable_name(self) -> None:
        if not is_valid_matlab_field_name(self.argument_name):
            raise ValueError(
                f"Cannot create MATLAB variable for estim option '{self.argument_name}' because "
                "the argument name is not a valid MATLAB identifier."
            )

    def resolve_value(self, context):
        return resolve_run_value(self.value, context)

    def validate_value(self, _value) -> None:
        return None

    def render_value(self, _value) -> str:
        raise NotImplementedError

    def render(self, context) -> str:
        value = self.resolve_value(context)
        self.validate_value(value)
        rendered_value = self.render_value(value)
        if self.create_variable or self.create_global_variable:
            lines = []
            if self.create_global_variable:
                lines.append(f"global {self.argument_name}")
            lines.append(f"{self.argument_name} = {rendered_value};")
            lines.append(f"estim_options('{self.argument_name}', {self.argument_name});")
            return "\n".join(lines)
        return f"estim_options('{self.argument_name}', {rendered_value});"


class NumericEstimOption(EstimOption):
    """Typed numeric ``estim_options`` argument."""

    positive: bool = False
    allowed_values: tuple[int | float, ...] | None = None

    def validate_value(self, value) -> None:
        if not isinstance(value, Real) or isinstance(value, bool):
            raise TypeError(
                f"estim_options('{self.argument_name}') expects a numeric value, "
                f"not {type(value).__name__}."
            )
        if self.positive and value <= 0:
            raise ValueError(
                f"estim_options('{self.argument_name}') expects a positive numeric value, got {value!r}."
            )
        if self.allowed_values is not None and value not in self.allowed_values:
            allowed = ", ".join(str(allowed_value) for allowed_value in self.allowed_values)
            raise ValueError(
                f"estim_options('{self.argument_name}') expected one of {allowed}, got {value!r}."
            )

    def render_value(self, value) -> str:
        return convert_numeric_array_to_matlab(value)


class IntegerEstimOption(NumericEstimOption):
    """Typed integer ``estim_options`` argument."""

    def validate_value(self, value) -> None:
        if not isinstance(value, (int, np.integer)) or isinstance(value, (bool, np.bool_)):
            raise TypeError(
                f"estim_options('{self.argument_name}') expects an integer value, "
                f"not {type(value).__name__}."
            )
        super().validate_value(value)


class StringEstimOption(EstimOption):
    """Typed string ``estim_options`` argument."""

    allowed_values: tuple[str, ...] | None = None

    def validate_value(self, value) -> None:
        if not isinstance(value, str):
            raise TypeError(
                f"estim_options('{self.argument_name}') expects a string value, "
                f"not {type(value).__name__}."
            )
        if self.allowed_values is not None and value not in self.allowed_values:
            allowed = ", ".join(repr(allowed_value) for allowed_value in self.allowed_values)
            raise ValueError(
                f"estim_options('{self.argument_name}') expected one of {allowed}, got {value!r}."
            )

    def render_value(self, value) -> str:
        return convert_string_to_matlab(value)


class SetMaxStepNumberOption(IntegerEstimOption):
    argument_name = "max_step_number"
    positive = True


class SetMaxFunEvalsOption(IntegerEstimOption):
    argument_name = "max_fun_evals"
    positive = True


class SetSimplexSizeOption(NumericEstimOption):
    argument_name = "simplex_size"
    positive = True


class SetFilterOption(IntegerEstimOption):
    argument_name = "filter"
    allowed_values = (0, 1)


class SetTolSimplexOption(NumericEstimOption):
    argument_name = "tol_simplex"
    positive = True


class SetParsInitMethodOption(IntegerEstimOption):
    argument_name = "pars_init_method"
    allowed_values = (0, 1, 2, 3)


class SetResultsOutputOption(IntegerEstimOption):
    argument_name = "results_output"
    allowed_values = (-5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6)


class SetMethodOption(StringEstimOption):
    argument_name = "method"
    allowed_values = ("nm", "mmea", "no",)


class SetDefaultEstimOptions(RunSection):
    key = "set_default_options"
    template_families = ("run",)
    section_tags = ("options",)
    matlab_code = "estim_options('default');"


class SetEstimOptionsSection(RunSection):
    """Render initialization and ordered ``estim_options(...)`` calls."""

    key = "set_options"
    template_families = ("run",)
    section_tags = ("options",)

    def __init__(
        self,
        *,
        options: tuple[EstimOption, ...] | None = None,
        initialize: bool = True,
    ) -> None:
        self.options = () if options is None else tuple(options)
        self.initialize = True if not self.options else initialize
        self._validate_options()
        super().__init__()

    @classmethod
    def default_options(cls) -> tuple[EstimOption, ...]:
        return ()

    def _validate_options(self) -> None:
        for option in self.options:
            if not isinstance(option, EstimOption):
                raise TypeError(
                    "SetEstimOptionsSection options must be EstimOption instances, "
                    f"not {type(option).__name__}."
                )

    def render(self, context) -> str:
        lines = [SetDefaultEstimOptions().render(context)] if self.initialize else []
        for option in self.options:
            lines.append(option.render(context))
        return "\n".join(lines)


__all__ = [
    "RunSetting",
    "resolve_run_value",
    "resolve_run_setting",
    "EstimOption",
    "NumericEstimOption",
    "IntegerEstimOption",
    "StringEstimOption",
    "SetMaxStepNumberOption",
    "SetMaxFunEvalsOption",
    "SetSimplexSizeOption",
    "SetFilterOption",
    "SetTolSimplexOption",
    "SetParsInitMethodOption",
    "SetResultsOutputOption",
    "SetMethodOption",
    "SetDefaultEstimOptions",
    "SetEstimOptionsSection",
]
