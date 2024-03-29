import pandas as pd
import matplotlib.pyplot as plt
import ipywidgets as widgets
from IPython.display import display, clear_output

from .multitier import MultiTierStructure


class TierVisualizer:
    def __init__(self, tier_structure: MultiTierStructure, plotting_functions: dict):
        self.tier_structure = tier_structure
        self.tier_sample_selectors = {}
        for tier_name, tier in self.tier_structure.tiers.items():
            self.tier_sample_selectors[tier_name] = widgets.Dropdown(
                options=tier.tier_sample_list,
                description=f'{tier_name}:'
            )
        self.data_type_selector = widgets.Dropdown(
            options=self.tier_structure.data.data_types,
            description='Data Type:'
        )
        self.plotting_functions = plotting_functions
        self.output_widget = widgets.Output()  # Output widget to capture and display plots

    def plot_data_and_predictions(self, tier_name):
        def display_data_and_predictions(tier_sample, data_type):
            with self.output_widget:  # Use the output widget as the context for plot display
                clear_output(wait=True)  # Clear the previous plots
                ind_list = self.tier_structure.get_tier_sample_inds(tier_name, [tier_sample])[tier_sample]
                if data_type in self.tier_structure.data.ind_data_types:
                    # Create subplots, max 5 per row
                    n_cols = 5
                    n_rows = len(ind_list) // n_cols + (len(ind_list) % n_cols > 0)
                    fig, axes = plt.subplots(nrows=n_rows, ncols=n_cols, figsize=(4 * n_cols, 4 * n_rows),
                                             tight_layout=True)
                    for i, ind_id in enumerate(ind_list):
                        ax = axes[i // n_cols, i % n_cols] if n_rows > 1 else axes[i % n_cols]
                        self.plotting_functions[data_type](
                            ax=ax,
                            tier_structure=self.tier_structure,
                            tier_name=tier_name,
                            tier_sample=tier_sample,
                            ind_id=ind_id
                        )
                else:
                    group_ids_list = self.tier_structure.data.get_group_list_from_ind_list(ind_list)
                    # Create subplots, max 5 per row
                    n_cols = 5
                    n_rows = len(group_ids_list) // n_cols + (len(group_ids_list) % n_cols > 0)
                    fig, axes = plt.subplots(nrows=n_rows, ncols=n_cols, figsize=(4 * n_cols, 4 * n_rows),
                                             tight_layout=True)
                    for i, group_id in enumerate(group_ids_list):
                        ax = axes[i // n_cols, i % n_cols] if n_rows > 1 else axes[i % n_cols]
                        self.plotting_functions[data_type](
                            ax=ax,
                            tier_structure=self.tier_structure,
                            tier_name=tier_name,
                            tier_sample=tier_sample,
                            group_id=group_id
                        )
                # Hide unused axes
                for j in range(i + 1, n_rows * n_cols):
                    axes.flat[j].axis('off')

        # This time, explicitly display the interactive widget and the output widget
        interactive_widget = widgets.interactive(display_data_and_predictions,
                                                 tier_sample=self.tier_sample_selectors[tier_name],
                                                 data_type=self.data_type_selector)
        display(interactive_widget, self.output_widget)
