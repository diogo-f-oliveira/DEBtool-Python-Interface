$function_header

$metadata_block

$typical_temperature_block

$completeness_level_block

$author_info_block

%% Group data
$group_data_block

% group data types
$group_data_types

% Struct with form tier_groups.(tier_name) = list_of_groups_of_tier
$tier_groups

%% Entity data
$entity_data_block

% entity data types
$entity_data_types

% Cell array of entity_ids
$entity_list

% Struct with form tier_entities.(tier_name) = list_of_entities_of_tier
$tier_entities

% Struct with form groups_of_entity.(entity_id) = list_of_groups_ids_entity_belongs_to
$groups_of_entity
    
% Tier subtree
% Lists entities that are below entity_id for each tier below
% Struct with form entity_descendants.(entity_id).(tier_name) = list_of_entities_below
$entity_descendants

% Struct with form entity_path.(entity_id).(tier_name) = ancestor_or_self_id
$entity_path

%% Tier parameters
% Cell array with tier parameters
$tier_pars

% Initial values for each tier parameter and entity
% Struct with form tier_par_init_values.(par).(entity_id) = value;
$tier_par_init_values

$weights_block

$save_fields_block

$save_fields_by_variate_type_block

temp = struct();
$set_temperature_equal_to_typical_block

$remove_dummy_weights_block

%% Set weight of individual data
cumulative_data_types = {'tW'};
ind_data_weights = struct('tW', 1/10);

for dt=1:length(metaData.entity_data_types)
    data_type = metaData.entity_data_types{dt};
    cumulative = strcmp(data_type, cumulative_data_types);
    for i=1:length(tiers.tier_entities.individual)
        ind_id = tiers.tier_entities.individual{i};
        data_varname = [data_type '_' ind_id];
        if isfield(data, data_varname)
            weights.(data_varname) = weights.(data_varname) * ind_data_weights.(data_type);
            if cumulative
                % Set weights to start at zero and linearly increase, keeping the same sum
                n_dt = length(weights.(data_varname));
                sum_w = sum(weights.(data_varname));
                weights.(data_varname) = sum_w * (0:n_dt-1)' / sum(0:n_dt-1);
            end
        end
    end
end

%% Set weight of group data
group_data_weights = struct('tJX_grp', 5/10);

for dt=1:length(metaData.group_data_types)
    data_type = metaData.group_data_types{dt};
    for g=1:length(tiers.tier_groups.individual)
        g_id = tiers.tier_groups.individual{g};
        data_varname = [data_type '_' g_id];
    
        if isfield(data, data_varname)
            n_inds_in_data = length(fieldnames(init.(data_varname)));
            weights.(data_varname) = weights.(data_varname) * group_data_weights.(data_type) * n_inds_in_data;
        end
    end
end

%% Set generic and multitier pseudo-data
$add_pseudodata_block
$multitier_pseudodata_block

%% Data Sources and References
%

$packing_block


