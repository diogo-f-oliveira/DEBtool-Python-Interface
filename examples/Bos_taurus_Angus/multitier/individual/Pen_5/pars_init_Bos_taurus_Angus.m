function [par, metaPar, txtPar] = pars_init_Bos_taurus_Angus(metaData)

metaPar.model = 'std';

%% reference parameter and model parameters

par.T_ref = 293.15; free.T_ref = 0; units.T_ref = 'K'; label.T_ref = 'Reference temperature';

par.p_Am = 2226.029807275121; free.p_Am = 1; units.p_Am = 'J/d.cm^2'; label.p_Am = 'Surface-specific maximum assimilation rate';
par.kap_X = 0.2423996666348881; free.kap_X = 1; units.kap_X = '-'; label.kap_X = 'digestion efficiency of food to reserve';
par.kap_P = 0.2637431695359602; free.kap_P = 0; units.kap_P = '-'; label.kap_P = 'faecation efficiency of food to faeces';
par.p_M = 25.761267471883635; free.p_M = 0; units.p_M = 'J/d.cm^3'; label.p_M = '[p_M], vol-spec somatic maint';
par.v = 0.3466243911621958; free.v = 0; units.v = 'cm/d'; label.v = 'energy conductance';
par.kap = 0.973616231490763; free.kap = 0; units.kap = '-'; label.kap = 'allocation fraction to soma';
par.E_G = 7834.345055677742; free.E_G = 0; units.E_G = 'J/cm^3'; label.E_G = '[E_G], spec cost for structure';
par.E_Hb = 4449409.214183612; free.E_Hb = 0; units.E_Hb = 'J'; label.E_Hb = 'maturity at birth';
par.E_Hx = 39424099.299462885; free.E_Hx = 0; units.E_Hx = 'J'; label.E_Hx = 'maturity at weaning';
par.E_Hp = 62291935.10907419; free.E_Hp = 0; units.E_Hp = 'J'; label.E_Hp = 'maturity at puberty';
par.h_a = 1.8052417123165e-14; free.h_a = 0; units.h_a = '1/d^2'; label.h_a = 'Weibull aging acceleration';
par.t_0 = 236.39543022686271; free.t_0 = 0; units.t_0 = 'd'; label.t_0 = 'time at start development';
par.del_M = 0.5464475534029014; free.del_M = 0; units.del_M = '-'; label.del_M = 'shape coefficent';
par.p_Am_f = 1919.721921416438; free.p_Am_f = 0; units.p_Am_f = 'J/d.cm^2'; label.p_Am_f = 'Surface-specific maximum assimilation rate for females';
par.E_Hp_f = 52997551.70972361; free.E_Hp_f = 0; units.E_Hp_f = 'J'; label.E_Hp_f = 'maturity at puberty for females';
par.T_A = 8000; free.T_A = 0; units.T_A = 'K'; label.T_A = 'Arrhenius temperature';
par.z = 13; free.z = 0; units.z = '-'; label.z = 'zoom factor';
par.F_m = 6.5; free.F_m = 0; units.F_m = 'l/d.cm^2'; label.F_m = '{F_m}, max spec searching rate';
par.kap_R = 0.95; free.kap_R = 0; units.kap_R = '-'; label.kap_R = 'reproduction efficiency';
par.p_T = 0; free.p_T = 0; units.p_T = 'J/d.cm^2'; label.p_T = '{p_T}, surf-spec somatic maint';
par.k_J = 0.002; free.k_J = 0; units.k_J = '1/d'; label.k_J = 'maturity maint rate coefficient';
par.s_G = 0.1; free.s_G = 0; units.s_G = '-'; label.s_G = 'Gompertz stress coefficient';
par.f = 1; free.f = 0; units.f = '-'; label.f = 'scaled functional response for 0-var data';

%% set chemical parameters from Kooy2010
[par, units, label, free] = addchem(par, units, label, free, metaData.phylum, metaData.class);

%% Set tier parameters
for p = 1:length(metaData.tier_pars)
    parName = metaData.tier_pars{p};
    free.(parName) = 0;
    for e = 1:length(metaData.entity_list)
        entity_id = metaData.entity_list{e};
        varName = [parName '_' entity_id];

        par.(varName) = metaData.tier_par_init_values.(parName).(entity_id);
        free.(varName) = 1;
        units.(varName) = units.(parName);
        label.(varName) = [label.(parName) ' for tier entity ' entity_id];
    end
end

%% Pack output
txtPar.units = units;
txtPar.label = label;
par.free = free;

end