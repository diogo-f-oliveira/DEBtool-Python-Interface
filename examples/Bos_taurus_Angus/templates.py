from pathlib import Path

from DEBtoolPyIF import (
    CopyFileTemplate,
    EstimationTemplates,
    MultitierMyDataSubstitutionTemplate,
    ParameterDefinition,
    ParameterDefinitions,
    ParameterRegistry,
    RegistryMultitierParsInitProgrammaticTemplate,
)
from DEBtoolPyIF.estimation_files.mydata_metadata_sections import SaveDataFieldsByVariateTypeSection, \
    MyDataFunctionHeader, SpeciesInfoMetadataSection, AuthorInfoMetadataSection, SaveFieldsSection, \
    CompletenessLevelSection
from DEBtoolPyIF.estimation_files.mydata_pseudodata_sections import AddPseudoDataSection
from DEBtoolPyIF.estimation_files.mydata_temperature_sections import SetTypicalTemperatureForAllDatasetsSection, \
    TypicalTemperatureSection
from DEBtoolPyIF.estimation_files.mydata_weight_sections import InitializeWeightsSection, RemoveDummyWeightsSection
from DEBtoolPyIF.multitier.mydata_sections import MultitierPseudoDataSection, MultitierPackingSection
from DEBtoolPyIF.estimation_files.algorithms import RestartingNelderMead


def build_angus_parameter_registry():
    parameter_registry = ParameterRegistry.default()
    for definition in (
            ParameterDefinitions.p_Am,
            ParameterDefinitions.t_0,
            ParameterDefinitions.E_Hx,
            ParameterDefinitions.del_M,
    ):
        parameter_registry.add(definition)
    parameter_registry.add(
        ParameterDefinition(
            "p_Am_f",
            "J/d.cm^2",
            "Surface-specific maximum assimilation rate for females",
        )
    )
    parameter_registry.add(ParameterDefinition("E_Hp_f", "J", "maturity at puberty for females"))
    return parameter_registry


def create_mydata_template(source_folder, species_name):
    return MultitierMyDataSubstitutionTemplate(
        source=source_folder / f"mydata_{species_name}.m",
        sections=(
            MyDataFunctionHeader(species_name=species_name),
            SpeciesInfoMetadataSection(
                phylum='Chordata',
                class_name='Mammalia',
                order_name='Artiodactyla',
                family='Bovidae',
                species='Bos taurus Angus',
                species_en='Angus cattle',
            ),
            AuthorInfoMetadataSection(
                author=['Diogo F. Oliveira', 'Goncalo M. Marques'],
                email='diogo.miguel.oliveira@tecnico.ulisboa.pt',
                address='Instituto Superior Tecnico, Universidade de Lisboa, Portugal',
            ),
            TypicalTemperatureSection(t_typical=38.6, is_celsius=True),
            CompletenessLevelSection(complete=3),
            # Data loading sections
            *MultitierMyDataSubstitutionTemplate.data_sections(),
            # Multitier variables sections
            *MultitierMyDataSubstitutionTemplate.tier_variable_sections(),
            InitializeWeightsSection(),
            SaveFieldsSection(),
            SaveDataFieldsByVariateTypeSection(),
            SetTypicalTemperatureForAllDatasetsSection(),
            RemoveDummyWeightsSection(),
            AddPseudoDataSection(),
            MultitierPseudoDataSection(),
            MultitierPackingSection()
        )
    )


def build_estimation_templates(
        base_template_folder: str | Path,
        tier_names: list[str],
        species_name: str) -> dict[
    str, EstimationTemplates]:
    """Create the template files for the example."""

    templates = {}
    for tier in tier_names:
        templates[tier] = EstimationTemplates(
            mydata=create_mydata_template(
                source_folder=base_template_folder / tier,
                species_name=species_name,
            ),

            pars_init=RegistryMultitierParsInitProgrammaticTemplate(
                parameter_registry=build_angus_parameter_registry(),
            ),

            predict=CopyFileTemplate(base_template_folder / tier / f'predict_{species_name}.m'),

            run=RestartingNelderMead(
                simplex_size=0.25,
            ),
        )

    return templates
