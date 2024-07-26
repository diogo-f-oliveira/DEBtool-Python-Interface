import os
from io import StringIO

from .wrapper import DEBtoolWrapper


class EstimationRunner(DEBtoolWrapper):
    # TODO: Store empty buffers for output as class attributes so that hide_output can be a method option

    @DEBtoolWrapper.apply_options_decorator
    def run_estimation(self, run_files_dir: str, hide_output=True):
        """

        @param run_files_dir: directory with estimation files
        @param species_name: species name that is used to find the required files
        @param hide_output: if True, MATLAB command window output is not shown
        @return:
        """

        # Check that file exists
        if not os.path.isfile(f"{run_files_dir}/run_{self.species_name}.m"):
            raise Exception("run.m file does not exist.")

        # Change MATLAB working directory
        self.cd(workspace_dir=run_files_dir)

        # Run estimation
        if hide_output:
            out = StringIO()
            err = StringIO()
            self.eng.eval(f'run_{self.species_name}', nargout=0, stdout=out, stderr=err)
        else:
            self.eng.eval(f'run_{self.species_name}', nargout=0)

        success = self.eng.workspace['info']

        return success

    @DEBtoolWrapper.apply_options_decorator
    def fetch_pars_from_mat_file(self, run_files_dir: str, results_file=None):

        if results_file is None:
            results_file = f"results_{self.species_name}.mat"

        # Change MATLAB working directory
        self.cd(workspace_dir=run_files_dir)
        # Load results file in MATLAB
        self.eng.eval(f"load('{os.path.abspath(run_files_dir)}/{results_file}');", nargout=0)
        # Fetch parameters from MATLAB workspace
        pars = self.eng.workspace['par']

        return pars

    @DEBtoolWrapper.apply_options_decorator
    def fetch_errors_from_mat_file(self, run_files_dir: str, error_type='RE', results_file=None):
        if error_type not in ('RE', 'SAE', 'SSE'):
            raise Exception(f"Invalid error_type {error_type}. Error type must be either 'RE', 'SAE' or 'SSE'.")

        if results_file is None:
            results_file = f"results_{self.species_name}.mat"

        # Change MATLAB working directory
        self.cd(workspace_dir=run_files_dir)
        # Load results file in MATLAB
        self.eng.eval(f"load('{os.path.abspath(run_files_dir)}/{results_file}');", nargout=0)
        # Build dict with prediction errors for each data field
        data_fields = list(self.eng.workspace['metaData']['data_fields'])  # pseudo-data is removed
        errors = {d: e[0] for d, e in zip(data_fields, self.eng.workspace['metaPar'][error_type])}

        return errors

    @DEBtoolWrapper.apply_options_decorator
    def fetch_data_from_mat_file(self, run_files_dir: str, results_file=None):
        if results_file is None:
            results_file = f"results_{self.species_name}.mat"

        # Change MATLAB working directory
        self.cd(workspace_dir=run_files_dir)
        # Load results file in MATLAB
        self.eng.eval(f"load('{os.path.abspath(run_files_dir)}/{results_file}');", nargout=0)

        return self.eng.workspace['data']

    @DEBtoolWrapper.apply_options_decorator
    def fetch_predictions_from_mat_file(self, run_files_dir: str, results_file=None):
        if results_file is None:
            results_file = f"results_{self.species_name}.mat"

        # Change MATLAB working directory
        self.cd(workspace_dir=run_files_dir)
        # Load results file in MATLAB
        self.eng.eval(f"load('{os.path.abspath(run_files_dir)}/{results_file}');", nargout=0)

        return self.eng.workspace['prdData']


if __name__ == '__main__':
    print('Done!')
