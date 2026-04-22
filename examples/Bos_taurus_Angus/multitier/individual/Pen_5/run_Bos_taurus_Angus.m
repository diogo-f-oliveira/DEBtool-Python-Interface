clear;
close all;
global pets

pets = {'Bos_taurus_Angus'};
check_my_pet(pets);

estim_options('default');
estim_options('method', 'nm');
estim_options('max_step_number', 500);
estim_options('max_fun_evals', 50000);
estim_options('simplex_size', 0.25);
estim_options('tol_simplex', 0.0001);
estim_options('pars_init_method', 2);
estim_options('results_output', 0);

[nsteps, converged, fval] = estim_pars;

n_runs = 10;
tol_restart = 0.0001;

estim_options('pars_init_method', 1);
estim_options('results_output', 0);
prev_fval = 1e10;
i = 2;

% Continue full-simplex runs while the objective is still improving.
while (abs(prev_fval - fval) > tol_restart) && (i <= n_runs) && ~converged
    prev_fval = fval;
    fprintf('Run %d/%d\n', i, n_runs)

    [nsteps, converged, fval] = estim_pars;
    i = i + 1;
end

estim_options('pars_init_method', 1);
estim_options('method', 'no');
estim_options('results_output', 0);
estim_pars;


load(['results_' pets{1} '.mat']);
[data, auxData, metaData, txtData, weights] = feval(['mydata_' pets{1}]);
q = rmfield(par, 'free');
[prdData, info] = feval(['predict_' pets{1}], q, data, auxData); 

save(['results_' pets{1} '.mat'], 'metaData', 'metaPar', 'par', 'txtPar', 'data', 'auxData', 'txtData', 'weights', 'prdData')