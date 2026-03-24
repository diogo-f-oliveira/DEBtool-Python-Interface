import shutil
from string import Template

from ..utils.data_conversion import convert_dict_to_matlab, convert_list_of_strings_to_matlab
from ..utils.mydata_code_generation import (
    check_files_exist_in_folder,
    generate_meta_data_code,
    generate_tier_variable_code,
)


class TierCodeGenerator:
    FILES_NEEDED = ["mydata", "pars_init", "predict", "run"]

    def __init__(self, tier):
        self.tier_estimator = tier
        self.tier_structure = tier.tier_structure
        self.output_folder = None

        complete, missing_file = self.check_all_files_exist(self.tier_estimator.template_folder)
        if not complete:
            raise Exception(f"Missing template file for tier {self.tier_estimator.name}: {missing_file}.")

    def check_all_files_exist(self, folder):
        files = [f"{tf}_{self.tier_estimator.tier_structure.species_name}.m" for tf in self.FILES_NEEDED]
        complete, missing_file = check_files_exist_in_folder(folder, files)
        return complete, missing_file

    def generate_mydata_file(self, entity_list, pseudo_data_weight=0.1):
        template_path = (
            self.tier_estimator.template_folder /
            f"mydata_{self.tier_estimator.tier_structure.species_name}.m"
        )
        output_path = self.output_folder / f"mydata_{self.tier_estimator.tier_structure.species_name}.m"

        entity_mydata_code_list = []
        group_mydata_code_list = []
        entity_data_types = set()
        group_data_types = set()
        tier_entities = {}
        tier_groups = {}
        tier_subtree = {entity_id: {} for entity_id in entity_list}
        groups_of_entity = {}
        for tier_name in self.tier_structure.entity_hierarchy.get_all_tiers_below(self.tier_estimator.name):
            tier = self.tier_structure.tiers[tier_name]

            tier_entities_to_include = set()
            tier_groups_to_include = set()
            for entity_id in entity_list:
                te_list = self.tier_structure.entity_hierarchy.map_entities(
                    source_tier=self.tier_estimator.name, target_tier=tier_name, entity_list=[entity_id]
                )
                tier_entities_to_include.update(te_list)
                tier_groups_to_include.update(tier.data.get_group_list_from_entity_list(te_list))

                if tier_name != self.tier_estimator.name:
                    tier_subtree[entity_id][tier_name] = te_list

            ent_dt, ent_mc = tier.data.get_entity_mydata_code(tier_entities_to_include)
            entity_data_types.update(set(ent_dt))
            entity_mydata_code_list.extend(ent_mc)
            g_dt, g_mc = tier.data.get_group_mydata_code(tier_entities_to_include)
            group_data_types.update(set(g_dt))
            group_mydata_code_list.extend(g_mc)

            tier_entities[tier_name] = list(tier_entities_to_include)
            tier_groups[tier_name] = list(tier_groups_to_include)
            groups_of_entity.update(tier.data.get_groups_of_entities(tier_entities_to_include))

        entity_data_code = "\n".join(entity_mydata_code_list)
        group_data_code = "\n".join(group_mydata_code_list)

        entity_data_types_code = generate_meta_data_code(
            var_name="entity_data_types",
            converted_data=convert_list_of_strings_to_matlab(list(entity_data_types)),
        )
        group_data_types_code = generate_meta_data_code(
            var_name="group_data_types",
            converted_data=convert_list_of_strings_to_matlab(list(group_data_types)),
        )
        entity_list_code = generate_tier_variable_code(
            var_name="entity_list",
            converted_data=convert_list_of_strings_to_matlab(entity_list),
            label="List of entities",
            pars_init_access=True,
        )

        tier_entities_code = generate_tier_variable_code(
            var_name="tier_entities",
            converted_data=convert_dict_to_matlab(
                {t: convert_list_of_strings_to_matlab(g_list, double_brackets=True) for t, g_list in tier_entities.items()}
            ),
            label="List of entity ids for each tier",
        )

        tier_groups_code = generate_tier_variable_code(
            var_name="tier_groups",
            converted_data=convert_dict_to_matlab(
                {t: convert_list_of_strings_to_matlab(g_list, double_brackets=True) for t, g_list in tier_groups.items()}
            ),
            label="List of groups ids for each tier",
        )

        data_to_format = {}
        for entity_id, subtree in tier_subtree.items():
            data_to_format[entity_id] = convert_dict_to_matlab(
                {t: convert_list_of_strings_to_matlab(e_list, double_brackets=True) for t, e_list in subtree.items()}
            )
        tier_subtree_code = generate_tier_variable_code(
            var_name="tier_subtree",
            converted_data=convert_dict_to_matlab(data_to_format),
            label="Tier subtree",
        )

        groups_of_entity_code = generate_tier_variable_code(
            var_name="groups_of_entity",
            converted_data=convert_dict_to_matlab(
                {e_id: convert_list_of_strings_to_matlab(g_list, double_brackets=True) for e_id, g_list in groups_of_entity.items()}
            ),
            label="Groups each entity belongs to",
        )

        tier_pars_code = generate_tier_variable_code(
            var_name="tier_pars",
            converted_data=convert_list_of_strings_to_matlab(self.tier_estimator.tier_pars),
            label="Tier parameters",
            comment="Tier parameters",
            pars_init_access=True,
        )

        tier_par_init_values = self.tier_estimator.tier_structure.get_init_par_values(
            tier_name=self.tier_estimator.name, entity_list=entity_list
        ).to_dict()
        tier_par_init_values_code = generate_meta_data_code(
            var_name="tier_par_init_values",
            converted_data=convert_dict_to_matlab(
                {p: convert_dict_to_matlab(init_values) for p, init_values in tier_par_init_values.items()}
            ),
        )

        with template_path.open("r") as mydata_template, output_path.open("w") as mydata_out:
            src = Template(mydata_template.read())
            result = src.substitute(
                entity_data=entity_data_code,
                group_data=group_data_code,
                entity_data_types=entity_data_types_code,
                group_data_types=group_data_types_code,
                entity_list=entity_list_code,
                tier_entities=tier_entities_code,
                tier_groups=tier_groups_code,
                tier_subtree=tier_subtree_code,
                groups_of_entity=groups_of_entity_code,
                tier_pars=tier_pars_code,
                tier_par_init_values=tier_par_init_values_code,
                extra_info=self.tier_estimator.extra_info,
                pseudo_data_weight=pseudo_data_weight,
            )
            print(result, file=mydata_out)

    def generate_pars_init_file(self, entity_list):
        if entity_list == "all":
            entity_list = list(self.tier_estimator.tier_structure.entity_hierarchy.get_entities(self.tier_estimator.name))
        pars_dict = self.tier_estimator.tier_structure.get_full_pars_dict(self.tier_estimator.name, entity_list[0])
        template_path = (
            self.tier_estimator.template_folder /
            f"pars_init_{self.tier_estimator.tier_structure.species_name}.m"
        )
        output_path = self.output_folder / f"pars_init_{self.tier_estimator.tier_structure.species_name}.m"

        with template_path.open("r") as pars_init_template, output_path.open("w") as pars_init_out:
            src = Template(pars_init_template.read())
            result = src.substitute(**pars_dict)
            print(result, file=pars_init_out)

    def generate_predict_file(self):
        shutil.copy(
            src=self.tier_estimator.template_folder / f"predict_{self.tier_estimator.tier_structure.species_name}.m",
            dst=self.output_folder,
        )

    def generate_run_file(self):
        template_path = (
            self.tier_estimator.template_folder /
            f"run_{self.tier_estimator.tier_structure.species_name}.m"
        )
        output_path = self.output_folder / f"run_{self.tier_estimator.tier_structure.species_name}.m"
        with template_path.open("r") as run_template, output_path.open("w") as run_out:
            src = Template(run_template.read())
            result = src.substitute(self.tier_estimator.estimation_settings)
            print(result, file=run_out)

    def generate_code(self, entity_list, pseudo_data_weight=0.1):
        self.generate_mydata_file(entity_list=entity_list, pseudo_data_weight=pseudo_data_weight)
        self.generate_pars_init_file(entity_list=entity_list)
        self.generate_predict_file()
        self.generate_run_file()
