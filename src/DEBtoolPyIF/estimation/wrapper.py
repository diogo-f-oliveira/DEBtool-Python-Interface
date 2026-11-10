import functools
import os


def _import_matlab_engine():
    """Import ``matlab.engine`` when a MATLAB session is needed.

    The import is deferred so that DEBtoolPyIF can be imported without the MATLAB Engine API for Python, which can
    only be installed for the MATLAB release on the user's machine.
    """
    try:
        import matlab.engine
    except ImportError as error:
        raise ImportError(
            "Running MATLAB from DEBtoolPyIF needs the MATLAB Engine API for Python, which is not installed. "
            "Install the matlabengine version that matches your MATLAB release, e.g. "
            "'pip install matlabengine==25.2.2' for R2025b. See the DEBtoolPyIF README for details."
        ) from error
    return matlab.engine


class MATLABWrapper:
    # TODO: Create a method or decorator to hide output from executing MATLAB functions
    AUTO_SESSION = 'auto'

    def __init__(self, matlab_session=AUTO_SESSION, window=False, clear_before=True):
        self.eng = None
        self.start_matlab_engine(matlab_session=matlab_session)
        self.window = window
        self.clear_before = clear_before

    def start_matlab_engine(self, matlab_session):
        if matlab_session == 'ignore':
            self.eng = None
            return
        matlab_engine = _import_matlab_engine()
        if matlab_session == self.AUTO_SESSION:
            matlab_sessions = matlab_engine.find_matlab()
            if matlab_sessions:
                self.eng = matlab_engine.connect_matlab(matlab_sessions[0])
            else:
                self.eng = matlab_engine.start_matlab()
        elif matlab_session == 'start':
            self.eng = matlab_engine.start_matlab()
        elif matlab_session == 'find':
            matlab_sessions = matlab_engine.find_matlab()
            if not len(matlab_sessions):
                raise Exception(
                    "No shared MATLAB session found. Make sure to run 'matlab.engine.shareEngine' in the "
                    "MATLAB command window.")
            else:
                self.eng = matlab_engine.connect_matlab(matlab_sessions[0])
        else:
            self.eng = matlab_engine.connect_matlab(matlab_session)

    def apply_options_decorator(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
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
    def __init__(self, estim_files_dir, species_name, matlab_session=MATLABWrapper.AUTO_SESSION, window=False,
                 clear_before=True):
        self.estim_files_dir = os.path.abspath(estim_files_dir)
        # Check folder exists
        if not os.path.isdir(self.estim_files_dir):
            raise Exception(f"Species folder {self.estim_files_dir} does not exist.")
        self.species_name = species_name
        super(DEBtoolWrapper, self).__init__(matlab_session=matlab_session, window=window, clear_before=clear_before)
        if self.eng is not None:
            self.cd(self.estim_files_dir)

    def load_results_file(self, results_file=None):
        if results_file is None:
            results_file = os.path.abspath(os.path.join(self.estim_files_dir, f"results_{self.species_name}.mat"))
        self.eng.eval(f"load('{results_file}');", nargout=0)

    def run_mydata_file(self):
        self.eng.eval(f"[data, auxData, metaData, txtData, weights] = mydata_{self.species_name};", nargout=0)

    def run_pars_init_file(self):
        self.eng.eval(f"[par, metaPar, txtPar] = pars_init_{self.species_name}(metaData);", nargout=0)

    def run_predict_file(self):
        self.eng.eval(f"[prdData, info] = predict_{self.species_name}(par, data, auxData);", nargout=0)
