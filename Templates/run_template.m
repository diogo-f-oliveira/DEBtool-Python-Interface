clear;
close all; 
global pets

pets = {''};
check_my_pet(pets);


%% Perform estimation but only save .mat file
estim_options('default');
estim_options('max_step_number',$n_steps);
estim_options('max_fun_evals',5e4);
estim_options('simplex_size',0.05);
estim_options('filter',0);
tol_simplex = $tol_simplex;  
estim_options('tol_simplex',tol_simplex);

estim_options('pars_init_method', $pars_init_method);
estim_options('results_output', 0);
estim_options('method', 'nm');
[nsteps, info, fval] = estim_pars;

n_runs = $n_runs;
estim_options('pars_init_method', 1);
estim_options('results_output', 0);
prev_fval = 1e10;
prev2_fval = 1e10;
i = 2;
% full simplex without significant improvement
while (abs(prev2_fval-fval) > tol_simplex) && (i < n_runs)
    prev2_fval = prev_fval;
    prev_fval = fval;
    fprintf('Run %d\n', i)
    [nsteps, info, fval] = estim_pars;
    i = i + 1;
end

%% Compute predictions
load(['results_' pets{1} '.mat']);
[data, auxData, metaData, txtData, weights] = feval(['mydata_' pets{1}]);
q = rmfield(par, 'free');
[prdData, info] = feval(['predict_' pets{1}], q, data, auxData);

%% Save variables, estimation figures, and HTML
estim_options('pars_init_method', 1)
estim_options('results_output', $results_output_mode);
estim_options('method', 'no');

estim_pars;

%% Save data and predictions
save(['results_' pets{1} '.mat'], 'metaData', 'metaPar', 'par', 'txtPar', 'data', 'prdData')