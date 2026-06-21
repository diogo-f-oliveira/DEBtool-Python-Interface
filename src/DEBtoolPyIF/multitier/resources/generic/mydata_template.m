$function_header

$metadata_block

$typical_temperature_block

$completeness_level_block

%% Group data included in this estimation run
$group_data_block

% Group data types mirrored into metaData.group_data_types
$group_data_types

%% Entity data included in this estimation run
$entity_data_block

% Entity data types mirrored into metaData.entity_data_types
$entity_data_types

% Cell array of entity ids for the current estimation tier
$entity_list

% Struct with form tiers.tier_entities.(tier_name) = list_of_entities_of_tier
$tier_entities

% Struct with form tiers.tier_groups.(tier_name) = list_of_groups_of_tier
$tier_groups

% Struct with form tiers.groups_of_entity.(entity_id) = list_of_group_ids_entity_belongs_to
$groups_of_entity

% Struct with form tiers.entity_descendants.(entity_id).(tier_name) = list_of_descendant_entities
$entity_descendants

% Struct with form tiers.entity_path.(entity_id).(tier_name) = ancestor_or_self_id
$entity_path

%% Tier parameters for the current estimation tier
$tier_pars

% Struct with form metaData.tier_par_init_values.(par).(entity_id) = value
$tier_par_init_values

%% Extra tier-specific information
$extra_info

$weights_block

$save_fields_block

$remove_dummy_weights_block

$data_partition_block

%% Add generic pseudo-data
$add_pseudodata_block

%% Optional multitier pseudo-data
$multitier_pseudodata_block

%% Optional bibliography metadata
$bibkeys_block

%% Discussion points
$discussion_block

$packing_block
