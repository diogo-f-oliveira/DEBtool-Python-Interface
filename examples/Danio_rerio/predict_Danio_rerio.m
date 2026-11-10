function [prdData, info] = predict_Danio_rerio(par, data, auxData)
% Predictions for the Danio_rerio single-species example (std model).
% Adapted from the DEBtool predict_my_pet template. The datasets match the
% mock data defined in examples/Danio_rerio/data.py.

  % unpack par, data, auxData
  cPar = parscomp_st(par); vars_pull(par);
  vars_pull(cPar);  vars_pull(data);  vars_pull(auxData);

  % customized filters for the std model
  filterChecks = k * v_Hp >= f^3 || ...         % constraint required for reaching puberty with f
                 ~reach_birth(g, k, v_Hb, f);   % constraint required for reaching birth with f
  if filterChecks
    info = 0;
    prdData = {};
    return;
  end

  % temperature correction factors
  TC_ab = tempcorr(temp.ab, T_ref, T_A);
  TC_tp = tempcorr(temp.tp, T_ref, T_A);
  TC_am = tempcorr(temp.am, T_ref, T_A);
  TC_Ri = tempcorr(temp.Ri, T_ref, T_A);
  TC_tL = tempcorr(temp.tL, T_ref, T_A);

  %% zero-variate data

  % life cycle
  pars_tp = [g; k; l_T; v_Hb; v_Hp];
  [tau_p, tau_b, l_p, l_b, info] = get_tp(pars_tp, f);
  if ~info
    prdData = {};
    return;
  end

  % birth
  L_b = L_m * l_b;                  % cm, structural length at birth
  Lw_b = L_b / del_M;               % cm, physical length at birth
  Ww_b = L_b^3 * (1 + f * w);       % g, wet weight at birth
  aT_b = tau_b / k_M / TC_ab;       % d, age at birth

  % puberty
  L_p = L_m * l_p;                  % cm, structural length at puberty
  Lw_p = L_p / del_M;               % cm, physical length at puberty
  tT_p = (tau_p - tau_b) / k_M / TC_tp; % d, time since birth at puberty

  % ultimate
  l_i = f - l_T;                    % -, scaled ultimate length
  L_i = L_m * l_i;                  % cm, ultimate structural length
  Lw_i = L_i / del_M;               % cm, ultimate physical length
  Ww_i = L_i^3 * (1 + f * w);       % g, ultimate wet weight

  % reproduction
  pars_R = [kap; kap_R; g; k_J; k_M; L_T; v; U_Hb; U_Hp];
  RT_i = TC_Ri * reprod_rate(L_i, f, pars_R); % #/d, ultimate reproduction rate

  % life span
  pars_tm = [g; l_T; h_a / k_M^2; s_G];
  tau_m = get_tm_s(pars_tm, f, l_b);
  aT_m = tau_m / k_M / TC_am;       % d, mean life span

  prdData.ab = aT_b;
  prdData.tp = tT_p;
  prdData.am = aT_m;
  prdData.Lb = Lw_b;
  prdData.Lp = Lw_p;
  prdData.Li = Lw_i;
  prdData.Wwb = Ww_b;
  prdData.Wwi = Ww_i;
  prdData.Ri = RT_i;

  %% uni-variate data

  % time-length (von Bertalanffy growth from birth)
  rT_B = TC_tL * k_M / 3 / (1 + f / g);  % 1/d, von Bertalanffy growth rate
  ELw = Lw_i - (Lw_i - Lw_b) * exp(-rT_B * tL(:,1)); % cm, physical length

  % length-weight
  EWw = (LW(:,1) * del_M).^3 * (1 + f * w); % g, wet weight

  prdData.tL = ELw;
  prdData.LW = EWw;
end
