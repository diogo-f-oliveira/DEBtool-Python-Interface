function initialize_ind_pars_from_csv(csv_file, species_name)
%UNTITLED2 Summary of this function goes here
%   Detailed explanation goes here

% Get pars and ind list from file
pars_table = readtable(csv_file);
ind_pars = pars_table.Properties.VariableNames(2:end);
id_col = pars_table.Properties.VariableNames{1};
ind_list = pars_table.(id_col);

% Load results file
load(['results_' species_name '.mat'], 'metaData');

% Change metaData
metaData.ind_pars = ind_pars;
metaData.inds = ind_list;

% Get par from pars_init and change individual parameter values
[par, metaPar, txtPar] = feval(['pars_init_' species_name], metaData);

for p=1:length(metaData.ind_pars)
    par_name = metaData.ind_pars{p};
    for i=1:length(metaData.inds)
        varname = [par_name '_' metaData.inds{i}];
        par.(varname) = pars_table.(par_name)(i);
    end
end

save(['results_' species_name '.mat'], 'metaData', 'metaPar', 'par', 'txtPar')
end

