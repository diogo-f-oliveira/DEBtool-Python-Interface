function [data, auxData, metaData, txtData, weights] = mydata_Bos_taurus_Angus

%% set metaData
metaData.phylum     = 'Chordata';
metaData.class      = 'Mammalia';
metaData.order      = 'Artiodactyla';
metaData.family     = 'Bovidae';
metaData.species    = 'Bos_taurus_Angus';
metaData.species_en = 'Angus cattle';
metaData.T_typical  = C2K(38.6);
metaData.data_0     = {};
metaData.data_1     = {};

metaData.COMPLETE = 2.5; % using criteria of LikaKear2011

metaData.author   = {'Diogo Oliveira', 'Goncalo Marques'};
% metaData.date_subm = [2024 02 02];
% metaData.email    = {''};
% metaData.address  = {''};

%% Group data
%% Time vs Group daily feed consumption data

data.tJX_grp_Pen_5 = [0 50.54; 1 49.18; 2 54.16; 3 50.4; 4 44.68; 5 46.69; 6 54.78; 7 52.23; 8 49.56; 9 52.82; 10 51.15; 11 36.73; 12 46.9; 13 40.68; 14 40.71; 15 43.31; 16 50.74; 17 43.98; 18 44.84; 19 50.21; 20 51.84; 21 33.68; 22 45.75; 23 43.31; 24 41.66; 25 50.81; 26 46.53; 27 47.02; 28 50.54; 29 42.52; 30 28.06; 31 41.5; 32 39.5; 33 41.42; 34 38.32; 35 40.07; 36 40.48; 37 37.73; 38 38.55; 39 43.31; 40 41.5; 41 46.63; 42 43.37; 43 51.62; 44 37.83; 45 49.38; 46 45.57; 47 49.42; 48 40.54; 49 43.49; 50 39.56; 51 43.29; 52 43.23; 53 47.51; 54 45.82; 55 45.82; 56 52.58; 57 51.76; 58 43.07; 59 53.37; 60 53.68; 61 53.68; 62 52.31; 63 52.31; 64 56.4; 65 50.15; 66 56.28; 67 54.39; 68 55.59; 69 49.16; 70 49.16; 71 55.49; 72 57.54; 73 55.22; 74 53.57; 75 52.54; 76 56.79; 77 48.34; 78 49.64; 79 42.56; 80 48.77; 81 42.09; 82 48.34; 83 48.34];
init.tJX_grp_Pen_5 = struct('PT033634130', 453, 'PT233843883', 506, 'PT333653651', 536, 'PT533358890', 477, 'PT724523831', 485); units.init.tJX_grp_Pen_5 = 'kg'; label.init.tJX_grp_Pen_5 = 'Initial weights for the individuals in the group';
units.tJX_grp_Pen_5 = {'d', 'kg'}; label.tJX_grp_Pen_5 = {'Time since start', 'Daily food consumption of group during test'}; title.tJX_grp_Pen_5 = 'Daily feed consumption of pen Pen_5'; comment.tJX_grp_Pen_5 = 'Data from GreenBeef trial 1, pen Pen_5'; bibkey.tJX_grp_Pen_5 = 'GreenBeefTrial1';



% group data types
metaData.group_data_types = {'tJX_grp'}; 


% Cell array of group_ids
data.group_list = 10; units.group_list = '-'; label.group_list = 'Dummy variable'; comment.group_list = 'List of group ids'; bibkey.group_list = '-'; 
tiers.group_list = {'Pen_5'}; units.tiers.group_list = '-'; label.tiers.group_list = 'List of groups ids'; 


%% Individual data
%% Time vs Weight data 

data.tW_PT533358890 = [0 477; 14 493; 21 498; 35 529; 50 551; 63 586; 83 621];
init.tW_PT533358890 = 477; units.init.tW_PT533358890 = 'kg'; label.init.tW_PT533358890 = 'Initial weight';
units.tW_PT533358890 = {'d', 'kg'}; label.tW_PT533358890 = {'Time since start', 'Wet weight'}; title.tW_PT533358890 = 'Growth curve of individual PT533358890'; comment.tW_PT533358890 = 'Data from GreenBeef trial 1, individual PT533358890'; bibkey.tW_PT533358890 = 'GreenBeefTrial1';

data.tW_PT333653651 = [0 536; 14 548; 21 561; 35 589; 50 603; 63 615; 83 632];
init.tW_PT333653651 = 536; units.init.tW_PT333653651 = 'kg'; label.init.tW_PT333653651 = 'Initial weight';
units.tW_PT333653651 = {'d', 'kg'}; label.tW_PT333653651 = {'Time since start', 'Wet weight'}; title.tW_PT333653651 = 'Growth curve of individual PT333653651'; comment.tW_PT333653651 = 'Data from GreenBeef trial 1, individual PT333653651'; bibkey.tW_PT333653651 = 'GreenBeefTrial1';

