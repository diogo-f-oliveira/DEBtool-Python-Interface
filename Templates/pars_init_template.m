function [par, metaPar, txtPar] = pars_init_template(metaData)
% Baseline generic multitier pars_init template for DEBtoolPyIF.
% Rename this file to pars_init_<species>.m and adapt the parameter set,
% free-parameter flags, and model-specific constants for your workflow.

metaPar.model = 'stx';

%% reference parameter (not to be changed)
par.T_ref = 293.15;   free.T_ref = 0;   units.T_ref = 'K';        label.T_ref = 'Reference temperature';

%% core primary parameters
par.T_A   = $T_A;       free.T_A   = 0;   units.T_A = 'K';          label.T_A   = 'Arrhenius temperature';
par.z     = $z;         free.z     = 0;   units.z = '-';            label.z     = 'zoom factor';
par.F_m   = $F_m;       free.F_m   = 0;   units.F_m = 'l/d.cm^2';   label.F_m   = '{F_m}, max spec searching rate';
par.kap_X = $kap_X;     free.kap_X = 0;   units.kap_X = '-';        label.kap_X = 'digestion efficiency of food to reserve';
par.kap_P = $kap_P;     free.kap_P = 0;   units.kap_P = '-';        label.kap_P = 'faecation efficiency of food to faeces';
par.v     = $v;         free.v     = 0;   units.v = 'cm/d';         label.v     = 'energy conductance';
par.kap   = $kap;       free.kap   = 0;   units.kap = '-';          label.kap   = 'allocation fraction to soma';
par.p_M   = $p_M;       free.p_M   = 0;   units.p_M = 'J/d.cm^3';   label.p_M   = '[p_M], vol-spec somatic maint';
par.p_T   = $p_T;       free.p_T   = 0;   units.p_T = 'J/d.cm^2';   label.p_T   = '{p_T}, surf-spec somatic maint';
par.k_J   = $k_J;       free.k_J   = 0;   units.k_J = '1/d';        label.k_J   = 'maturity maint rate coefficient';
par.E_G   = $E_G;       free.E_G   = 0;   units.E_G = 'J/cm^3';     label.E_G   = '[E_G], spec cost for structure';
par.E_Hb  = $E_Hb;      free.E_Hb  = 0;   units.E_Hb = 'J';         label.E_Hb  = 'maturity at birth';
par.E_Hp  = $E_Hp;      free.E_Hp  = 0;   units.E_Hp = 'J';         label.E_Hp  = 'maturity at puberty';
par.kap_R = $kap_R;     free.kap_R = 0;   units.kap_R = '-';        label.kap_R = 'reproduction efficiency';
par.h_a   = $h_a;       free.h_a   = 0;   units.h_a = '1/d^2';      label.h_a   = 'Weibull aging acceleration';
par.s_G   = $s_G;       free.s_G   = 0;   units.s_G = '-';          label.s_G   = 'Gompertz stress coefficient';

%% other parameters
par.f = 1;              free.f = 0;       units.f = '-';            label.f = 'scaled functional response for 0-var data';

%% set chemical parameters from Kooy2010
[par, units, label, free] = addchem(par, units, label, free, metaData.phylum, metaData.class);

%% Set tier parameters for the current estimation entities
% This is where inherited initial values become free entity-specific
% parameters such as par.p_Am_<entity_id>.
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
