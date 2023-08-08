import matlab.engine
from copy import deepcopy
import os
import random


class DEBModelParametrizationProblem:
    GEN_FACTOR = 20
    REQUIRED_FILES = ('mydata', 'pars_init', 'predict')

    def __init__(self, species_folder, species_name, window=False):
        """
        Initialize the problem class for a given species.
        @param species_folder: The folder with the files needed to run DEB models and compute the loss function
        @param species_name: The name of the species
        @param window: if true, a MATLAB window is opened where the commands are ran. Useful to check any variables in
        the workspace of MATLAB. Updates every time a command is called.
        """
        self.species_name = species_name
        # Check that the folder has the correct files
        for file in self.REQUIRED_FILES:
            if not os.path.isfile(f"{species_folder}/{file}_{self.species_name}.m"):
                raise Exception(f"{file}_{self.species_name}.m file does not exist in the provided folder.")
        self.species_folder = species_folder

        # Start the MATLAB engine
        self.eng = matlab.engine.start_matlab()
        # Open a MATLAB window
        if window:
            self.eng.desktop(nargout=0)
        self.eng.cd(self.species_folder, nargout=0)

        # Call my_data.m to get the data for the estimation
        self.eng.eval(f"[data, auxData, metaData, txtData, weights] = mydata_{self.species_name};", nargout=0)

        # Call pars_init.m to get the parameter values
        self.eng.eval(f"[par, metaPar, txtPar] = pars_init_{species_name}(metaData);", nargout=0)
        self._all_pars = self.eng.workspace['par']
        self.pars = tuple(p for p, f in self._all_pars['free'].items() if f > 0)

        # Get model type
        self.model_type = self.eng.workspace['metaPar']['model']

        # Set up loss function global variable
        self.eng.eval("global lossfunction;", nargout=0)
        self.eng.eval("lossfunction = 'sb';", nargout=0)

    @property
    def pars_dict(self):
        """
        Returns a dictionary with the parameters of the calibration problem and a 0 value.
        @return: a dictionary with the parameters of the problem
        """
        return {p: 0 for p in self.pars}

    @property
    def get_par_bounds(self):
        """
        Returns a set of bounds for parameters values. All parameters must be greater than zero.
        Efficiencies can not be greater than 1. All other parameters do not have a maximum value and the bounds are
        centered around the values in the pars_init.m file. These bounds can be increase if desired.
        @return: A dictionary with parameters as keys and a tuple of bounds (min, max) for each parameter
        """
        par_bounds = self.pars_dict
        for p in par_bounds:
            # If the parameter is an efficiency it is between 0 and 1
            if 'kap' in p:
                par_bounds[p] = (0, 1)
            # Otherwise give a large range to search around the value given in the pars_init file
            else:
                v = self._all_pars[p]
                par_bounds[p] = (v / self.GEN_FACTOR, v * self.GEN_FACTOR)
        return par_bounds

    def check_pars(self, pars_dict: dict):
        """
        Checks that pars_dict has all and only the parameters of the problem
        @param pars_dict: A dictionary with the paramters of the problem
        @return: None, raises an exception if the pars_dict is not correct
        """
        # if any(self.pars == tuple(pars_dict.keys())):
        for p in self.pars:
            if p not in pars_dict:
                raise Exception(f"Missing parameter values from pars dict: {p}")
        for p in pars_dict:
            if p not in self.pars:
                raise Exception(f"Extra parameter ")

    def get_complete_pars(self, pars_dict: dict):
        """
        Fills in the remaining parameters of the DEB model that do not need to be calibrated. This dictionary is what
        is passed to MATLAB to compute predictions with DEB theory and the loss function.
        @param pars_dict: A dictionary with the parameters of the problem
        @return: A dictionary with all the parameters of the DEB model
        """
        complete_pars = deepcopy(self._all_pars)
        for p, v in pars_dict.items():
            complete_pars[p] = v
        return complete_pars

    def check_feasibilty(self, pars_dict: dict):
        """
        Checks that the parameters are feasible by calling a filter function for the DEB model
        @param pars_dict: A dictionary with the parameters of the problem
        @return: True if the parameter values are a feasible solution, False otherwise
        """
        self.check_pars(pars_dict)
        complete_pars = self.get_complete_pars(pars_dict)
        self.eng.workspace['par'] = complete_pars
        return bool(self.eng.eval(f"filter_{self.model_type}(par);", nargout=1))

    def evaluate(self, pars_dict: dict):
        """
        Computes the loss function for a set of parameters
        @param pars_dict:
        @return: the value of the loss function
        """
        # Check that pars dict has all pars
        self.check_pars(pars_dict)

        # Check feasibility
        if not self.check_feasibilty(pars_dict):
            return float('nan')

        # Pass pars to MATLAB
        self.eng.workspace['par'] = self.get_complete_pars(pars_dict)
        # Get predictions
        self.eng.eval(f"[prdData, info] = predict_{self.species_name}(par, data, auxData);", nargout=0)
        # If predict failed, the parameters are infeasible
        if not self.eng.workspace['info']:
            return float('nan')

        # Compute loss function
        self.eng.eval("loss = lossfun(data, prdData, weights);", nargout=0)
        # Retrieve loss function value
        return self.eng.workspace['loss']


if __name__ == '__main__':
    species_name = "Bos_taurus_Mertolenga"
    species_folder = r"C:\Users\diogo\OneDrive - Universidade de Lisboa\Terraprima\Code\DEB Parameter Estimation\Mertolenga\Standard\t_0 pseudo data weight 0"

    problem = DEBModelParametrizationProblem(species_folder=species_folder, species_name=species_name, window=True)

    # Parameters are all zero, solution is infeasible
    pars_dict = problem.pars_dict
    print(problem.evaluate(pars_dict))

    # Randomly trying different parameter values
    default_pars_dict = {'p_Am': 1689,
                         'kap_X': 0.123,
                         'v': 0.09545,
                         'kap': 0.9174,
                         'p_M': 26.26,
                         'E_G': 8880,
                         'E_Hb': 7716000.0,
                         'E_Hx': 47650000.0,
                         'E_Hp': 116700000.0,
                         't_0': 96.5,
                         'p_Am_f': 1689}
    for i in range(100):
        pars_dict = problem.pars_dict
        for p, v in default_pars_dict.items():
            pars_dict[p] = v * (random.random() + 0.5)
        loss = problem.evaluate(pars_dict)
        print(loss)
