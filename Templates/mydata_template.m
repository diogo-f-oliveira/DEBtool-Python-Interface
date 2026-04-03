function [data, auxData, metaData, txtData, weights] = mydata_template
% Baseline generic multitier mydata template for DEBtoolPyIF.
% Rename this file to mydata_<species>.m and adapt the metadata, weighting,
% pseudo-data, and references for your project.

%% initialize containers used throughout the file
data = struct();
init = struct();
tiers = struct();
units = struct();
label = struct();
bibkey = struct();
comment = struct();
title = struct();

%% set metaData
metaData.phylum     = '';
metaData.class      = '';
metaData.order      = '';
metaData.family     = '';
metaData.species    = '';
metaData.species_en = '';
metaData.T_typical  = 0; % K, body temperature
metaData.data_0     = {};
metaData.data_1     = {};

metaData.COMPLETE = 2.5; % using criteria of LikaKear2011

metaData.author   = {''};
% metaData.date_subm = [2026 01 01];
% metaData.email    = {''};
% metaData.address  = {''};

%% Group data included in this estimation run
$group_data

% Group data types mirrored into metaData.group_data_types
$group_data_types

% Struct with form tiers.tier_groups.(tier_name) = list_of_groups_of_tier
$tier_groups

%% Entity data included in this estimation run
$entity_data

% Entity data types mirrored into metaData.entity_data_types
$entity_data_types

% Cell array of entity ids for the current estimation tier
$entity_list

% Struct with form tiers.tier_entities.(tier_name) = list_of_entities_of_tier
$tier_entities

% Struct with form tiers.groups_of_entity.(entity_id) = list_of_groups_ids_entity_belongs_to
$groups_of_entity

% Struct with form tiers.tier_subtree.(entity_id).(tier_name) = list_of_entities_below
$tier_subtree

%% Tier parameters for the current estimation tier
% Cell array with tier parameters
$tier_pars

% Struct with form metaData.tier_par_init_values.(par).(entity_id) = value
$tier_par_init_values

%% Extra tier-specific information
% Use this area for custom helper variables that should travel with the
% generated mydata file. Keep any additions aligned with predict_<species>.m.
$extra_info

%% Set default weights and temperature metadata
weights = setweights(data, []);

metaData.data_fields = fieldnames(data);
temp = struct();
for i = 1:length(metaData.data_fields)
    field = metaData.data_fields{i};

    % Add typical temperature only to fields without specified temperature.
    if ~isfield(temp, field)
        temp.(field) = metaData.T_typical;
        units.temp.(field) = 'K';
        label.temp.(field) = 'temperature';
    end

    % Remove dummy variables from the objective function.
    if strcmp(label.(field), 'Dummy variable')
        weights.(field) = 0;
    end

    % Save data variable names in metaData for DEBtool.
    if length(data.(field)) > 1
        metaData.data_1{end+1} = field; % univariate
    else
        metaData.data_0{end+1} = field; % zero-variate
    end
end

%% Optional template-specific weight adjustments
% This generic baseline leaves observation weights unchanged apart from
% zeroing dummy variables above. Add any entity-level or group-level
% reweighting rules below when needed by your workflow.
%
% Example patterns:
% - rescale all time-series weights of a given data type
% - increase or decrease the contribution of grouped observations
% - reweight cumulative observations along the time axis

%% Optional pseudo-data for current-tier parameters
% Lower tiers commonly use inherited parameter values as pseudo-data.
for e = 1:length(tiers.entity_list)
    entity_id = tiers.entity_list{e};
    for p = 1:length(tiers.tier_pars)
        par_name = tiers.tier_pars{p};
        varname = [par_name '_' entity_id];

        data.psd.(varname) = metaData.tier_par_init_values.(par_name).(entity_id);
        units.psd.(varname) = '';
        label.psd.(varname) = '';
        weights.psd.(varname) = $pseudo_data_weight;
    end
end

%% Optional standard DEB pseudo-data
% Uncomment or adapt the next line if your workflow should include the
% standard DEB pseudo-data supplied by DEBtool in addition to the
% multitier-specific parameter pseudo-data above.
%
% [data, units, label, weights] = addpseudodata(data, units, label, weights);

%% pack auxData and txtData for output
auxData.temp = temp;
auxData.tiers = tiers;
auxData.init = init;
txtData.units = units;
txtData.label = label;
txtData.bibkey = bibkey;
txtData.comment = comment;
txtData.title = title;

%% Discussion points
D1 = '';
D2 = '';
metaData.discussion = struct('D1', D1, 'D2', D2);

%% Data Sources and References
% Add bibliography entries to metaData.biblist below when needed.

end
