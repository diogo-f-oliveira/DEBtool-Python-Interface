"""Estimation templates for the Danio_rerio single-species example.

``mydata``, ``pars_init`` and ``run`` are assembled in Python from the generic (non-multitier) template classes.
``predict`` is copied verbatim, since it remains the most workflow-specific species file.
"""

from pathlib import Path

from DEBtoolPyIF import CopyFileTemplate, EstimationTemplates, MyDataProgrammaticTemplate, NelderMead
from DEBtoolPyIF.estimation_files import RegistryParsInitProgrammaticTemplate
from DEBtoolPyIF.estimation_files.mydata_data_sections import EntityDataSection, GroupDataSection
from DEBtoolPyIF.estimation_files.mydata_metadata_sections import (
    AuthorInfoMetadataSection,
    BibkeysSection,
    CompletenessLevelSection,
    DiscussionSection,
    MyDataFunctionHeader,
    SaveFieldsSection,
    SpeciesInfoMetadataSection,
)
from DEBtoolPyIF.estimation_files.mydata_packing_sections import PackingSection
from DEBtoolPyIF.estimation_files.mydata_pseudodata_sections import AddPseudoDataSection
from DEBtoolPyIF.estimation_files.mydata_temperature_sections import TypicalTemperatureSection
from DEBtoolPyIF.estimation_files.mydata_weight_sections import InitializeWeightsSection, RemoveDummyWeightsSection
from DEBtoolPyIF.parameters import StdParameterRegistry, del_M

from examples.Danio_rerio.data import MOCK_BIBKEY, SpeciesDataSection, load_mock_datasets

EXAMPLE_FOLDER = Path(__file__).resolve().parent
SPECIES_NAME = "Danio_rerio"

# References use the usual AmP idiom. BibkeysSection renders after PackingSection, as in DEBtool's mydata_my_pet.m,
# so reassigning ``bibkey`` here does not overwrite the per-dataset bibkey struct.
MOCK_BIBLIST = f"""%% References
bibkey = '{MOCK_BIBKEY}'; type = 'Misc'; bib = [ ...
'author = {{DEBtoolPyIF}}, ' ...
'year = {{2026}}, ' ...
'title = {{Mock data for the Danio rerio example}}, ' ...
'note = {{Generated values, not observations}}'];
metaData.biblist.(bibkey) = ['@', type, '{{', bibkey, ', ' bib, '}}'];"""


def build_parameter_registry():
    """The std model registry plus the shape coefficient used by the length data."""
    return StdParameterRegistry().merged([del_M])


def create_mydata_template(datasets=None) -> MyDataProgrammaticTemplate:
    datasets = load_mock_datasets() if datasets is None else datasets
    return MyDataProgrammaticTemplate(
        sections=(
            MyDataFunctionHeader(),
            SpeciesInfoMetadataSection(
                phylum="Chordata",
                class_name="Actinopterygii",
                order_name="Cypriniformes",
                family="Danionidae",
                species="Danio rerio",
                species_en="Zebrafish",
            ),
            AuthorInfoMetadataSection(author="DEBtoolPyIF example", email="", address=""),
            TypicalTemperatureSection(t_typical=28.5, is_celsius=True),
            CompletenessLevelSection(complete=2.5),
            # Multitier data blocks are part of the required mydata contract; they render empty here.
            GroupDataSection(),
            EntityDataSection(),
            SpeciesDataSection(datasets),
            InitializeWeightsSection(),
            SaveFieldsSection(),
            RemoveDummyWeightsSection(),
            AddPseudoDataSection(),
            PackingSection(),
            DiscussionSection(discussion_points={"D1": "All data are mock values generated from the std model."}),
            BibkeysSection(bibkeys_content=MOCK_BIBLIST),
        )
    )


def build_estimation_templates(datasets=None) -> EstimationTemplates:
    return EstimationTemplates(
        mydata=create_mydata_template(datasets),
        pars_init=RegistryParsInitProgrammaticTemplate(
            parameter_registry=build_parameter_registry(),
            model="std",
        ),
        predict=CopyFileTemplate(EXAMPLE_FOLDER / f"predict_{SPECIES_NAME}.m"),
        # Unset NelderMead settings are read from SpeciesGenerationContext.estimation_settings at render time.
        run=NelderMead(simplex_size=0.1),
    )
