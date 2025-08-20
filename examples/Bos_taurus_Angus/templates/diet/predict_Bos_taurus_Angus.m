function [prdData, info] = predict_Bos_taurus_Angus(par, data, auxData)
info = 1;

%% compute temperature correction factors
TC = tempcorr(auxData.temp.tier_pars, par.T_ref, par.T_A);

%% Initialize group data
for g=1:length(auxData.tiers.group_list)
    group_id = auxData.tiers.group_list{g};
    
    tJX_grp_varname = ['tJX_grp_' group_id];
    if isfield(data, tJX_grp_varname)
        prdData.(tJX_grp_varname) = 0;
    end
end

%% Iterate for each tier sample (for each diet)
for ts=1:length(auxData.tiers.tier_sample_list)
    tier_sample_id = auxData.tiers.tier_sample_list{ts};
    
    %% Set tier parameters (diet parameters)
    tier_pars = par;
    for p=1:length(auxData.tiers.tier_pars)
        tier_pars.(auxData.tiers.tier_pars{p}) = par.([auxData.tiers.tier_pars{p} '_' tier_sample_id]);
    end
    
    %% Check validity of tier parameter set
    if ~filter_stx(tier_pars)
        prdData = []; info = 0; return
    end
    vars_pull(tier_pars);  vars_pull(parscomp_st(tier_pars));
        
    % Growth curve parameters
    rT_B = TC * p_M / 3 / (E_G + f * kap * p_Am / v);
    L_inf = f * L_m - L_T;
    % Food consumption parameters
    a_JX = f * w_X .* p_Am * TC / mu_X / kap_X;
    
    %% Iterate for each individual that belongs to the tier sample
    sample_inds = auxData.tiers.tier_sample_inds.(tier_sample_id);
    for i=1:length(sample_inds)
        ind_id = sample_inds{i};
        
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
        for g=1:length(auxData.tiers.groups_of_ind.(ind_id))
            group_id = auxData.tiers.groups_of_ind.(ind_id){g};
            
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
prdData.group_list = 10;
prdData.ind_list = 10;
prdData.groups_of_ind = 10;
prdData.tier_sample_list = 10;
prdData.tier_sample_inds = 10;
prdData.tier_pars = 10;

end