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

data.tJX_grp_Pen_2 = [0 45.43; 1 43.88; 2 26.68; 3 46.87; 4 40.24; 5 41.11; 6 41.15; 7 44.57; 8 45.67; 9 47.08; 10 41.6; 11 33.54; 12 47.22; 13 40.4; 14 38.04; 15 40.91; 16 36.2; 17 38.47; 18 38.95; 19 38.89; 20 40.95; 21 30.58; 22 37.61; 23 48.26; 24 41.03; 25 44.06; 26 43.23; 27 47.73; 28 41.82; 29 43.78; 30 29.79; 31 37.26; 32 29.83; 33 39.34; 34 45.31; 35 36.18; 36 44.02; 37 41.3; 38 43.11; 39 49.12; 40 42.88; 41 41.72; 42 45.65; 43 45.49; 44 44.04; 45 47.26; 46 45.33; 47 49.18; 48 46.08; 49 45.88; 50 47.81; 51 48.36; 52 50.03; 53 51.46; 54 44.68; 55 44.68; 56 39.02; 57 41.58; 58 48.02; 59 42.64; 60 48.65; 61 48.65; 62 45.12; 63 45.12; 64 48.69; 65 55.53; 66 48.89; 67 50.85; 68 54.41; 69 43.74; 70 43.74; 71 53.53; 72 56.51; 73 52.39; 74 54.31; 75 48.46; 76 56.28; 77 57.18; 78 55.06; 79 51.8; 80 59.42; 81 53.68; 82 56.02; 83 56.02];
init.tJX_grp_Pen_2 = struct('PT424401157', 469, 'PT433843806', 507, 'PT624139868', 464, 'PT833653644', 548, 'PT933843912', 545); units.init.tJX_grp_Pen_2 = 'kg'; label.init.tJX_grp_Pen_2 = 'Initial weights for the individuals in the group';
units.tJX_grp_Pen_2 = {'d', 'kg'}; label.tJX_grp_Pen_2 = {'Time since start', 'Daily food consumption of group during test'}; title.tJX_grp_Pen_2 = 'Daily feed consumption of pen Pen_2'; comment.tJX_grp_Pen_2 = 'Data from GreenBeef trial 1, pen Pen_2'; bibkey.tJX_grp_Pen_2 = 'GreenBeefTrial1';



% group data types
metaData.group_data_types = {'tJX_grp'}; 


% Cell array of group_ids
data.group_list = 10; units.group_list = '-'; label.group_list = 'Dummy variable'; comment.group_list = 'List of group ids'; bibkey.group_list = '-'; 
tiers.group_list = {'Pen_2'}; units.tiers.group_list = '-'; label.tiers.group_list = 'List of groups ids'; 


%% Individual data
%% Time vs Weight data 

data.tW_PT424401157 = [0 469; 14 482; 21 486; 35 512; 50 540; 63 549; 83 571];
init.tW_PT424401157 = 469; units.init.tW_PT424401157 = 'kg'; label.init.tW_PT424401157 = 'Initial weight';
units.tW_PT424401157 = {'d', 'kg'}; label.tW_PT424401157 = {'Time since start', 'Wet weight'}; title.tW_PT424401157 = 'Growth curve of individual PT424401157'; comment.tW_PT424401157 = 'Data from GreenBeef trial 1, individual PT424401157'; bibkey.tW_PT424401157 = 'GreenBeefTrial1';

data.tW_PT933843912 = [0 545; 14 561; 21 565; 35 581; 50 616; 63 649; 83 668];
init.tW_PT933843912 = 545; units.init.tW_PT933843912 = 'kg'; label.init.tW_PT933843912 = 'Initial weight';
units.tW_PT933843912 = {'d', 'kg'}; label.tW_PT933843912 = {'Time since start', 'Wet weight'}; title.tW_PT933843912 = 'Growth curve of individual PT933843912'; comment.tW_PT933843912 = 'Data from GreenBeef trial 1, individual PT933843912'; bibkey.tW_PT933843912 = 'GreenBeefTrial1';

data.tW_PT433843806 = [0 507; 14 532; 21 532; 35 568; 50 600; 63 607; 83 628];
init.tW_PT433843806 = 507; units.init.tW_PT433843806 = 'kg'; label.init.tW_PT433843806 = 'Initial weight';
units.tW_PT433843806 = {'d', 'kg'}; label.tW_PT433843806 = {'Time since start', 'Wet weight'}; title.tW_PT433843806 = 'Growth curve of individual PT433843806'; comment.tW_PT433843806 = 'Data from GreenBeef trial 1, individual PT433843806'; bibkey.tW_PT433843806 = 'GreenBeefTrial1';