data.tW_PT233843883 = [0 506; 14 525; 21 533; 35 561; 50 583; 63 592; 83 620];
init.tW_PT233843883 = 506; units.init.tW_PT233843883 = 'kg'; label.init.tW_PT233843883 = 'Initial weight';
units.tW_PT233843883 = {'d', 'kg'}; label.tW_PT233843883 = {'Time since start', 'Wet weight'}; title.tW_PT233843883 = 'Growth curve of individual PT233843883'; comment.tW_PT233843883 = 'Data from GreenBeef trial 1, individual PT233843883'; bibkey.tW_PT233843883 = 'GreenBeefTrial1';

data.tW_PT724523831 = [0 485; 14 505; 21 510; 35 474; 50 504; 63 581; 83 565];
init.tW_PT724523831 = 485; units.init.tW_PT724523831 = 'kg'; label.init.tW_PT724523831 = 'Initial weight';
units.tW_PT724523831 = {'d', 'kg'}; label.tW_PT724523831 = {'Time since start', 'Wet weight'}; title.tW_PT724523831 = 'Growth curve of individual PT724523831'; comment.tW_PT724523831 = 'Data from GreenBeef trial 1, individual PT724523831'; bibkey.tW_PT724523831 = 'GreenBeefTrial1';

data.tW_PT033634130 = [0 453; 14 468; 21 471; 35 500; 50 517; 63 526; 83 556];
init.tW_PT033634130 = 453; units.init.tW_PT033634130 = 'kg'; label.init.tW_PT033634130 = 'Initial weight';
units.tW_PT033634130 = {'d', 'kg'}; label.tW_PT033634130 = {'Time since start', 'Wet weight'}; title.tW_PT033634130 = 'Growth curve of individual PT033634130'; comment.tW_PT033634130 = 'Data from GreenBeef trial 1, individual PT033634130'; bibkey.tW_PT033634130 = 'GreenBeefTrial1';



% individual data types
metaData.ind_data_types = {'tW'}; 


% Cell array of ind_ids
data.ind_list = 10; units.ind_list = '-'; label.ind_list = 'Dummy variable'; comment.ind_list = 'List of individuals'; bibkey.ind_list = '-'; 
tiers.ind_list = {'PT533358890', 'PT333653651', 'PT233843883', 'PT724523831', 'PT033634130'}; units.tiers.ind_list = '-'; label.tiers.ind_list = 'List of individuals'; 
metaData.ind_list = tiers.ind_list; % Save in metaData to use in pars_init.m

% Struct with form groups_of_ind.(ind_id) = list_of_groups_ids_ind_belongs_to
data.groups_of_ind = 10; units.groups_of_ind = '-'; label.groups_of_ind = 'Dummy variable'; comment.groups_of_ind = 'Groups of individuals'; bibkey.groups_of_ind = '-'; 
tiers.groups_of_ind = struct('PT533358890', {{'Pen_5'}}, 'PT333653651', {{'Pen_5'}}, 'PT233843883', {{'Pen_5'}}, 'PT724523831', {{'Pen_5'}}, 'PT033634130', {{'Pen_5'}}); units.tiers.groups_of_ind = '-'; label.tiers.groups_of_ind = 'Groups of individuals'; 


% Cell array of tier_sample_ids
data.tier_sample_list = 10; units.tier_sample_list = '-'; label.tier_sample_list = 'Dummy variable'; comment.tier_sample_list = 'Tier sample list'; bibkey.tier_sample_list = '-'; 
tiers.tier_sample_list = {'PT033634130', 'PT233843883', 'PT333653651', 'PT533358890', 'PT724523831'}; units.tiers.tier_sample_list = '-'; label.tiers.tier_sample_list = 'Tier sample list'; 
metaData.tier_sample_list = tiers.tier_sample_list; % Save in metaData to use in pars_init.m

% Struct with form 
% tier_sample_inds.(tier_sample_id) = list_of_inds_in_tier_sample
data.tier_sample_inds = 10; units.tier_sample_inds = '-'; label.tier_sample_inds = 'Dummy variable'; comment.tier_sample_inds = 'List of individuals that belong to the name sample'; bibkey.tier_sample_inds = '-'; 
tiers.tier_sample_inds = struct('PT033634130', {{'PT033634130'}}, 'PT233843883', {{'PT233843883'}}, 'PT333653651', {{'PT333653651'}}, 'PT533358890', {{'PT533358890'}}, 'PT724523831', {{'PT724523831'}}); units.tiers.tier_sample_inds = '-'; label.tiers.tier_sample_inds = 'List of individuals that belong to the name sample'; 


