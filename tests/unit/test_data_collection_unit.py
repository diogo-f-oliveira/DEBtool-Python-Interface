from pathlib import Path

import pandas as pd
import pytest

from DEBtoolPyIF.data_sources.collection import DataCollection
from DEBtoolPyIF.data_sources.base import EntityDataSourceBase, GroupDataSourceBase


class FakeEntitySource(EntityDataSourceBase):
    def __init__(self, name, TYPE, entities, data_map):
        # Do not call super; set minimal attrs expected by DataCollection
        self.name = name
        self.TYPE = TYPE
        self.entities = set(entities)
        # data_map: dict entity_id -> pd.DataFrame
        self._data_map = {str(k): v for k, v in data_map.items()}

    def get_entity_data(self, entity_id):
        # Return DataFrame for the entity or raise as real impl would
        entity_id = str(entity_id)
        if entity_id not in self.entities:
            raise Exception(f'Invalid entity ID. Entity {entity_id} not found in the dataset.')
        return self._data_map.get(entity_id, pd.DataFrame())


class FakeGroupSource(GroupDataSourceBase):
    def __init__(self, name, TYPE, groups, entity_to_group_map, data_map):
        # groups: iterable of group ids
        # entity_to_group_map: dict entity_id -> group_id
        # data_map: dict group_id -> DataFrame
        self.name = name
        self.TYPE = TYPE
        self.groups = set(groups)
        # Build entity_vs_group_df with True where mapping exists
        evg = pd.DataFrame(index=sorted(set(entity_to_group_map.keys())), columns=sorted(self.groups))
        for e, g in entity_to_group_map.items():
            evg.loc[str(e), str(g)] = True
        self.entity_vs_group_df = evg
        self._data_map = {str(k): v for k, v in data_map.items()}

    def get_group_data(self, group_id):
        gid = str(group_id)
        if gid not in self.groups:
            raise Exception(f'Invalid Group ID. Group {gid} not found in the dataset.')
        return self._data_map.get(gid, pd.DataFrame())


# Small helper to make DataFrames inline
def df(rows):
    return pd.DataFrame(rows)


@pytest.fixture
def sample_datacollection():
    # Build a reusable DataCollection used by several tests
    # Entities and groups use lowercase ids; TYPE is uppercase. Data source names use <TYPE>_<number>.
    e1_entities = ['a', 'b']
    e2_entities = ['b', 'c']
    e1_data = {'a': df([{'x': 1}]), 'b': df([{'x': 2}])}
    e2_data = {'b': df([{'y': 10}]), 'c': df([{'y': 20}])}

    # Two entity sources of TYPE T1 named T1_1 and T1_2
    e1 = FakeEntitySource(name='T1_1', TYPE='T1', entities=e1_entities, data_map=e1_data)
    e2 = FakeEntitySource(name='T1_2', TYPE='T1', entities=e2_entities, data_map=e2_data)

    # Groups are lowercase ids
    groups = ['g1', 'g2']
    entity_to_group = {'a': 'g1', 'b': 'g1', 'c': 'g2'}
    g_data = {'g1': df([{'g': 100}]), 'g2': df([{'g': 200}])}
    # Group data source of TYPE GT named GT_1
    g1 = FakeGroupSource(name='GT_1', TYPE='GT', groups=groups, entity_to_group_map=entity_to_group, data_map=g_data)

    return DataCollection(tier='test', data_sources=[e1, g1, e2])


def test_add_data_sources_and_mappings(sample_datacollection):
    dc = sample_datacollection

    # Entities should be union of e1 and e2 (lowercase)
    assert sorted(dc.entities) == ['a', 'b', 'c']
    # Groups should match group source (lowercase)
    assert sorted(dc.groups) == ['g1', 'g2']

    # Data types (uppercase)
    assert 'T1' in dc.entity_data_types
    assert 'GT' in dc.group_data_types

    # entity_vs_data_source_df must have True for (b,T1_1) and (b,T1_2)
    assert bool(dc.entity_vs_data_source_df.loc['b', 'T1_1'])
    assert bool(dc.entity_vs_data_source_df.loc['b', 'T1_2'])

    # group_vs_data_source_df must have True for (g1,GT_1)
    assert bool(dc.group_vs_data_source_df.loc['g1', 'GT_1'])

    # entity_vs_group_df should indicate group membership
    assert bool(dc.entity_vs_group_df.loc['a', 'g1'])
    assert bool(dc.entity_vs_group_df.loc['c', 'g2'])

    # get_entity_list_of_group
    assert dc.get_entity_list_of_group('g1') == ['a', 'b']

    # get_groups_of_entities
    got = dc.get_groups_of_entities(['a', 'c'])
    assert 'a' in got and got['a'] == ['g1']
    assert 'c' in got and got['c'] == ['g2']

    # get_group_list_from_entity_list (subset)
    assert dc.get_group_list_from_entity_list(['b']) == ['g1']


def test_get_entity_data_concat_and_none():
    # Use lowercase entity id 'x' and data sources named T1_1/T1_2
    e1_entities = ['x']
    e2_entities = ['x']
    e1_data = {'x': df([{'a': 1}])}
    e2_data = {'x': df([{'a': 2}])}
    e1 = FakeEntitySource(name='T1_1', TYPE='T1', entities=e1_entities, data_map=e1_data)
    e2 = FakeEntitySource(name='T1_2', TYPE='T1', entities=e2_entities, data_map=e2_data)

    dc = DataCollection(tier='t', data_sources=[e1, e2])

    # get_data_source_of_entity
    sources = dc.get_data_source_of_entity('x', 'T1')
    assert set(sources) == {'T1_1', 'T1_2'}

    # get_entity_data should concatenate two dataframes (result length 2)
    out = dc.get_entity_data('x', 'T1')
    assert len(out) == 2

    # request non-existent entity/data raises KeyError (pandas indexing) in current impl
    with pytest.raises(KeyError):
        dc.get_entity_data('nope', 'T1')
    with pytest.raises(KeyError):
        dc.get_entity_data('x', 'UNKNOWN_TYPE')


def test_get_group_data_concat_and_none():
    # two group sources with same TYPE, group id lowercased 'g'
    g1 = FakeGroupSource(name='GT_1', TYPE='GT', groups=['g'], entity_to_group_map={'e': 'g'}, data_map={'g': df([{'v': 1}])})
    g2 = FakeGroupSource(name='GT_2', TYPE='GT', groups=['g'], entity_to_group_map={'e': 'g'}, data_map={'g': df([{'v': 2}])})

    dc = DataCollection(tier='t', data_sources=[g1, g2])

    sources = dc.get_data_source_of_group('g', 'GT')
    assert set(sources) == {'GT_1', 'GT_2'}

    out = dc.get_group_data('g', 'GT')
    assert len(out) == 2

    with pytest.raises(KeyError):
        dc.get_group_data('nope', 'GT')
    with pytest.raises(KeyError):
        dc.get_group_data('g', 'UNKNOWN')
