from string import Template
import os
import shutil

from .data_sources import DataCollection, IndDataSourceBase
from .utils import check_files_exist_in_folder




class CodeGeneratorBase:
    FILES_NEEDED = ['mydata', 'pars_init', 'predict', 'run']

    def __init__(self, template_folder: str, individual_params: list, species_name: str, data: DataCollection):
        self.data = data
        self.mydata_code = []
        self.estimation_settings = {}

        self.individual_params = individual_params
        self.species_name = species_name

        files = [f"{tf}_{self.species_name}.m" for tf in self.FILES_NEEDED]
        complete, missing_file = check_files_exist_in_folder(template_folder, files)
        if not complete:
            raise Exception(f"Missing template file for {missing_file}.")
        self.template_folder = template_folder

    def set_estimation_settings(self, n_runs=25, results_output_mode=0, n_steps=500, pars_init_method=1,
                                tol_simplex=1e-4):
        self.estimation_settings['n_runs'] = n_runs
        self.estimation_settings['results_output_mode'] = results_output_mode
        self.estimation_settings['n_steps'] = n_steps
        self.estimation_settings['pars_init_method'] = pars_init_method
        self.estimation_settings['tol_simplex'] = tol_simplex

    def create_mydata_file(self, output_folder, ind_list):
        self.mydata_code = self.data.get_mydata_code(ind_list=ind_list)
        # replaced self.get_mydata_code(ind_list=ind_list)
        mydata_template = open(f'{self.template_folder}/mydata_{self.species_name}.m', 'r')
        mydata_out = open(f'{output_folder}/mydata_{self.species_name}.m', 'w')
        src = Template(mydata_template.read())
        result = src.substitute(ind_pars=str(self.individual_params)[1:-1],
                                individual_data='\n'.join(self.mydata_code),
                                ind_list=str(ind_list)[1:-1],
                                univar_types=self.data.data_types.__repr__()[1:-1])
        print(result, file=mydata_out)
        mydata_out.close()
        mydata_template.close()

    def create_pars_init_file(self, output_folder):
        shutil.copy(src=f"{self.template_folder}/pars_init_{self.species_name}.m", dst=f"{output_folder}")

    def create_predict_file(self, output_folder):
        shutil.copy(src=f"{self.template_folder}/predict_{self.species_name}.m", dst=f"{output_folder}")

    def create_run_file(self, output_folder):
        run_template = open(f'{self.template_folder}/run_{self.species_name}.m', 'r')
        run_out = open(f'{output_folder}/run_{self.species_name}.m', 'w')
        src = Template(run_template.read())
        result = src.substitute(self.estimation_settings)
        print(result, file=run_out)
        run_out.close()
        run_template.close()

    def generate_code(self, output_folder, ind_list=None):
        return


class GroupStepCodeGenerator(CodeGeneratorBase):
    def __init__(self, template_folder: str, individual_params: list, species_name: str, data: DataCollection):
        super().__init__(template_folder, individual_params, species_name, data)

    def create_mydata_file(self, output_folder, ind_list, ind_data_weight=None, extra_info=None):
        self.mydata_code = self.data.get_mydata_code(ind_list=ind_list)
        mydata_template = open(f'{self.template_folder}/mydata_{self.species_name}.m', 'r', encoding="utf8")
        mydata_out = open(f'{output_folder}/mydata_{self.species_name}.m', 'w', encoding="utf-8")
        src = Template(mydata_template.read())
        if ind_data_weight is None:
            ind_data_weight = "struct("
            for ds in self.data.data_sources:
                n = len(ds.individuals) if isinstance(ds, IndDataSourceBase) else len(ds.groups)
                ind_data_weight += f"'{ds.TYPE}', 1/{n}, "
            ind_data_weight = ind_data_weight[:-2] + ");"
        if extra_info is None:
            extra_info = {}
        result = src.substitute(ind_pars=str(self.individual_params)[1:-1],
                                individual_data='\n'.join(self.mydata_code),
                                ind_list=str(ind_list)[1:-1],
                                ind_data_weight=ind_data_weight,
                                univar_types=self.data.data_types.__repr__()[1:-1],
                                **extra_info)

        print(result, file=mydata_out)
        mydata_out.close()
        mydata_template.close()

    def generate_code(self, output_folder, ind_list=None, ind_data_weight=None, extra_info=None):
        # Create folder if it doesn't exist
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        # If no ind list is provided then all individuals from all data sources are used
        if ind_list is None:
            ind_list = list(self.data.individuals)

        # Generate files
        self.create_mydata_file(output_folder, ind_list, ind_data_weight=ind_data_weight, extra_info=extra_info)
        self.create_pars_init_file(output_folder)
        self.create_predict_file(output_folder)
        self.create_run_file(output_folder)

        # Check that files were created properly
        files = [f"{tf}_{self.species_name}.m" for tf in self.FILES_NEEDED]
        complete, missing_file = check_files_exist_in_folder(output_folder, files)
        if not complete:
            raise Exception(f"An error occurred whilst creating file {missing_file}.")


