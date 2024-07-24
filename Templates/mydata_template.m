function [data, auxData, metaData, txtData, weights] = mydata_template

%% set metaData
metaData.phylum     = '';
metaData.class      = '';
metaData.order      = '';
metaData.family     = '';
metaData.species    = '';
metaData.species_en = '';
metaData.T_typical  = 0; % K, body temp
metaData.data_0     = {};
metaData.data_1     = {};

metaData.COMPLETE = 2.5; % using criteria of LikaKear2011

metaData.author   = {''};
% metaData.date_subm = [2024 02 02];
% metaData.email    = {''};
% metaData.address  = {''};

%% Group data
$group_data

% Group data types
$group_data_types

% Cell array of group_ids
$group_list

%% Individual data
$individual_data

% Individual data types
$ind_data_types

% Cell array of ind_ids
$ind_list

% Struct with form groups_of_ind.(ind_id) = list_of_groups_ids_ind_belongs_to
$groups_of_ind

% Extra info
$extra_info

% Cell array of tier_sample_ids
$tier_sample_list

% Struct with form
% tier_sample_inds.(tier_sample_id) = list_of_inds_in_tier_sample
$tier_sample_inds

%% Tier parameters
% Cell array with tier parameters
$tier_pars

% Initial values for each tier parameter and sample
% Struct with form tier_par_init_values.(par).(tier_sample_id) = value;
$tier_par_init_values


%% Set temperature data and remove weights for dummy variables
weights = setweights(data, []);

metaData.data_fields = fieldnames(data);
temp = struct();
for i = 1:length(metaData.data_fields)
    % Add typical temperature only to fields without specified temperature
    field = metaData.data_fields{i};
    if ~isfield(temp, field)
        temp.(field) = metaData.T_typical;
        units.temp.(field) = 'K';
        label.temp.(field) = 'temperature';
    end
    % Removing weight from dummy variables
    if strcmp(label.(field), 'Dummy variable')
        weights.(field) = 0;
    end
    % Saving data variable names in metaData
    if length(data.(field)) > 1
        metaData.data_1{end+1} = field; % univariate
    else
        metaData.data_0{end+1} = field; % zero-variate
    end
end

%% Set weight of individual data
for ts=1:length(tiers.tier_sample_list)
    tier_sample_id = tiers.tier_sample_list{ts};
    sample_inds = tiers.tier_sample_inds.(tier_sample_id);
    n_sample_inds = length(sample_inds);
    
    % Set weight of individual data
    for dt=1:length(metaData.ind_data_types)
        data_type = metaData.ind_data_types{dt};
        
        for i=1:length(sample_inds)
            ind_id = sample_inds{i};
            data_varname = [data_type '_' ind_id];
            if isfield(data, data_varname)
                weights.(data_varname) = weights.(data_varname) / n_sample_inds;
            end
        end
    end
end


%% Set pseudo-data for tier parameters
for ts=1:length(tiers.tier_sample_list)
    tier_sample_id = tiers.tier_sample_list{ts};
    for p=1:length(tiers.tier_pars)
        par_name = tiers.tier_pars{p};
        varname = [par_name '_' tier_sample_id];
        
        data.psd.(varname) = metaData.tier_par_init_values.(par_name).(tier_sample_id);
        units.psd.(varname) = '';
        label.psd.(varname) = '';
        weights.psd.(varname) = $pseudo_data_weight;
    end
end

%% pack auxData and txtData for output
auxData.temp = temp;
auxData.tiers = tiers;
auxData.init = init;
txtData.units = units;
txtData.label = label;
txtData.bibkey = bibkey;
txtData.comment = comment;

%% Discussion points
D1 = '';
D2 = '';
metaData.discussion = struct('D1', D1, 'D2', D2);

%% Data Sources and References


