"""Reusable DEB parameter definitions."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ParameterDefinition:
    name: str
    units: str
    label: str
    default_value: float | int | None = None
    default_free: int = 0
    float_format: str | None = None
    latex_label: str | None = None

# TODO: Delete this, serves no purpose since a new parameter definition will simply use ParameterDefinition
@dataclass(frozen=True)
class CustomParameterDefinition(ParameterDefinition):
    """User-defined parameter metadata."""


T_ref = ParameterDefinition("T_ref", "K", "Reference temperature", default_value=293.15)
T_A = ParameterDefinition("T_A", "K", "Arrhenius temperature", default_value=8000)
z = ParameterDefinition("z", "-", "zoom factor", default_value=13)
F_m = ParameterDefinition("F_m", "l/d.cm^2", "{F_m}, max spec searching rate", default_value=6.5)
kap_X = ParameterDefinition("kap_X", "-", "digestion efficiency of food to reserve")
kap_P = ParameterDefinition("kap_P", "-", "faecation efficiency of food to faeces")
v = ParameterDefinition("v", "cm/d", "energy conductance")
kap = ParameterDefinition("kap", "-", "allocation fraction to soma")
p_M = ParameterDefinition("p_M", "J/d.cm^3", "[p_M], vol-spec somatic maint")
p_T = ParameterDefinition("p_T", "J/d.cm^2", "{p_T}, surf-spec somatic maint", default_value=0)
k_J = ParameterDefinition("k_J", "1/d", "maturity maint rate coefficient", default_value=0.002)
E_G = ParameterDefinition("E_G", "J/cm^3", "[E_G], spec cost for structure")
E_Hb = ParameterDefinition("E_Hb", "J", "maturity at birth")
E_Hx = ParameterDefinition("E_Hx", "J", "maturity at weaning")
E_Hp = ParameterDefinition("E_Hp", "J", "maturity at puberty")
kap_R = ParameterDefinition("kap_R", "-", "reproduction efficiency", default_value=0.95)
h_a = ParameterDefinition("h_a", "1/d^2", "Weibull aging acceleration")
s_G = ParameterDefinition("s_G", "-", "Gompertz stress coefficient", default_value=0.1)
f = ParameterDefinition("f", "-", "scaled functional response for 0-var data", default_value=1)
p_Am = ParameterDefinition("p_Am", "J/d.cm^2", "Surface-specific maximum assimilation rate")
t_0 = ParameterDefinition("t_0", "d", "time at start development")
del_M = ParameterDefinition("del_M", "-", "shape coefficent")

# TODO: Add classes for parameters that often have variants, e.g., maturity levels, food levels, chemical parameters

ALL_PARAMETER_DEFINITIONS = (
    T_ref,
    T_A,
    z,
    F_m,
    kap_X,
    kap_P,
    v,
    kap,
    p_M,
    p_T,
    k_J,
    E_G,
    E_Hb,
    E_Hx,
    E_Hp,
    kap_R,
    h_a,
    s_G,
    f,
    p_Am,
    t_0,
    del_M,
)

DEFAULT_PARAMETER_DEFINITIONS = (
    T_ref,
    T_A,
    z,
    F_m,
    kap_X,
    kap_P,
    v,
    kap,
    p_M,
    p_T,
    k_J,
    E_G,
    E_Hb,
    E_Hp,
    kap_R,
    h_a,
    s_G,
    f,
)

PARAMETER_DEFINITIONS_BY_NAME = {definition.name: definition for definition in ALL_PARAMETER_DEFINITIONS}


def get_parameter_definition(name: str) -> ParameterDefinition | None:
    return PARAMETER_DEFINITIONS_BY_NAME.get(name)


def require_parameter_definition(name: str) -> ParameterDefinition:
    definition = get_parameter_definition(name)
    if definition is None:
        raise KeyError(name)
    return definition

# TODO: This implementation repeats the above variables. Perhaps a registry system would be less repetitive and error-prone
class ParameterDefinitions:
    """Catalog of reusable package-defined parameter definitions."""

    T_ref = T_ref
    T_A = T_A
    z = z
    F_m = F_m
    kap_X = kap_X
    kap_P = kap_P
    v = v
    kap = kap
    p_M = p_M
    p_T = p_T
    k_J = k_J
    E_G = E_G
    E_Hb = E_Hb
    E_Hx = E_Hx
    E_Hp = E_Hp
    kap_R = kap_R
    h_a = h_a
    s_G = s_G
    f = f
    p_Am = p_Am
    t_0 = t_0
    del_M = del_M

    @classmethod
    def all(cls) -> tuple[ParameterDefinition, ...]:
        return ALL_PARAMETER_DEFINITIONS

    @classmethod
    def default(cls) -> tuple[ParameterDefinition, ...]:
        return DEFAULT_PARAMETER_DEFINITIONS

    @classmethod
    def get(cls, name: str) -> ParameterDefinition | None:
        return get_parameter_definition(name)

    @classmethod
    def require(cls, name: str) -> ParameterDefinition:
        return require_parameter_definition(name)

__all__ = [
    "ALL_PARAMETER_DEFINITIONS",
    "DEFAULT_PARAMETER_DEFINITIONS",
    "PARAMETER_DEFINITIONS_BY_NAME",
    "CustomParameterDefinition",
    "ParameterDefinition",
    "ParameterDefinitions",
    "E_G",
    "E_Hb",
    "E_Hp",
    "E_Hx",
    "F_m",
    "T_A",
    "T_ref",
    "del_M",
    "f",
    "get_parameter_definition",
    "h_a",
    "k_J",
    "kap",
    "kap_P",
    "kap_R",
    "kap_X",
    "p_Am",
    "p_M",
    "p_T",
    "require_parameter_definition",
    "s_G",
    "t_0",
    "v",
    "z",
]