%% Tier parameters
% Cell array with tier parameters
data.tier_pars = 10; units.tier_pars = '-'; label.tier_pars = 'Dummy variable'; comment.tier_pars = 'Tier parameters'; bibkey.tier_pars = '-'; 
tiers.tier_pars = {'p_Am', 'kap_X'}; units.tiers.tier_pars = '-'; label.tiers.tier_pars = 'Tier parameters'; 
metaData.tier_pars = tiers.tier_pars; % Save in metaData to use in pars_init.m

% Initial values for each tier parameter and sample
% Struct with form tier_par_init_values.(par).(tier_sample_id) = value;
metaData.tier_par_init_values = struct('p_Am', struct('PT033634130', 4545.209098166135, 'PT233843883', 4545.209098166135, 'PT333653651', 4545.209098166135, 'PT533358890', 4545.209098166135, 'PT724523831', 4545.209098166135), 'kap_X', struct('PT033634130', 0.22337822221306397, 'PT233843883', 0.22337822221306397, 'PT333653651', 0.22337822221306397, 'PT533358890', 0.22337822221306397, 'PT724523831', 0.22337822221306397)); 


%% Set temperature data and remove weights for dummy variables
weights = setweights(data, []);

metaData.data_fields = fieldnames(data);
temp = struct();
for i = 1:length(metaData.data_fields)
    % Add typical temperature only to fields without specified temperature
    field = metaData.data_fields{i};
    if ~isfield(temp, field)
        temp.(field) = metaData.T_typical;
        units.temp.(field) = 'K';
        label.temp.(field) = 'temperature';
    end
    % Removing weight from dummy variables
    if strcmp(label.(field), 'Dummy variable')
        weights.(field) = 0;
    end
    % Saving data variable names in metaData
    if length(data.(field)) > 1
        metaData.data_1{end+1} = field; % univariate
    else
        metaData.data_0{end+1} = field; % zero-variate
    end
end

%% Set weight of individual data
cumulative_data_types = {'tW'};
ind_data_weights = struct('tW', 1/5);

for dt=1:length(metaData.ind_data_types)
    data_type = metaData.ind_data_types{dt};
    cumulative = strcmp(data_type, cumulative_data_types);
    for i=1:length(tiers.ind_list)
        ind_id = tiers.ind_list{i};
        data_varname = [data_type '_' ind_id];
        if isfield(data, data_varname)
            weights.(data_varname) = weights.(data_varname) * ind_data_weights.(data_type);
            if cumulative
                % Set weights to start at zero and linearly increase, keeping the same sum
                n_dt = length(weights.(data_varname));
                sum_w = sum(weights.(data_varname));
                weights.(data_varname) = sum_w * (0:n_dt-1)' / sum(0:n_dt-1);
            end
        end
    end
end


%% Set weight of group data
group_data_weights = struct('tJX_grp', 1);
for dt=1:length(metaData.group_data_types)
    data_type = metaData.group_data_types{dt};
    for g=1:length(tiers.group_list)
        g_id = tiers.group_list{g};
        data_varname = [data_type '_' g_id];
    
        if isfield(data, data_varname)
            n_inds_in_data = length(fieldnames(init.(data_varname)));
            weights.(data_varname) = weights.(data_varname) * group_data_weights.(data_type) * n_inds_in_data;
        end
    end
end


%% Set pseudo-data for tier parameters
for ts=1:length(tiers.tier_sample_list)
    tier_sample_id = tiers.tier_sample_list{ts};
    for p=1:length(tiers.tier_pars)
        par_name = tiers.tier_pars{p};
        varname = [par_name '_' tier_sample_id];
        
        data.psd.(varname) = metaData.tier_par_init_values.(par_name).(tier_sample_id);
        units.psd.(varname) = '';
        label.psd.(varname) = '';
        weights.psd.(varname) = 0.1;
    end
end
    
%% pack auxData and txtData for output
auxData.temp = temp;
auxData.tiers = tiers;
auxData.init = init;
txtData.units = units;
txtData.label = label;
txtData.bibkey = bibkey;
txtData.comment = comment;
txtData.title = title;

%% Discussion points
D1 = '';
D2 = '';
metaData.discussion = struct('D1', D1, 'D2', D2);

%% Data Sources and References


