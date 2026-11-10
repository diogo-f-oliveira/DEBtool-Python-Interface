function [prdData, info] = predict_Bos_taurus_Angus(par, data, auxData)
info = 1;

%% compute temperature correction factors
TC = tempcorr(auxData.temp.tier_pars, par.T_ref, par.T_A);

%% Building female parameter set
female_pars = par;
female_pars.p_Am = par.p_Am_f;
female_pars.E_Hp = par.E_Hp_f;

if ~filter_stx(female_pars)
    prdData = []; info = 0; return
end
vars_pull(female_pars); vars_pull(parscomp_st(female_pars));


%% Predictions for data on females

% stage transitions
pars_txf = [g k l_T v_Hb v_Hx v_Hp];
[t_pf, t_xf, t_bf, l_pf, l_xf, l_bf, info] = get_tx(pars_txf, f);
if ~info
    prdData = []; info = 0; return
end

% Predictions
L_bf = L_m * l_bf;                   % cm, structural length at birth at f
L_xf = L_m * l_xf;
L_pf = L_m * l_pf;
L_if = (f - l_T) * L_m;

aT_bf = t_0 + t_bf/ k_M/ TC;            % d, age at birth for females
tT_xf = (t_xf - t_bf)/ k_M/ TC;         % d, time since birth at weaning for females
tT_pf = (t_pf - t_bf)/ k_M/ TC;         % d, time since birth at puberty for females
Wwb_f = L_bf^3 * (1 + f * ome);         % g, wet weight at birth at f
Wwx_f = L_xf^3 * (1 + f * ome);         % g, wet weight at weaning at f
Wwp_f = L_pf^3 * (1 + f * ome);         % g, wet weight at puberty at f
Wwi_f = L_if^3 * (1 + f * ome);         % g, ultimate wet weight at f
Lhi_f = L_if / del_M;                   % cm, ultimate withers height at f

% Reproduction rate
Lb = l_bf * L_m; Lp = l_pf * L_m; % volumetric length at birth, puberty
UE0 = Lb^3 * (f + g)/ v * (1 + 3 * l_bf/ 4/ f); % d.cm^2, scaled cost per foetus
SC = f * L_m.^3 .* (g ./ L_m + (1 + L_T ./ L_m)/ L_m)/ (f + g);
SR = (1 - kap) * SC - k_J * E_Hp / p_Am;
RT_i = TC * kap_R .* SR/ UE0; % set reprod rate of juveniles to zero

% life span
pars_tm = [g; k; v_Hb; v_Hx; v_Hp; h_a; s_G];  % compose parameter vector at T_ref
t_m = get_tm_mod('stx', pars_tm, f);           % -, scaled mean life span at T_ref
aT_f = t_m/ k_M/ TC;                           % d, mean life span at T

%% Males
% Check validity of tier parameter set
if ~filter_stx(par)
    prdData = []; info = 0; return
end
% Set structure nitrogen equal to reserve nitrogen
vars_pull(par);  vars_pull(parscomp_st(par));

% stage transitions
pars_txf = [g k l_T v_Hb v_Hx v_Hp];
[t_pm, t_xm, t_bm, l_pm, l_xm, l_bm, info] = get_tx(pars_txf, f);
if ~info
    prdData = []; info = 0; return
end

% Predictions
L_bm = L_m * l_bm;                   % cm, structural length at birth at f
L_xm = L_m * l_xm;
L_pm = L_m * l_pm;
L_im = (f - l_T) * L_m;

aT_bm = t_0 + t_bm/ k_M/ TC;            % d, age at birth for females
tT_xm = (t_xm - t_bm)/ k_M/ TC;           % d, time since birth at weaning for males
tT_pm = (t_pm - t_bm)/ k_M/ TC;           % d, time since birth at puberty for males
Wwb_m = L_bm^3 * (1 + f * ome);         % g, wet weight at birth at f
Wwx_m = L_xm^3 * (1 + f * ome);         % g, wet weight at weaning at f
Wwp_m = L_pm^3 * (1 + f * ome);         % g, wet weight at puberty at f
Wwi_m = L_im^3 * (1 + f * ome);         % g, ultimate wet weight at f
Lhi_m = L_im / del_M;

% life span
pars_tm = [g; k; v_Hb; v_Hx; v_Hp; h_a; s_G];  % compose parameter vector at T_ref
t_m = get_tm_mod('stx', pars_tm, f);           % -, scaled mean life span at T_ref
aT_m = t_m/ k_M/ TC;                           % d, mean life span at T

%% Loop through each diet and make predictions
diet_list = auxData.tiers.entity_descendants.male.diet;
for i=1:length(diet_list)
    diet_id = diet_list{i};
    % Digestibility
    DMD_varname = ['DMD_' diet_id];
    if isfield(data, DMD_varname)
        prdData.(DMD_varname) = (w_X - w_P * y_P_E / y_X_E) / w_X;
    end
end

%% Initialize group data
for j=1:length(auxData.tiers.tier_groups.individual)
    group_id = auxData.tiers.tier_groups.individual{j};
    
    tJX_grp_varname = ['tJX_grp_' group_id];
    if isfield(data, tJX_grp_varname)
        prdData.(tJX_grp_varname) = 0;
    end
end

% Growth curve parameters
rT_B = TC * p_M / 3 / (E_G + f * kap * p_Am / v);
L_inf = f * L_m - L_T;
% Food consumption parameters
a_JX = f * w_X .* p_Am * TC / mu_X / kap_X;

%% Loop through each individual and compute predictions
ind_list = auxData.tiers.entity_descendants.male.individual;
for i=1:length(ind_list)
    ind_id = ind_list{i};
    
    %% Predict individual data
    % Weight predictions
    tW_varname = ['tW_' ind_id];
    if isfield(data, tW_varname)
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
    for j=1:length(auxData.tiers.groups_of_entity.(ind_id))
        group_id = auxData.tiers.groups_of_entity.(ind_id){j};
        
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

%% Set predictions for the dummy variables
prdData.entity_list = 10;
prdData.tier_entities = 10;
prdData.tier_groups = 10;
prdData.entity_descendants = 10;
prdData.entity_path = 10;
prdData.groups_of_entity = 10;
prdData.tier_pars = 10;

%% pack to output

% % Zero-variate data
% Females
prdData.Wwb_f = Wwb_f;
prdData.tx_f = tT_xf;
prdData.Wwx_f = Wwx_f;
prdData.tp_f = tT_pf;
prdData.Wwp_f = Wwp_f;
prdData.Wwi_f = Wwi_f;
prdData.Lhi_f = Lhi_f;
prdData.Ri = RT_i;

% Males
prdData.Wwb_m = Wwb_m;
prdData.tx_m = tT_xm;
prdData.Wwx_m = Wwx_m;
prdData.tp_m = tT_pm;
prdData.Wwp_m = Wwp_m;
prdData.Wwi_m = Wwi_m;
prdData.Lhi_m = Lhi_m;

% Common data
prdData.ab = 0.5*(aT_bf + aT_bm);     % equal for males and females
prdData.am = 0.5*(aT_f + aT_m);

end
