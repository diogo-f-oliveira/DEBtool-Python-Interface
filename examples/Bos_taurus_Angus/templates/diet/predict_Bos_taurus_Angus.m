function [prdData, info] = predict_Bos_taurus_Angus(par, data, auxData)
info = 1;

%% compute temperature correction factors
TC = tempcorr(auxData.temp.tier_pars, par.T_ref, par.T_A);

%% Initialize group data
for g=1:length(auxData.tiers.tier_groups.individual)
    group_id = auxData.tiers.tier_groups.individual{g};
    
    tJX_grp_varname = ['tJX_grp_' group_id];
    if isfield(data, tJX_grp_varname)
        prdData.(tJX_grp_varname) = 0;
    end
end

%% Iterate for each tier entity (for each diet)
for e=1:length(auxData.tiers.entity_list)
    diet_id = auxData.tiers.entity_list{e};
    
    %% Set tier parameters (diet parameters)
    diet_pars = par;
    for p=1:length(auxData.tiers.tier_pars)
        diet_pars.(auxData.tiers.tier_pars{p}) = par.([auxData.tiers.tier_pars{p} '_' diet_id]);
    end
    
    %% Check validity of tier parameter set
    if ~filter_stx(diet_pars)
        prdData = []; info = 0; return
    end
    vars_pull(diet_pars);  vars_pull(parscomp_st(diet_pars));
        
    % Growth curve parameters
    rT_B = TC * p_M / 3 / (E_G + f * kap * p_Am / v);
    L_inf = f * L_m - L_T;
    % Food consumption parameters
    a_JX = f * w_X .* p_Am * TC / mu_X / kap_X;
    
    %% Iterate for each individual that belongs to the tier sample
    ind_list = auxData.tiers.tier_subtree.(diet_id).individual;
    for i=1:length(ind_list)
        ind_id = ind_list{i};
        
        %% Predict individual data
        % Weight predictions
        tW_varname = ['tW_' ind_id];
        if isfield(data, tW_varname) % Check if individual has weight data
            % Length at start of test
            L_init = nthroot(auxData.init.(tW_varname)*1e3 / (1 + f * ome),3);
            if L_init > L_inf  % Check for feasibility
                prdData = []; info = 0; return
            end
            % Time
            t = data.(tW_varname)(:,1);
            % Weight
            W = (1 + f * ome) * (L_inf - (L_inf - L_init) .* exp( - t * rT_B)).^3;
            prdData.(tW_varname) = W ./ 1e3; % to kg
        end
        
        %% Predict group data ind_id is part of
        for g=1:length(auxData.tiers.groups_of_entity.(ind_id))
            group_id = auxData.tiers.groups_of_entity.(ind_id){g};
            
            % Group feed consumption predictions
            tJX_grp_varname = ['tJX_grp_' group_id];
            if isfield(data, tJX_grp_varname)
                t = data.(tJX_grp_varname)(:,1);
                L_init = nthroot(auxData.init.(tJX_grp_varname).(ind_id)*1e3 / (1 + f * ome),3);
                if L_init > L_inf  % Check for feasibility
                    prdData = []; info = 0; return
                end
                % Food consumption during test
                L = (L_inf - (L_inf - L_init) .* exp( - t * rT_B));
                JX = a_JX * L.^2 ./ 1e3;
                prdData.(tJX_grp_varname) = prdData.(tJX_grp_varname) + JX;
            end
        end
    end
end

%% Set predictions for the dummy variables
prdData.entity_list = 10;
prdData.tier_entities = 10;
prdData.tier_groups = 10;
prdData.tier_subtree = 10;
prdData.groups_of_entity = 10;
prdData.tier_pars = 10;

end