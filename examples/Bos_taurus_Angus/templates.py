from pathlib import Path

from DEBtoolPyIF import (
    CopyFileTemplate,
    EstimationTemplates,
    MultitierMyDataSubstitutionTemplate,
    RegistryMultitierParsInitProgrammaticTemplate,
    get_parameter_registry_of_typified_model,
)
from DEBtoolPyIF.parameters import E_Hp, del_M, p_Am
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
    parameter_registry = get_parameter_registry_of_typified_model("stx")
    for definition in (
            p_Am,
            del_M,
    ):
        parameter_registry.add(definition)
    parameter_registry.add(
        p_Am.replace(
            name="p_Am_f",
            label="Surface-specific maximum assimilation rate for females",
        )
    )
    parameter_registry.add(
        E_Hp.replace(
            name="E_Hp_f",
            label="maturity at puberty for females",
        )
    )
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
