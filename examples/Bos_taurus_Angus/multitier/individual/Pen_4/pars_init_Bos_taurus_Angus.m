function [par, metaPar, txtPar] = pars_init_Bos_taurus_Angus(metaData)

metaPar.model = 'stx'; 

%% reference parameter (not to be changed) 
par.T_ref = 293.15;   free.T_ref = 0;   units.T_ref = 'K';        label.T_ref = 'Reference temperature'; 

%% core primary parameters 
par.p_Am  = 2308.9050612470874;      free.p_Am   = 0;   units.p_Am = 'J/d.cm^2';  label.p_Am  = 'Surface-specific maximum assimilation rate';
par.kap_X = 0.22029769232546206;     free.kap_X  = 0;   units.kap_X = '-';        label.kap_X = 'digestion efficiency of food to reserve'; 
par.v = 0.35026158502519045;             free.v      = 0;   units.v = 'cm/d';         label.v = 'energy conductance'; 
par.kap = 0.9732603650127476;         free.kap    = 0;   units.kap = '-';          label.kap = 'allocation fraction to soma'; 
par.p_M = 25.584244825527605;         free.p_M    = 0;   units.p_M = 'J/d.cm^3';   label.p_M = '[p_M], vol-spec somatic maint'; 
par.E_G = 7834.906339035637;         free.E_G    = 0;   units.E_G = 'J/cm^3';     label.E_G = '[E_G], spec cost for structure'; 
par.E_Hb = 4545964.929101762;       free.E_Hb   = 0;   units.E_Hb = 'J';         label.E_Hb = 'maturity at birth'; 
par.E_Hx = 40024979.13168743;       free.E_Hx   = 0;   units.E_Hx = 'J';         label.E_Hx = 'maturity at weaning'; 
par.E_Hp = 63197525.47471765;       free.E_Hp   = 0;   units.E_Hp = 'J';         label.E_Hp = 'maturity at puberty'; 
par.h_a = 1.5698265143968423e-14;         free.h_a    = 0;   units.h_a = '1/d^2';      label.h_a = 'Weibull aging acceleration'; 
par.t_0 = 237.04630667634297;         free.t_0    = 0;   units.t_0 = 'd';          label.t_0 = 'time at start development'; 
par.del_M = 0.5475870793118289;     free.del_M  = 0;   units.del_M = '-';        label.del_M = 'shape coefficent';

%% Standard parameters
par.T_A = 8000;         free.T_A   = 0;   units.T_A = 'K';          label.T_A = 'Arrhenius temperature'; 
par.z = 13;             free.z     = 0;   units.z = '-';            label.z = 'zoom factor'; 
par.F_m = 6.5;          free.F_m   = 0;   units.F_m = 'l/d.cm^2';   label.F_m = '{F_m}, max spec searching rate'; 
par.kap_P = 0.1;        free.kap_P = 0;   units.kap_P = '-';        label.kap_P = 'faecation efficiency of food to faeces'; 
par.kap_R = 0.95;       free.kap_R = 0;   units.kap_R = '-';        label.kap_R = 'reproduction efficiency'; 
par.p_T = 0;            free.p_T   = 0;   units.p_T = 'J/d.cm^2';   label.p_T = '{p_T}, surf-spec somatic maint'; 
par.k_J = 0.002;        free.k_J   = 0;   units.k_J = '1/d';        label.k_J = 'maturity maint rate coefficient'; 
par.s_G = 0.1;          free.s_G   = 0;   units.s_G = '-';          label.s_G = 'Gompertz stress coefficient'; 

%% other parameters 
par.f = 1;              free.f      = 0;    units.f = '-';              label.f = 'scaled functional response for 0-var data'; 

%% set chemical parameters from Kooy2010 
[par, units, label, free] = addchem(par, units, label, free, metaData.phylum, metaData.class);

%% Set tier parameters
for e=1:length(metaData.entity_list)
    entity_id = metaData.entity_list{e};
    for p=1:length(metaData.tier_pars)
        par_name = metaData.tier_pars{p};
        varname = [par_name '_' entity_id];
        
        par.(varname) = metaData.tier_par_init_values.(par_name).(entity_id);
        free.(varname) = 1;
        units.(varname) = units.(par_name);
        label.(varname) = [label.(par_name) ' of diet ' entity_id];
    end
end

%% Pack output:
txtPar.units = units; txtPar.label = label; par.free = free; 

