function [filter, flag] = filter_ruminant(p)
filter = 0; flag = 0; % default setting of filter and flag

% all pars must be positive
parvec = [p.p_Am; p.v; p.kap; p.p_M; p.E_G; p.k_J; p.E_Hb; p.E_Hx; p.E_Hp; p.kap_R; p.h_a; p.T_A; p.kap_X; p.kap_P; p.xi_C];
if sum(parvec <= 0) > 0 
    flag = 1;
    return;
elseif p.p_T < 0
    flag = 1;
    return;
end

% efficiencies must be lower than 1
parvec = [p.kap; p.kap_R; p.kap_X; p.kap_P; p.xi_C];
if sum(parvec >= 1) > 0
    flag = 2;
    return;
end

% maturity at birth, weaning, puberty must be in order
if p.E_Hb >= p.E_Hx || p.E_Hx >= p.E_Hp 
    flag = 4;
    return;
end

% growth efficiency lower than 1
w_V = [p.n_CV, p.n_HV, p.n_OV, p.n_NV] * [12; 1; 16; 14];
M_V = p.d_V/ w_V;            % mol/cm^3, [M_V], volume-specific mass of structure
kap_G = p.mu_V * M_V/ p.E_G;    % -, growth efficiency
if kap_G >= 1 
    flag = 3;
    return;
end

% constraint required for reaching puberty
L_m = p.kap * p.p_Am / p.p_M;
l_T = p.p_T / p.p_M;
if p.k_J * p.E_Hp >= (1-p.kap) * p.p_Am * L_m^2 * p.f * (p.f - l_T)^2
    flag = 5;
    return;
end
filter = 1;
end