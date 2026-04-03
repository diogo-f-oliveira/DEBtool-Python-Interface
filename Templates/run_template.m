% Baseline generic multitier run template for DEBtoolPyIF.
% Rename this file to run_<species>.m and replace the species name below.

clear;
close all;
global pets

pets = {'your_species_name'}; % Replace with the actual species name.
check_my_pet(pets);

%% Perform estimation and save the DEBtool result file
estim_options('default');
estim_options('max_step_number', $n_steps);
estim_options('max_fun_evals', 5e4);
estim_options('simplex_size', 0.05);
estim_options('filter', 0);
tol_simplex = $tol_simplex;
estim_options('tol_simplex', tol_simplex);

estim_options('pars_init_method', $pars_init_method);
estim_options('results_output', 0);
estim_options('method', 'nm');
[nsteps, converged, fval] = estim_pars; %#ok<NASGU,ASGLU>

n_runs = $n_runs;
estim_options('pars_init_method', 1);
estim_options('results_output', 0);
prev_fval = 1e10;
i = 2;

% Continue full-simplex runs while the objective is still improving.
while (abs(prev_fval - fval) > tol_simplex) && (i < n_runs) && ~converged
    prev_fval = fval;
    fprintf('Run %d\n', i)
    [nsteps, converged, fval] = estim_pars; %#ok<NASGU,ASGLU>
    i = i + 1;
end

%% Save variables, estimation figures, and HTML
estim_options('pars_init_method', 1);
estim_options('results_output', $results_output_mode);
estim_options('method', 'no');
estim_pars;

%% Load data and compute predictions explicitly
load(['results_' pets{1} '.mat']);
[data, auxData, metaData, txtData, weights] = feval(['mydata_' pets{1}]);
q = rmfield(par, 'free');
[prdData, info] = feval(['predict_' pets{1}], q, data, auxData); %#ok<NASGU,ASGLU>

%% Save the enriched result file
save(['results_' pets{1} '.mat'], 'metaData', 'metaPar', 'par', 'txtPar', 'data', 'auxData', 'txtData', 'weights', 'prdData')
