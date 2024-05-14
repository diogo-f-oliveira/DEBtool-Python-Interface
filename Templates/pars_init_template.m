function [par, metaPar, txtPar] = pars_init_template(metaData)

metaPar.model = 'stx'; 

%% reference parameter (not to be changed) 
par.T_ref = 293.15;   free.T_ref = 0;   units.T_ref = 'K';        label.T_ref = 'Reference temperature'; 

%% core primary parameters 
par.p_Am  = $p_Am;      free.p_Am  = 0;   units.p_Am = 'J/d.cm^2';  label.p_Am  = 'Surface-specific maximum assimilation rate';
par.kap_X = $kap_X;     free.kap_X = 0;   units.kap_X = '-';        label.kap_X = 'digestion efficiency of food to reserve'; 
par.v = $v;             free.v     = 0;   units.v = 'cm/d';         label.v = 'energy conductance'; 
par.kap = $kap;         free.kap   = 0;   units.kap = '-';          label.kap = 'allocation fraction to soma'; 
par.p_M = $p_M;         free.p_M   = 0;   units.p_M = 'J/d.cm^3';   label.p_M = '[p_M], vol-spec somatic maint'; 
par.E_G = $E_G;         free.E_G   = 0;   units.E_G = 'J/cm^3';     label.E_G = '[E_G], spec cost for structure'; 
par.E_Hb = $E_Hb;       free.E_Hb  = 0;   units.E_Hb = 'J';         label.E_Hb = 'maturity at birth'; 
par.E_Hx = $E_Hx;       free.E_Hx  = 0;   units.E_Hx = 'J';         label.E_Hx = 'maturity at weaning'; 
par.E_Hp = $E_Hp;       free.E_Hp  = 0;   units.E_Hp = 'J';         label.E_Hp = 'maturity at puberty'; 
par.h_a = $h_a;         free.h_a   = 0;   units.h_a = '1/d^2';      label.h_a = 'Weibull aging acceleration'; 
par.t_0 = $t_0;         free.t_0   = 0;   units.t_0 = 'd';          label.t_0 = 'time at start development'; 
par.del_M = $del_M;     free.del_M = 0;   units.del_M = '-';        label.del_M = 'shape coefficent';
par.T_A = $T_A;         free.T_A   = 0;   units.T_A = 'K';          label.T_A = 'Arrhenius temperature'; 
par.z = $z;             free.z     = 0;   units.z = '-';            label.z = 'zoom factor'; 
par.F_m = $F_m;         free.F_m   = 0;   units.F_m = 'l/d.cm^2';   label.F_m = '{F_m}, max spec searching rate'; 
par.kap_R = $kap_R;     free.kap_R = 0;   units.kap_R = '-';        label.kap_R = 'reproduction efficiency'; 
par.kap_P = $kap_P;     free.kap_P = 0;   units.kap_P = '-';        label.kap_P = 'faecation efficiency of food to faeces'; 
par.p_T = $p_T;         free.p_T   = 0;   units.p_T = 'J/d.cm^2';   label.p_T = '{p_T}, surf-spec somatic maint'; 
par.k_J = $k_J;         free.k_J   = 0;   units.k_J = '1/d';        label.k_J = 'maturity maint rate coefficient'; 
par.s_G = $s_G;         free.s_G   = 0;   units.s_G = '-';          label.s_G = 'Gompertz stress coefficient'; 

%% other parameters 
par.f = 1;              free.f      = 0;    units.f = '-';              label.f = 'scaled functional response for 0-var data'; 

%% set chemical parameters from Kooy2010 
[par, units, label, free] = addchem(par, units, label, free, metaData.phylum, metaData.class);

%% Set tier parameters
for ts=1:length(metaData.tier_sample_list)
    tier_sample_id = metaData.tier_sample_list{ts};
    for p=1:length(metaData.tier_pars)
        par_name = metaData.tier_pars{p};
        varname = [par_name '_' tier_sample_id];
        
        par.(varname) = metaData.tier_par_init_values.(par_name).(tier_sample_id);
        free.(varname) = 1;
        units.(varname) = units.(par_name);
        label.(varname) = [label.(par_name) ' of diet-year ' tier_sample_id];
        
    end
end

%% Pack output:
txtPar.units = units; txtPar.label = label; par.free = free; 
