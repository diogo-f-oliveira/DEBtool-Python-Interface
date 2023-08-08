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
    def __init__(self):
        self.eng = matlab.engine.start_matlab()
        # TODO: Make all arguments as class attributes

    def run_estimation(self, run_files_dir: str, species_name: str, window=False, clear_before=False, close_after=False,
                       hide_output=False):
        """

        @param run_files_dir: directory with estimation files
        @param species_name: species name that is used to find the required files
        @param window: if true, a new MATLAB window is opened to run the estimation
        @param clear_before: if true, MATLAB workspace is cleared before running estimation
        @param close_after: if True, MATLAB connection is closed after running estimation
        @param hide_output: if True, MATLAB command window output is not shown
        @return:
        """
        if window:
            self.eng.desktop(nargout=0)
        if clear_before:
            self.eng.eval("clear", nargout=0)

        # Check that file exists
        if not os.path.isfile(f"{run_files_dir}/run_{species_name}.m"):
            raise Exception("run.m file does not exist.")

        # Change MATLAB working directory
        self.cd(workspace_dir=run_files_dir)

        # Run estimation
        if hide_output:
            out = StringIO()
            err = StringIO()
            self.eng.eval(f'run_{species_name}', nargout=0, stdout=out, stderr=err)
        else:
            self.eng.eval(f'run_{species_name}', nargout=0)

        # Load results .mat file and return parameters and estimation errors.
        # self.eng.eval(f"load('{run_files_dir}/results_{species_name}.mat')", nargout=0)
        # TODO: More flexibility in which results are pulled

        pars = self.eng.workspace['par']

        estimation_errors = {'final': self.eng.workspace['final_lf_values'],
                             # 'noindpars': self.eng.workspace['noindpars_lf_values'],
                             're': {d: e[0] for d, e in zip(
                                 self.eng.workspace['metaData']['data_0'] + self.eng.workspace['metaData']['data_1'],
                                 self.eng.workspace['metaPar']['RE'])}}
        meta_data = self.eng.workspace['metaData']
        success = self.eng.workspace['info']

        # Shut down engine
        if close_after:
            self.close()

        # Return results
        results = dict(pars=pars, estimation_errors=estimation_errors, meta_data=meta_data, success=success)
        return results

    def fetch_pars_from_mat_file(self, run_files_dir: str, species_name: str, window=False, clear_before=True,
                                 close_after=False):
        if window:
            self.eng.desktop(nargout=0)
        if clear_before:
            self.eng.eval("clear", nargout=0)

        # Change MATLAB working directory
        self.cd(workspace_dir=run_files_dir)

        self.eng.eval(f"load('{os.path.abspath(run_files_dir)}/results_{species_name}.mat')", nargout=0)

        # Shut down engine
        if close_after:
            self.close()

        return self.eng.workspace['par']

    def cd(self, workspace_dir):
        self.eng.cd(os.path.abspath(workspace_dir), nargout=0)

    def close(self):
        self.eng.quit()


if __name__ == '__main__':
    print('Done!')
