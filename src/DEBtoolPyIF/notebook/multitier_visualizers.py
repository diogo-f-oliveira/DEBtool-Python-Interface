import matplotlib.pyplot as plt
import ipywidgets as widgets
import numpy as np
from IPython.display import display, clear_output

from ..multitier import MultiTierStructure
from ..data_sources.collection import DataCollection


class TierVisualizer:
    MAX_SUBPLOT_COLS = 5
    SUBPLOT_SIZE = 4

    def __init__(self, tier_structure: MultiTierStructure, plotting_functions: dict):
        self.tier_structure = tier_structure
        self.tier_entity_selectors = {}
        self.tier_group_selectors = {}
        data_types = []
        for tier_name, tier in self.tier_structure.tiers.items():
            self.tier_entity_selectors[tier_name] = widgets.SelectMultiple(
                options=tier.tier_entities,
                value=tier.tier_entities,
                description=f'{tier_name} entity:'
            )
            self.tier_group_selectors[tier_name] = widgets.SelectMultiple(
                options=tier.tier_groups,
                value=tier.tier_groups,
                description=f'{tier_name} group:'
            )
            data_types.extend([f"{tier_name} {dt}" for dt in tier.data.data_types])

        self.data_type_selector = widgets.Dropdown(
            options=data_types,
            value=data_types[1],
            description='Data:'
        )

        # TODO: Add argument for plotting function arguments
        self.plotting_functions = plotting_functions
        self.output_widget = widgets.Output()  # Output widget to capture and display plots

    def create_figure(self, n_subplots):
        n_cols = self.MAX_SUBPLOT_COLS if n_subplots > 5 else n_subplots
        n_rows = n_subplots // n_cols + (n_subplots % n_cols > 0)
        fig, axes = plt.subplots(nrows=n_rows, ncols=n_cols,
                                 figsize=(self.SUBPLOT_SIZE * n_cols, self.SUBPLOT_SIZE * n_rows),
                                 tight_layout=True)
        # Hide unused axes
        for j in range(n_subplots, n_rows * n_cols):
            axes.flat[j].axis('off')

        return fig, axes

    def plot_predictions_of_entity_list(self, axes, plotting_function, pars_entity_list,
                                        data_collection: DataCollection,
                                        data_type: str, pars_tier: str, data_tier: str):
        flat_axes = np.atleast_1d(axes).ravel()
        ax_idx = 0
        for p_id in pars_entity_list:
            pars = self.tier_structure.get_full_pars_dict(tier_name=pars_tier, entity_id=p_id, include_tier=True)
            data_entity_list = self.tier_structure.entity_hierarchy.map_entities(
                source_tier=pars_tier, target_tier=data_tier, entity_list=[p_id]
            )

            for d_id in data_entity_list:
                data_source_name = data_collection.get_data_source_of_entity(entity_id=d_id, data_type=data_type)[0]
                data_source = data_collection.data_sources[data_source_name]
                plotting_function(ax=flat_axes[ax_idx],
                                  data_source=data_source,
                                  data_tier=data_tier,
                                  data_entity_id=d_id,
                                  pars=pars,
                                  pars_tier=pars_tier,
                                  pars_entity_id=p_id,
                                  tier_structure=self.tier_structure,
                                  )
                ax_idx += 1

    def plot_predictions_of_group_list(self, axes, plotting_function, group_list, data_collection: DataCollection,
                                       data_type: str, pars_tier: str, data_tier: str):
        flat_axes = np.atleast_1d(axes).ravel()
        ax_idx = 0
        for g_id in group_list:
            # Get data source of group id
            data_source_name = data_collection.get_data_source_of_group(group_id=g_id, data_type=data_type)[0]
            data_source = data_collection.data_sources[data_source_name]
            # Get full parameter dict of pars_tier based on group id
            data_entity_list = data_collection.get_entity_list_of_group(group_id=g_id)
            data_entity_pars_dict = {}
            pars_entity_list = []
            for d_id in data_entity_list:
                pars_entity_of_data_entity = self.tier_structure.entity_hierarchy.map_entities(
                    source_tier=data_tier, target_tier=pars_tier, entity_list=[d_id]
                )[0]
                pars_dict = self.tier_structure.get_full_pars_dict(tier_name=pars_tier,
                                                                   entity_id=pars_entity_of_data_entity,
                                                                   include_tier=True)
                pars_entity_list.append(pars_entity_of_data_entity)
                data_entity_pars_dict[d_id] = pars_dict
            plotting_function(ax=flat_axes[ax_idx],
                              data_source=data_source,
                              data_tier=data_tier,
                              data_group_id=g_id,
                              data_entity_pars_dict=data_entity_pars_dict,
                              pars_tier=pars_tier,
                              pars_entity_list=pars_entity_list,
                              tier_structure=self.tier_structure,
                              )
            ax_idx += 1

    def plot_tier_data_and_predictions(self, tier_name):
        def display_data_and_predictions(selected_entity_list, tier_and_data_type):
            with self.output_widget:  # Use the output widget as the context for plot display
                clear_output()  # Clear the previous plots
                data_tier, data_type = tier_and_data_type.split()
                data_collection = self.tier_structure.data[data_tier]

                # ind_list = self.tier_structure.ind_list_from_tier_sample_list(tier_name, tier_entity_list)
                if data_type in data_collection.entity_data_types:

                    # Create subplots
                    if self.tier_structure.entity_hierarchy.is_tier_below(tier_name=tier_name, other_tier=data_tier):
                        n_subplots = len(self.tier_structure.entity_hierarchy.map_entities(
                            source_tier=tier_name, target_tier=data_tier, entity_list=selected_entity_list
                        ))
                    else:
                        n_subplots = len(selected_entity_list)
                    fig, axes = self.create_figure(n_subplots=n_subplots)

                    self.plot_predictions_of_entity_list(
                        axes=axes,
                        plotting_function=self.plotting_functions[data_tier][data_type],
                        pars_entity_list=selected_entity_list,
                        data_collection=data_collection,
                        data_type=data_type,
                        pars_tier=tier_name,
                        data_tier=data_tier
                    )

                    # TODO: axis labels should only be displayed on the outer axes
                elif data_type in data_collection.group_data_types:
                    if tier_name == data_tier:
                        data_entity_list = list(selected_entity_list)
                    elif self.tier_structure.entity_hierarchy.is_tier_below(tier_name=tier_name, other_tier=data_tier):
                        data_entity_list = self.tier_structure.entity_hierarchy.map_entities(
                            source_tier=tier_name, target_tier=data_tier, entity_list=selected_entity_list
                        )
                    else:
                        print('Behaviour is not defined for plotting predictions of a group data source of a tier '
                              'above of the parameters tier.')
                        return

                    group_list = data_collection.get_group_list_from_entity_list(data_entity_list)
                    fig, axes = self.create_figure(n_subplots=len(group_list))

                    self.plot_predictions_of_group_list(
                        axes=axes,
                        plotting_function=self.plotting_functions[data_tier][data_type],
                        group_list=group_list,
                        data_collection=data_collection,
                        data_type=data_type,
                        pars_tier=tier_name,
                        data_tier=data_tier
                    )
                else:
                    raise Exception(f'Data type {data_type} is not an Entity or Group Data Source.')

                # fig.show()
                fig.canvas.draw()

        # This time, explicitly display the interactive widget and the output widget
        interactive_widget = widgets.interactive(display_data_and_predictions,
                                                 selected_entity_list=self.tier_entity_selectors[tier_name],
                                                 tier_and_data_type=self.data_type_selector)
        display(interactive_widget, self.output_widget)
