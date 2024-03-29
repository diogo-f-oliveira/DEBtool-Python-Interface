import functools
import os
import matlab.engine
from io import StringIO


def run_estimation(run_files_dir, species_name, window=False):
    eng = matlab.engine.start_matlab()
    if window:
        eng.desktop(nargout=0)

    # Check that file exists
    if not os.path.isfile(f"{run_files_dir}/run_{species_name}.m"):
        raise Exception("run.m file does not exist.")

    # Change MATLAB working directory
    eng.cd(run_files_dir, nargout=0)

    # Run estimation
    eng.eval(f'run_{species_name}', nargout=0)

    # Load results .mat file and return parameters and estimation errors.
    eng.eval(f"load('{run_files_dir}/results_{species_name}.mat')", nargout=0)
    pars = eng.workspace['par']
    estimation_errors = eng.workspace['metaPar']
    meta_data = eng.workspace['metaData']
    # Close engine
    eng.quit()
    return pars, estimation_errors, meta_data


class EstimationRunner:
    # TODO: Store empty buffers for output as class attributes so that hide_output can be a method option

    def __init__(self, window=False, clear_before=True, species_name=None):
        self.window = window
        self.clear_before = clear_before
        self.eng = matlab.engine.start_matlab()
        self.species_name = species_name

    def apply_options_decorator(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            # Apply the options just like in the original apply_options method
            if self.window:
                self.eng.desktop(nargout=0)
            if self.clear_before:
                self.eng.eval("clear", nargout=0)
            # Call the actual function
            return func(self, *args, **kwargs)

        return wrapper

    @apply_options_decorator
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

    @apply_options_decorator
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

    @apply_options_decorator
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

    @apply_options_decorator
    def fetch_data_from_mat_file(self, run_files_dir: str, results_file=None):
        if results_file is None:
            results_file = f"results_{self.species_name}.mat"

        # Change MATLAB working directory
        self.cd(workspace_dir=run_files_dir)
        # Load results file in MATLAB
        self.eng.eval(f"load('{os.path.abspath(run_files_dir)}/{results_file}');", nargout=0)

        return self.eng.workspace['data']

    @apply_options_decorator
    def fetch_predictions_from_mat_file(self, run_files_dir: str, results_file=None):
        if results_file is None:
            results_file = f"results_{self.species_name}.mat"

        # Change MATLAB working directory
        self.cd(workspace_dir=run_files_dir)
        # Load results file in MATLAB
        self.eng.eval(f"load('{os.path.abspath(run_files_dir)}/{results_file}');", nargout=0)

        return self.eng.workspace['prdData']

    def cd(self, workspace_dir):
        self.eng.cd(os.path.abspath(workspace_dir), nargout=0)

    def close(self):
        self.eng.quit()


if __name__ == '__main__':
    print('Done!')
