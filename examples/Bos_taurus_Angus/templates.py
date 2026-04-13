from pathlib import Path

from DEBtoolPyIF import EstimationTemplates, MultitierMyDataSubstitutionTemplate, MultitierParsInitSubstitutionTemplate, \
    CopyFileTemplate, RunSubstitutionTemplate
from DEBtoolPyIF.estimation_files.mydata_metadata_sections import SaveDataFieldsByVariateTypeSection, \
    MyDataFunctionHeaderSection, SpeciesInfoMetadataSection, AuthorInfoMetadataSection, SaveFieldsSection, \
    CompletenessLevelSection
from DEBtoolPyIF.estimation_files.mydata_pseudodata_sections import AddPseudoDataSection
from DEBtoolPyIF.estimation_files.mydata_temperature_sections import SetTypicalTemperatureForAllDatasetsSection, \
    TypicalTemperatureSection
from DEBtoolPyIF.estimation_files.mydata_weight_sections import InitializeWeightsSection, RemoveDummyWeightsSection
from DEBtoolPyIF.multitier.mydata_sections import MultitierPseudoDataSection, MultitierPackingSection
from DEBtoolPyIF.estimation_files.algorithms import NelderMead


def create_mydata_template(source_folder, species_name):
    return MultitierMyDataSubstitutionTemplate(
        source=source_folder / f"mydata_{species_name}.m",
        sections=(
            MyDataFunctionHeaderSection(species_name=species_name),
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

            pars_init=MultitierParsInitSubstitutionTemplate(
                source=base_template_folder / tier / f'pars_init_{species_name}.m',
            ),

            predict=CopyFileTemplate(base_template_folder / tier / f'predict_{species_name}.m'),

            run=NelderMead(),
        )

    return templates
