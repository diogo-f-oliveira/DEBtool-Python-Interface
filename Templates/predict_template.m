function [prdData, info] = predict_template(par, data, auxData)

info = 1;

%% compute temperature correction factors
TC = tempcorr(auxData.temp.tier_pars, par.T_ref, par.T_A);

%% Iterate for each tier sample
for ts=1:length(auxData.tiers.tier_sample_list)
    tier_sample_id = auxData.tiers.tier_sample_list{ts};
        
    %% Set tier parameters
    tier_pars = par;
    for p=1:length(auxData.tiers.tier_pars)
        tier_pars.(auxData.tiers.tier_pars{p}) = par.([auxData.tiers.tier_pars{p} '_' tier_sample_id]);
    end
    
    %% Check validity of tier parameter set
    if ~filter_stx(tier_pars)
        prdData = []; info = 0; return
    end
    vars_pull(tier_pars);  vars_pull(parscomp_st(tier_pars));
    
    %% Predict group data
    % code
    
    sample_inds = auxData.tiers.tier_sample_inds.(tier_sample_id);
    for i=1:length(sample_inds)
        ind_id = auxData.tiers.ind_list{i};
        
        %% Predict individual data
        % code
        
        %% Predict group data ind_id is part of
        for g=1:length(auxData.tiers.groups_of_ind(ind_id))
            group_id = auxData.tiers.groups_of_ind(ind_id){g};
            
            % code
        end
    end
end

%% Set predictions for the dummy variables
prdData.group_data = 10;
prdData.individual_data = 10;
prdData.ind_list = 10;
prdData.groups_of_ind = 10;
prdData.tier_sample_list = 10;
prdData.tier_sample_inds = 10;
prdData.tier_pars = 10;


end