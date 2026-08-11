"""Reusable DEB parameter definitions."""

from __future__ import annotations

from collections import OrderedDict
from dataclasses import dataclass, replace as dataclass_replace


class _UnsetType:
    """Sentinel for replace() arguments that were not provided."""


_UNSET = _UnsetType()
_BUILTIN_DEFINITIONS_BY_NAME: OrderedDict[str, "ParameterDefinition"] = OrderedDict()
_DEFAULT_DEFINITION_NAMES: list[str] = []


@dataclass(frozen=True)
class ParameterDefinition:
    name: str
    units: str
    label: str
    default_value: float | int | None = None
    default_free: int = 0
    float_format: str | None = None
    latex_label: str | None = None

    def replace(
            self,
            *,
            name: str | _UnsetType = _UNSET,
            units: str | _UnsetType = _UNSET,
            label: str | _UnsetType = _UNSET,
            default_value: float | int | None | _UnsetType = _UNSET,
            default_free: int | _UnsetType = _UNSET,
            float_format: str | None | _UnsetType = _UNSET,
            latex_label: str | None | _UnsetType = _UNSET,
    ) -> "ParameterDefinition":
        changes = {}
        if name is not _UNSET:
            changes["name"] = name
        if units is not _UNSET:
            changes["units"] = units
        if label is not _UNSET:
            changes["label"] = label
        if default_value is not _UNSET:
            changes["default_value"] = default_value
        if default_free is not _UNSET:
            changes["default_free"] = default_free
        if float_format is not _UNSET:
            changes["float_format"] = float_format
        if latex_label is not _UNSET:
            changes["latex_label"] = latex_label
        return dataclass_replace(self, **changes)


def _register_builtin(
        name: str,
        units: str,
        label: str,
        *,
        default_value: float | int | None = None,
        default_free: int = 0,
        float_format: str | None = None,
        latex_label: str | None = None,
        include_in_default: bool = False,
) -> ParameterDefinition:
    definition = ParameterDefinition(
        name=name,
        units=units,
        label=label,
        default_value=default_value,
        default_free=default_free,
        float_format=float_format,
        latex_label=latex_label,
    )
    _BUILTIN_DEFINITIONS_BY_NAME[name] = definition
    if include_in_default:
        _DEFAULT_DEFINITION_NAMES.append(name)
    return definition


T_ref = _register_builtin("T_ref", "K", "Reference temperature", default_value=293.15)
T_A = _register_builtin("T_A", "K", "Arrhenius temperature", default_value=8000, include_in_default=True)
z = _register_builtin("z", "-", "Zoom factor", default_value=13, include_in_default=True)
F_m = _register_builtin(
    "F_m",
    "l/d.cm^2",
    "Maximum specific searching rate",
    latex_label=r"\{ F_m \}",
    default_value=6.5,
    include_in_default=True,
)
kap_X = _register_builtin(
    "kap_X",
    "-",
    "Digestion efficiency",
    latex_label=r"\kappa_X",
    include_in_default=True
)
kap_P = _register_builtin(
    "kap_P",
    "-",
    "Defecation efficiency",
    latex_label=r"\kappa_P",
    include_in_default=True
)
v = _register_builtin("v", "cm/d", "Energy conductance", latex_label=r'\dot{v}', include_in_default=True)
kap = _register_builtin("kap", "-", "Allocation fraction to soma", latex_label=r"\kappa", include_in_default=True)
p_M = _register_builtin("p_M", "J/d.cm^3", "Volume-specific somatic maintenance rate", latex_label=r"[\dot{p}_M]", include_in_default=True)
p_T = _register_builtin(
    "p_T",
    "J/d.cm^2",
    "Surface-specific somatic maintenance rate",
    latex_label=r"\{ \dot{p}_T \}",
    default_value=0,
    include_in_default=True,
)
k_J = _register_builtin(
    "k_J",
    "1/d",
    "Maturity maintenance rate coefficient",
    latex_label=r"\dot{k}_J",
    default_value=0.002,
    include_in_default=True,
)
E_G = _register_builtin("E_G", "J/cm^3", "Specific cost for structure", latex_label=r"[E_G]", include_in_default=True)
E_Hb = _register_builtin("E_Hb", "J", "Maturity at birth", latex_label=r"E_H^b", include_in_default=True)
E_Hx = _register_builtin("E_Hx", "J", "Maturity at weaning", latex_label=r"E_H^x")
E_Hp = _register_builtin("E_Hp", "J", "Maturity at puberty", latex_label=r"E_H^p", include_in_default=True)
kap_R = _register_builtin(
    "kap_R",
    "-",
    "Reproduction efficiency",
    latex_label=r"\kappa_R",
    default_value=0.95,
    include_in_default=True,
)
h_a = _register_builtin("h_a", "1/d^2", "Weibull aging acceleration", latex_label=r"\ddot{h}_a", include_in_default=True)
s_G = _register_builtin(
    "s_G",
    "-",
    "Gompertz stress coefficient",
    default_value=0.1,
    include_in_default=True,
)
f = _register_builtin(
    "f",
    "-",
    "Scaled functional response",
    default_value=1,
    include_in_default=True,
)
p_Am = _register_builtin("p_Am", "J/d.cm^2", "Surface-specific maximum assimilation rate", latex_label=r"\{ \dot{p}_{Am} \}")
t_0 = _register_builtin("t_0", "d", "Time at start of development", latex_label=r"t_0")
del_M = _register_builtin("del_M", "-", "Shape coefficent", latex_label=r"\delta_M")
V_0 = _register_builtin("V_0", "cm^3", "Initial structure at fertilization", default_free=0, default_value=0)

# TODO: Add classes for parameters that often have variants, e.g., maturity levels, food levels,

ALL_PARAMETER_DEFINITIONS = tuple(_BUILTIN_DEFINITIONS_BY_NAME.values())
DEFAULT_PARAMETER_DEFINITIONS = tuple(
    _BUILTIN_DEFINITIONS_BY_NAME[name] for name in _DEFAULT_DEFINITION_NAMES
)
PARAMETER_DEFINITIONS_BY_NAME = dict(_BUILTIN_DEFINITIONS_BY_NAME)


def get_parameter_definition(name: str) -> ParameterDefinition | None:
    return PARAMETER_DEFINITIONS_BY_NAME.get(name)


def require_parameter_definition(name: str) -> ParameterDefinition:
    definition = get_parameter_definition(name)
    if definition is None:
        raise KeyError(name)
    return definition


__all__ = [
              "ALL_PARAMETER_DEFINITIONS",
              "DEFAULT_PARAMETER_DEFINITIONS",
              "PARAMETER_DEFINITIONS_BY_NAME",
              "ParameterDefinition",
              "get_parameter_definition",
              "require_parameter_definition",
          ] + list(_BUILTIN_DEFINITIONS_BY_NAME)
