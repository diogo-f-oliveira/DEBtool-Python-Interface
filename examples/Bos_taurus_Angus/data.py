from typing import Dict
from DEBtoolPyIF.data_sources.collection import DataCollection
from DEBtoolPyIF.data_sources.entity import TimeWeightEntityDataSource, DigestibilityEntityDataSource
from DEBtoolPyIF.data_sources.group import TimeFeedGroupDataSource

DATA_FOLDER = 'examples/Bos_taurus_Angus/data'


def load_data(data_folder: str = DATA_FOLDER) -> Dict[str, DataCollection]:
    """Load data collections for the example. Returns dict of DataCollection keyed by tier name."""
    bibkey = 'GreenBeefTrial1'
    comment = 'Data from GreenBeef trial 1'
    prefix = 'Pen'

    dmdds = DigestibilityEntityDataSource(
        f"{data_folder}/greenbeef_1_diet_info.csv",
        id_col='diet', dmd_col='digestibility', id_name='diet',
        bibkey=bibkey, comment=comment
    )

    twds = TimeWeightEntityDataSource(
        f"{data_folder}/greenbeef_1_weights.csv",
        id_col='sia', weight_col='weight', date_col='date',
        title='Wet weight growth curve', id_name='individual',
        bibkey=bibkey, comment=comment
    )

    gtfds = TimeFeedGroupDataSource(
        f"{data_folder}/greenbeef_1_feed_intake_pen.csv",
        id_col='pen', feed_col='dry_intake', date_col='date',
        weight_data_source=twds,
        title='Daily feed consumption',
        prefix=prefix, bibkey=bibkey, comment=comment
    )

    return {
        'breed': DataCollection(tier='breed', data_sources=[]),
        'diet': DataCollection(tier='diet', data_sources=[dmdds]),
        'individual': DataCollection(tier='individual', data_sources=[twds, gtfds]),
    }
