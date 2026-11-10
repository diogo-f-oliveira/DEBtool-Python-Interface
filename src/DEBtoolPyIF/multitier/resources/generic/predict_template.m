function [prdData, info] = predict_template(par, data, auxData)
% Baseline generic multitier predict template for DEBtoolPyIF.
% Rename this file to predict_<species>.m and replace each TODO block with
% the biology and observation equations for your hierarchy.

prdData = struct();
info = 1;

%% Optional temperature correction or other global auxiliary calculations
% Example pattern:
% TC = tempcorr(auxData.temp.some_reference_field, par.T_ref, par.T_A);

%% The current tier and lower tiers are stored in descending order
tier_names = fieldnames(auxData.tiers.tier_entities);
current_tier_name = tier_names{1};
lower_tier_names = tier_names(2:end);

%% Initialize group data of the estimation tier
prdData = initialize_group_predictions(prdData, data, auxData.tiers, current_tier_name);

%% Loop through estimation entities
for e = 1:length(auxData.tiers.entity_list)
    entity_id = auxData.tiers.entity_list{e};

    %% Set tier parameters for the entity
    entity_pars = par;
    for p = 1:length(auxData.tiers.tier_pars)
        par_name = auxData.tiers.tier_pars{p};
        entity_pars.(par_name) = par.([par_name '_' entity_id]);
    end

    %% Check validity of the tier parameter set
    % Replace this block with the validity checks that make sense for your
    % DEB model and tier. If the parameterization is invalid or leads to an
    % infeasible state, set info = 0 and return.

    %% Predict entity data of the estimation tier
    % Use auxData.init and the current entity id to compute predictions for
    % the estimation-tier observations governed directly by entity_id.

    %% Predict group data of the estimation tier
    if isfield(auxData.tiers.groups_of_entity, entity_id)
        estimation_group_list = auxData.tiers.groups_of_entity.(entity_id);
    else
        estimation_group_list = {};
    end
    for g = 1:length(estimation_group_list)
        group_id = estimation_group_list{g};
    end

    %% Loop through each tier below
    for t = 1:length(lower_tier_names)
        lower_tier_name = lower_tier_names{t};

        %% Initialize group data of the lower tier
        prdData = initialize_group_predictions(prdData, data, auxData.tiers, lower_tier_name);

        if ~isfield(auxData.tiers.entity_descendants, entity_id)
            continue
        end
        if ~isfield(auxData.tiers.entity_descendants.(entity_id), lower_tier_name)
            continue
        end

        %% Loop through entity list of the tier below
        lower_entity_list = auxData.tiers.entity_descendants.(entity_id).(lower_tier_name);
        for le = 1:length(lower_entity_list)
            lower_entity_id = lower_entity_list{le};

            %% Predict entity data of the lower tier

            %% Predict group data of the lower tier
            if isfield(auxData.tiers.groups_of_entity, lower_entity_id)
                lower_group_list = auxData.tiers.groups_of_entity.(lower_entity_id);
            else
                lower_group_list = {};
            end
            for g = 1:length(lower_group_list)
                lower_group_id = lower_group_list{g};
            end
        end
    end
end

%% Set predictions for the dummy helper variables
prdData.entity_list = 10;
prdData.tier_entities = 10;
prdData.tier_groups = 10;
prdData.entity_descendants = 10;
prdData.entity_path = 10;
prdData.groups_of_entity = 10;
prdData.tier_pars = 10;

end

function prdData = initialize_group_predictions(prdData, data, tiers, tier_name)
% Initializes group predictions for one tier by preallocating zero-valued
% predictions for every data field associated with the relevant group ids.

if ~isfield(tiers, 'tier_groups') || ~isfield(tiers.tier_groups, tier_name)
    return
end

group_list = tiers.tier_groups.(tier_name);
data_fields = fieldnames(data);
for g = 1:length(group_list)
    group_id = group_list{g};
    suffix = ['_' group_id];
    for k = 1:length(data_fields)
        varname = data_fields{k};
        if strcmp(varname, 'psd')
            continue
        end
        if length(varname) > length(suffix) && strcmp(varname(end-length(suffix)+1:end), suffix)
            if ~isfield(prdData, varname)
                prdData.(varname) = zeros(size(data.(varname)));
            end
        end
    end
end
end
