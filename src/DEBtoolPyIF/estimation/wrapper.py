import matlab.engine
import functools
import os


class MATLABWrapper:
    # TODO: Create a method or decorator to hide output from executing MATLAB functions

    def __init__(self, matlab_session='start', window=False, clear_before=True):
        if matlab_session == 'start':
            self.eng = matlab.engine.start_matlab()
        elif matlab_session == 'find':
            matlab_sessions = matlab.engine.find_matlab()
            if not len(matlab_sessions):
                raise Exception(
                    "No shared MATLAB session found. Make sure to run 'matlab.engine.shareEngine' in the "
                    "MATLAB command window.")
            else:
                self.eng = matlab.engine.connect_matlab(matlab_sessions[0])
        else:
            self.eng = matlab.engine.connect_matlab(matlab_session)
        self.window = window
        self.clear_before = clear_before

    def apply_options_decorator(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            # Apply the options just like in the original apply_options method
            if self.window:
                self.open_matlab_window()
            if self.clear_before:
                self.clear()
            # Call the actual function
            return func(self, *args, **kwargs)

        return wrapper

    def cd(self, workspace_dir):
        self.eng.cd(os.path.abspath(workspace_dir), nargout=0)

    def close(self):
        self.eng.quit()

    def clear(self):
        self.eng.eval("clear", nargout=0)

    def open_matlab_window(self):
        self.eng.desktop(nargout=0)

    # TODO: eval method


class DEBtoolWrapper(MATLABWrapper):
    def __init__(self, estim_filer_dir, species_name, matlab_session=None, window=False, clear_before=True):
        self.estim_files_dir = os.path.abspath(estim_filer_dir)
        # Check folder exists
        if not os.path.isdir(self.estim_files_dir):
            raise Exception(f"Species folder {self.estim_files_dir} does not exist.")
        self.species_name = species_name
        super(DEBtoolWrapper, self).__init__(matlab_session=matlab_session, window=window, clear_before=clear_before)
        self.cd(self.estim_files_dir)

    def load_results_file(self, results_file=None):
        if results_file is None:
            results_file = os.path.join(self.estim_files_dir, f"results_{self.species_name}.mat")
        self.eng.eval(f"load('{results_file}');", nargout=0)

    def run_mydata_file(self):
        self.eng.eval(f"[data, auxData, metaData, txtData, weights] = mydata_{self.species_name};", nargout=0)

    def run_pars_init_file(self):
        self.eng.eval(f"[par, metaPar, txtPar] = pars_init_{self.species_name}(metaData);", nargout=0)

    def run_predict_file(self):
        self.eng.eval(f"[prdData, info] = predict_{self.species_name}(par, data, auxData);", nargout=0)
