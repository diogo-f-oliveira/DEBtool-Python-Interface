import matlab.engine
import functools
import os


class DEBtoolWrapper:
    # TODO: Create a method or decorator to hide output from executing MATLAB functions

    def __init__(self, matlab_session=None, window=False, clear_before=True, species_name=None):
        if matlab_session is None:
            self.eng = matlab.engine.start_matlab()
        if matlab_session == 'find':
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
        self.species_name = species_name

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
