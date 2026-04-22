function [par, metaPar, txtPar] = pars_init_Bos_taurus_Angus(metaData)

metaPar.model = 'std';

%% reference parameter and model parameters

par.T_ref = 293.15; free.T_ref = 0; units.T_ref = 'K'; label.T_ref = 'Reference temperature';
par.p_Am = 5000; free.p_Am = 1; units.p_Am = 'J/d.cm^2'; label.p_Am = 'Surface-specific maximum assimilation rate';
par.kap_X = 0.2; free.kap_X = 1; units.kap_X = '-'; label.kap_X = 'digestion efficiency of food to reserve';
par.kap_P = 0.1; free.kap_P = 1; units.kap_P = '-'; label.kap_P = 'faecation efficiency of food to faeces';
par.p_M = 80; free.p_M = 1; units.p_M = 'J/d.cm^3'; label.p_M = '[p_M], vol-spec somatic maint';
par.v = 0.05; free.v = 1; units.v = 'cm/d'; label.v = 'energy conductance';
par.kap = 0.97; free.kap = 1; units.kap = '-'; label.kap = 'allocation fraction to soma';
par.E_G = 7800; free.E_G = 1; units.E_G = 'J/cm^3'; label.E_G = '[E_G], spec cost for structure';
par.E_Hb = 2000000.0; free.E_Hb = 1; units.E_Hb = 'J'; label.E_Hb = 'maturity at birth';
par.E_Hx = 20000000.0; free.E_Hx = 1; units.E_Hx = 'J'; label.E_Hx = 'maturity at weaning';
par.E_Hp = 60000000.0; free.E_Hp = 1; units.E_Hp = 'J'; label.E_Hp = 'maturity at puberty';
par.h_a = 5e-10; free.h_a = 1; units.h_a = '1/d^2'; label.h_a = 'Weibull aging acceleration';
par.t_0 = 80; free.t_0 = 1; units.t_0 = 'd'; label.t_0 = 'time at start development';
par.del_M = 0.15; free.del_M = 1; units.del_M = '-'; label.del_M = 'shape coefficent';
par.p_Am_f = 4500; free.p_Am_f = 1; units.p_Am_f = 'J/d.cm^2'; label.p_Am_f = 'Surface-specific maximum assimilation rate for females';
par.E_Hp_f = 60000000.0; free.E_Hp_f = 1; units.E_Hp_f = 'J'; label.E_Hp_f = 'maturity at puberty for females';
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
for e = 1:length(metaData.entity_list)
    entity_id = metaData.entity_list{e};
    for p = 1:length(metaData.tier_pars)
        par_name = metaData.tier_pars{p};
        varname = [par_name '_' entity_id];

        par.(varname) = metaData.tier_par_init_values.(par_name).(entity_id);
        free.(varname) = 1;
        units.(varname) = units.(par_name);
        label.(varname) = [label.(par_name) ' for tier entity ' entity_id];
    end
end

%% Pack output
txtPar.units = units;
txtPar.label = label;
par.free = free;

end