data.tW_PT833653644 = [0 548; 14 544; 21 553; 35 579; 50 603; 63 623; 83 652];
init.tW_PT833653644 = 548; units.init.tW_PT833653644 = 'kg'; label.init.tW_PT833653644 = 'Initial weight';
units.tW_PT833653644 = {'d', 'kg'}; label.tW_PT833653644 = {'Time since start', 'Wet weight'}; title.tW_PT833653644 = 'Growth curve of individual PT833653644'; comment.tW_PT833653644 = 'Data from GreenBeef trial 1, individual PT833653644'; bibkey.tW_PT833653644 = 'GreenBeefTrial1';

data.tW_PT624139868 = [0 464; 14 470; 21 480; 35 508; 50 542; 63 558; 83 582];
init.tW_PT624139868 = 464; units.init.tW_PT624139868 = 'kg'; label.init.tW_PT624139868 = 'Initial weight';
units.tW_PT624139868 = {'d', 'kg'}; label.tW_PT624139868 = {'Time since start', 'Wet weight'}; title.tW_PT624139868 = 'Growth curve of individual PT624139868'; comment.tW_PT624139868 = 'Data from GreenBeef trial 1, individual PT624139868'; bibkey.tW_PT624139868 = 'GreenBeefTrial1';



% individual data types
metaData.ind_data_types = {'tW'}; 


% Cell array of ind_ids
data.ind_list = 10; units.ind_list = '-'; label.ind_list = 'Dummy variable'; comment.ind_list = 'List of individuals'; bibkey.ind_list = '-'; 
tiers.ind_list = {'PT424401157', 'PT933843912', 'PT433843806', 'PT833653644', 'PT624139868'}; units.tiers.ind_list = '-'; label.tiers.ind_list = 'List of individuals'; 
metaData.ind_list = tiers.ind_list; % Save in metaData to use in pars_init.m

% Struct with form groups_of_ind.(ind_id) = list_of_groups_ids_ind_belongs_to
data.groups_of_ind = 10; units.groups_of_ind = '-'; label.groups_of_ind = 'Dummy variable'; comment.groups_of_ind = 'Groups of individuals'; bibkey.groups_of_ind = '-'; 
tiers.groups_of_ind = struct('PT424401157', {{'Pen_2'}}, 'PT933843912', {{'Pen_2'}}, 'PT433843806', {{'Pen_2'}}, 'PT833653644', {{'Pen_2'}}, 'PT624139868', {{'Pen_2'}}); units.tiers.groups_of_ind = '-'; label.tiers.groups_of_ind = 'Groups of individuals'; 


% Cell array of tier_sample_ids
data.tier_sample_list = 10; units.tier_sample_list = '-'; label.tier_sample_list = 'Dummy variable'; comment.tier_sample_list = 'Tier sample list'; bibkey.tier_sample_list = '-'; 
tiers.tier_sample_list = {'PT424401157', 'PT433843806', 'PT624139868', 'PT833653644', 'PT933843912'}; units.tiers.tier_sample_list = '-'; label.tiers.tier_sample_list = 'Tier sample list'; 
metaData.tier_sample_list = tiers.tier_sample_list; % Save in metaData to use in pars_init.m

% Struct with form 
% tier_sample_inds.(tier_sample_id) = list_of_inds_in_tier_sample
data.tier_sample_inds = 10; units.tier_sample_inds = '-'; label.tier_sample_inds = 'Dummy variable'; comment.tier_sample_inds = 'List of individuals that belong to the name sample'; bibkey.tier_sample_inds = '-'; 
tiers.tier_sample_inds = struct('PT424401157', {{'PT424401157'}}, 'PT433843806', {{'PT433843806'}}, 'PT624139868', {{'PT624139868'}}, 'PT833653644', {{'PT833653644'}}, 'PT933843912', {{'PT933843912'}}); units.tiers.tier_sample_inds = '-'; label.tiers.tier_sample_inds = 'List of individuals that belong to the name sample'; 


%% Tier parameters
% Cell array with tier parameters
data.tier_pars = 10; units.tier_pars = '-'; label.tier_pars = 'Dummy variable'; comment.tier_pars = 'Tier parameters'; bibkey.tier_pars = '-'; 
tiers.tier_pars = {'p_Am', 'kap_X'}; units.tiers.tier_pars = '-'; label.tiers.tier_pars = 'Tier parameters'; 
metaData.tier_pars = tiers.tier_pars; % Save in metaData to use in pars_init.m

% Initial values for each tier parameter and sample
% Struct with form tier_par_init_values.(par).(tier_sample_id) = value;
metaData.tier_par_init_values = struct('p_Am', struct('PT424401157', 4545.209098166135, 'PT433843806', 4545.209098166135, 'PT624139868', 4545.209098166135, 'PT833653644', 4545.209098166135, 'PT933843912', 4545.209098166135), 'kap_X', struct('PT424401157', 0.22337822221306397, 'PT433843806', 0.22337822221306397, 'PT624139868', 0.22337822221306397, 'PT833653644', 0.22337822221306397, 'PT933843912', 0.22337822221306397)); 


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