class IndividualStepCodeGenerator(CodeGeneratorBase):
    def __init__(self, template_folder: str, individual_params: list, species_name: str, data: DataCollection):
        super().__init__(template_folder, individual_params, species_name, data)
        # TODO: Set output folder as an attribute
        self.pars_dict = {}

    # TODO: read pars from file
    def read_default_pars_file(self, pars_file):
        default_pars = {}
        with open(pars_file, 'r') as f:
            for line in f:
                p, v = line.split()
                default_pars[p] = float(v)
        return default_pars

    def create_pars_init_file(self, output_folder, default_pars, estimate_group_pars=0, extra_par_values=''):
        # Get default values for parameters
        self.pars_dict = {}
        # TODO: Check if it is a path, otherwise raise Exception
        if not isinstance(default_pars, dict):
            self.read_default_pars_file(default_pars)
        else:
            self.pars_dict = default_pars

        # Create files
        pars_init_template = open(f'{self.template_folder}/pars_init_{self.species_name}.m', 'r')
        pars_init_out = open(f'{output_folder}/pars_init_{self.species_name}.m', 'w')
        src = Template(pars_init_template.read())
        result = src.substitute(estimate_group_pars=int(estimate_group_pars), extra_par_values=extra_par_values,
                                **self.pars_dict)
        print(result, file=pars_init_out)
        pars_init_out.close()
        pars_init_template.close()

    def create_mydata_file(self, output_folder, ind_list, group_list, species_data_weight=1, ind_data_weight=None,
                           pseudo_data: dict = None, pseudo_data_weight=0.1, extra_info=None):
        self.mydata_code = self.data.get_mydata_code(ind_list=ind_list)
        mydata_template = open(f'{self.template_folder}/mydata_{self.species_name}.m', 'r', encoding="utf8")
        mydata_out = open(f'{output_folder}/mydata_{self.species_name}.m', 'w', encoding="utf-8")
        src = Template(mydata_template.read())
        if ind_data_weight is None:
            ind_data_weight = f"1 / {len(ind_list)}"
        if pseudo_data is None:
            pseudo_data_code = ''
        else:
            pseudo_data_code = '\n'.join([f"pseudo_data_values.{p} = {val};" for p, val in pseudo_data.items()])
        if extra_info is None:
            extra_info = {}

        result = src.substitute(ind_pars=str(self.individual_params)[1:-1],
                                individual_data='\n'.join(self.mydata_code),
                                ind_list=str(ind_list)[1:-1],
                                group_list=str(group_list)[1:-1],
                                species_data_weight=species_data_weight,
                                ind_data_weight=ind_data_weight,
                                univar_types=self.data.data_types.__repr__()[1:-1],
                                pseudo_data_values=pseudo_data_code,
                                pseudo_data_weight=pseudo_data_weight,
                                **extra_info)
        print(result, file=mydata_out)
        mydata_out.close()
        mydata_template.close()

    def generate_code(self, output_folder, default_pars, ind_list=None, group_list=None, estimate_group_pars=0,
                      extra_info=None, extra_par_values='', **mydata_options):
        # Create folder if it doesn't exist
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        # If no ind list is provided then all individuals from all data sources are used
        if ind_list is None:
            ind_list = self.data.individuals
        if group_list is None:
            group_list = self.data.groups

        # Generate files
        self.create_mydata_file(output_folder, ind_list, group_list, extra_info=extra_info, **mydata_options)
        self.create_pars_init_file(output_folder, default_pars, estimate_group_pars=estimate_group_pars,
                                   extra_par_values=extra_par_values)
        self.create_predict_file(output_folder)
        self.create_run_file(output_folder)

        # Check that files were created properly
        files = [f"{tf}_{self.species_name}.m" for tf in self.FILES_NEEDED]
        complete, missing_file = check_files_exist_in_folder(output_folder, files)
        if not complete:
            raise Exception(f"A mistake occurred whilst creating file {missing_file}.")


def format_extra_info(var_name, data, label, comment='-', units='-', bibkey='-', pars_init_access=False):
    s = f"data.{var_name} = 10; " \
        f"units.{var_name} = '-'; " \
        f"label.{var_name} = 'Dummy variable'; " \
        f"comment.{var_name} = '{comment}'; " \
        f"bibkey.{var_name} = '{bibkey}'; \n"
    s += f"extra.{var_name} = {data}; " \
         f"units.extra.{var_name} = '{units}'; " \
         f"label.extra.{var_name} = '{label}'; \n"
    if pars_init_access:
        s += f"metaData.{var_name} = extra.{var_name}; % Save in metaData to use in pars_init.m"
    return s
