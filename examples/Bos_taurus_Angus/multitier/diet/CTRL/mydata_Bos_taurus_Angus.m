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

data.tJX_grp_Pen_3 = [0 44.62; 1 44.22; 2 49.87; 3 51.94; 4 50.32; 5 48.06; 6 50.56; 7 43.44; 8 44.01; 9 44.13; 10 45.3; 11 46.98; 12 46.89; 13 48.1; 14 43.96; 15 44.82; 16 49.82; 17 49.13; 18 49.63; 19 46.79; 20 57.49; 21 45.73; 22 45.38; 23 53.4; 24 47.63; 25 53.92; 26 48.62; 27 43.62; 28 51.38; 29 46.98; 30 45.08; 31 52.75; 32 49.09; 33 46.85; 34 47.37; 35 54.65; 36 45.94; 37 47.15; 38 49.74; 39 52.24; 40 50.86; 41 53.62; 42 53.62; 43 56.46; 44 54.56; 45 53.27; 46 54.22; 47 56.37; 48 57.15; 49 52.06; 50 55.25; 51 62.5; 52 62.06; 53 56.63; 54 57.67; 55 57.67; 56 57.58; 57 56.2; 58 55.34; 59 55.17; 60 59.48; 61 59.48; 62 64.91; 63 64.91; 64 50.94; 65 51.89; 66 53.96; 67 60.25; 68 49.69; 69 52.41; 70 52.41; 71 55.43; 72 62.32; 73 56.12; 74 56.29; 75 56.37; 76 57.15; 77 58.44; 78 55.6; 79 52.06; 80 56.72; 81 55.25; 82 55.99; 83 55.99];
init.tJX_grp_Pen_3 = struct('PT333842562', 515, 'PT524401180', 496, 'PT533987885', 436, 'PT833653649', 535, 'PT933843894', 508); units.init.tJX_grp_Pen_3 = 'kg'; label.init.tJX_grp_Pen_3 = 'Initial weights for the individuals in the group';
units.tJX_grp_Pen_3 = {'d', 'kg'}; label.tJX_grp_Pen_3 = {'Time since start', 'Daily food consumption of group during test'}; title.tJX_grp_Pen_3 = 'Daily feed consumption of pen Pen_3'; comment.tJX_grp_Pen_3 = 'Data from GreenBeef trial 1, pen Pen_3'; bibkey.tJX_grp_Pen_3 = 'GreenBeefTrial1';

data.tJX_grp_Pen_4 = [0 45.31; 1 46.38; 2 50.99; 3 50.73; 4 49.98; 5 53.4; 6 48.49; 7 48.1; 8 50.04; 9 49.82; 10 47.02; 11 45.17; 12 49.82; 13 47.07; 14 46.72; 15 45.43; 16 47.58; 17 46.2; 18 48.43; 19 43.6; 20 57.75; 21 51.5; 22 50.64; 23 60.38; 24 51.42; 25 56.16; 26 54.31; 27 55.86; 28 53.79; 29 49.39; 30 49.22; 31 55.94; 32 53.4; 33 52.88; 34 47.28; 35 56.2; 36 58.18; 37 54.39; 38 53.7; 39 61.2; 40 56.03; 41 54.22; 42 53.36; 43 54.65; 44 47.93; 45 50.25; 46 51.98; 47 54.74; 48 55.86; 49 53.36; 50 54.65; 51 62.84; 52 66.72; 53 57.88; 54 56.72; 55 56.72; 56 55.17; 57 58.44; 58 55.34; 59 56.63; 60 65.77; 61 65.77; 62 54.82; 63 54.82; 64 60.08; 65 55.51; 66 65.08; 67 60.86; 68 58.92; 69 60.94; 70 60.94; 71 52.32; 72 52.24; 73 52.06; 74 50.08; 75 54.82; 76 57.58; 77 56.81; 78 58.27; 79 59.39; 80 56.37; 81 62.93; 82 59.74; 83 59.74];
init.tJX_grp_Pen_4 = struct('PT224401177', 562, 'PT524956505', 542, 'PT533843896', 480, 'PT924401183', 510, 'PT933602927', 426); units.init.tJX_grp_Pen_4 = 'kg'; label.init.tJX_grp_Pen_4 = 'Initial weights for the individuals in the group';
units.tJX_grp_Pen_4 = {'d', 'kg'}; label.tJX_grp_Pen_4 = {'Time since start', 'Daily food consumption of group during test'}; title.tJX_grp_Pen_4 = 'Daily feed consumption of pen Pen_4'; comment.tJX_grp_Pen_4 = 'Data from GreenBeef trial 1, pen Pen_4'; bibkey.tJX_grp_Pen_4 = 'GreenBeefTrial1';



% group data types
metaData.group_data_types = {'tJX_grp'}; 


% Cell array of group_ids
data.group_list = 10; units.group_list = '-'; label.group_list = 'Dummy variable'; comment.group_list = 'List of group ids'; bibkey.group_list = '-'; 
tiers.group_list = {'Pen_3', 'Pen_4'}; units.tiers.group_list = '-'; label.tiers.group_list = 'List of groups ids'; 


%% Individual data
%% Time vs Weight data 

data.tW_PT533843896 = [0 480; 14 492; 21 506; 35 536; 50 551; 63 574; 83 586];
init.tW_PT533843896 = 480; units.init.tW_PT533843896 = 'kg'; label.init.tW_PT533843896 = 'Initial weight';
units.tW_PT533843896 = {'d', 'kg'}; label.tW_PT533843896 = {'Time since start', 'Wet weight'}; title.tW_PT533843896 = 'Growth curve of individual PT533843896'; comment.tW_PT533843896 = 'Data from GreenBeef trial 1, individual PT533843896'; bibkey.tW_PT533843896 = 'GreenBeefTrial1';

data.tW_PT924401183 = [0 510; 14 543; 21 555; 35 587; 50 624; 63 648; 83 685];
init.tW_PT924401183 = 510; units.init.tW_PT924401183 = 'kg'; label.init.tW_PT924401183 = 'Initial weight';
units.tW_PT924401183 = {'d', 'kg'}; label.tW_PT924401183 = {'Time since start', 'Wet weight'}; title.tW_PT924401183 = 'Growth curve of individual PT924401183'; comment.tW_PT924401183 = 'Data from GreenBeef trial 1, individual PT924401183'; bibkey.tW_PT924401183 = 'GreenBeefTrial1';

data.tW_PT933602927 = [0 426; 14 450; 21 462; 35 482; 50 497; 63 524; 83 539];
init.tW_PT933602927 = 426; units.init.tW_PT933602927 = 'kg'; label.init.tW_PT933602927 = 'Initial weight';
units.tW_PT933602927 = {'d', 'kg'}; label.tW_PT933602927 = {'Time since start', 'Wet weight'}; title.tW_PT933602927 = 'Growth curve of individual PT933602927'; comment.tW_PT933602927 = 'Data from GreenBeef trial 1, individual PT933602927'; bibkey.tW_PT933602927 = 'GreenBeefTrial1';

data.tW_PT333842562 = [0 515; 14 535; 21 539; 35 566; 50 594; 63 630; 83 652];
init.tW_PT333842562 = 515; units.init.tW_PT333842562 = 'kg'; label.init.tW_PT333842562 = 'Initial weight';
units.tW_PT333842562 = {'d', 'kg'}; label.tW_PT333842562 = {'Time since start', 'Wet weight'}; title.tW_PT333842562 = 'Growth curve of individual PT333842562'; comment.tW_PT333842562 = 'Data from GreenBeef trial 1, individual PT333842562'; bibkey.tW_PT333842562 = 'GreenBeefTrial1';

data.tW_PT524401180 = [0 496; 14 503; 21 508; 35 532; 50 560; 63 586; 83 610];
init.tW_PT524401180 = 496; units.init.tW_PT524401180 = 'kg'; label.init.tW_PT524401180 = 'Initial weight';
units.tW_PT524401180 = {'d', 'kg'}; label.tW_PT524401180 = {'Time since start', 'Wet weight'}; title.tW_PT524401180 = 'Growth curve of individual PT524401180'; comment.tW_PT524401180 = 'Data from GreenBeef trial 1, individual PT524401180'; bibkey.tW_PT524401180 = 'GreenBeefTrial1';

data.tW_PT833653649 = [0 535; 14 546; 21 557; 35 586; 50 613; 63 641; 83 656];
init.tW_PT833653649 = 535; units.init.tW_PT833653649 = 'kg'; label.init.tW_PT833653649 = 'Initial weight';
units.tW_PT833653649 = {'d', 'kg'}; label.tW_PT833653649 = {'Time since start', 'Wet weight'}; title.tW_PT833653649 = 'Growth curve of individual PT833653649'; comment.tW_PT833653649 = 'Data from GreenBeef trial 1, individual PT833653649'; bibkey.tW_PT833653649 = 'GreenBeefTrial1';

data.tW_PT524956505 = [0 542; 14 567; 21 577; 35 603; 50 638; 63 664; 83 707];
init.tW_PT524956505 = 542; units.init.tW_PT524956505 = 'kg'; label.init.tW_PT524956505 = 'Initial weight';
units.tW_PT524956505 = {'d', 'kg'}; label.tW_PT524956505 = {'Time since start', 'Wet weight'}; title.tW_PT524956505 = 'Growth curve of individual PT524956505'; comment.tW_PT524956505 = 'Data from GreenBeef trial 1, individual PT524956505'; bibkey.tW_PT524956505 = 'GreenBeefTrial1';

data.tW_PT933843894 = [0 508; 14 521; 21 534; 35 563; 50 583; 63 610; 83 639];
init.tW_PT933843894 = 508; units.init.tW_PT933843894 = 'kg'; label.init.tW_PT933843894 = 'Initial weight';
units.tW_PT933843894 = {'d', 'kg'}; label.tW_PT933843894 = {'Time since start', 'Wet weight'}; title.tW_PT933843894 = 'Growth curve of individual PT933843894'; comment.tW_PT933843894 = 'Data from GreenBeef trial 1, individual PT933843894'; bibkey.tW_PT933843894 = 'GreenBeefTrial1';

data.tW_PT224401177 = [0 562; 14 589; 21 597; 35 632; 50 660; 63 697; 83 723];
init.tW_PT224401177 = 562; units.init.tW_PT224401177 = 'kg'; label.init.tW_PT224401177 = 'Initial weight';
units.tW_PT224401177 = {'d', 'kg'}; label.tW_PT224401177 = {'Time since start', 'Wet weight'}; title.tW_PT224401177 = 'Growth curve of individual PT224401177'; comment.tW_PT224401177 = 'Data from GreenBeef trial 1, individual PT224401177'; bibkey.tW_PT224401177 = 'GreenBeefTrial1';

data.tW_PT533987885 = [0 436; 14 449; 21 460; 35 486; 50 502; 63 515; 83 542];
init.tW_PT533987885 = 436; units.init.tW_PT533987885 = 'kg'; label.init.tW_PT533987885 = 'Initial weight';
units.tW_PT533987885 = {'d', 'kg'}; label.tW_PT533987885 = {'Time since start', 'Wet weight'}; title.tW_PT533987885 = 'Growth curve of individual PT533987885'; comment.tW_PT533987885 = 'Data from GreenBeef trial 1, individual PT533987885'; bibkey.tW_PT533987885 = 'GreenBeefTrial1';



% individual data types
metaData.ind_data_types = {'tW'}; 


% Cell array of ind_ids
data.ind_list = 10; units.ind_list = '-'; label.ind_list = 'Dummy variable'; comment.ind_list = 'List of individuals'; bibkey.ind_list = '-'; 
tiers.ind_list = {'PT533843896', 'PT924401183', 'PT933602927', 'PT333842562', 'PT524401180', 'PT833653649', 'PT524956505', 'PT933843894', 'PT224401177', 'PT533987885'}; units.tiers.ind_list = '-'; label.tiers.ind_list = 'List of individuals'; 
metaData.ind_list = tiers.ind_list; % Save in metaData to use in pars_init.m

% Struct with form groups_of_ind.(ind_id) = list_of_groups_ids_ind_belongs_to
data.groups_of_ind = 10; units.groups_of_ind = '-'; label.groups_of_ind = 'Dummy variable'; comment.groups_of_ind = 'Groups of individuals'; bibkey.groups_of_ind = '-'; 
tiers.groups_of_ind = struct('PT533843896', {{'Pen_4'}}, 'PT924401183', {{'Pen_4'}}, 'PT933602927', {{'Pen_4'}}, 'PT333842562', {{'Pen_3'}}, 'PT524401180', {{'Pen_3'}}, 'PT833653649', {{'Pen_3'}}, 'PT524956505', {{'Pen_4'}}, 'PT933843894', {{'Pen_3'}}, 'PT224401177', {{'Pen_4'}}, 'PT533987885', {{'Pen_3'}}); units.tiers.groups_of_ind = '-'; label.tiers.groups_of_ind = 'Groups of individuals'; 


% Cell array of tier_sample_ids
data.tier_sample_list = 10; units.tier_sample_list = '-'; label.tier_sample_list = 'Dummy variable'; comment.tier_sample_list = 'Tier sample list'; bibkey.tier_sample_list = '-'; 
tiers.tier_sample_list = {'CTRL'}; units.tiers.tier_sample_list = '-'; label.tiers.tier_sample_list = 'Tier sample list'; 
metaData.tier_sample_list = tiers.tier_sample_list; % Save in metaData to use in pars_init.m

% Struct with form
% tier_sample_inds.(tier_sample_id) = list_of_inds_in_tier_sample
data.tier_sample_inds = 10; units.tier_sample_inds = '-'; label.tier_sample_inds = 'Dummy variable'; comment.tier_sample_inds = 'List of individuals that belong to the name sample'; bibkey.tier_sample_inds = '-'; 
tiers.tier_sample_inds = struct('CTRL', {{'PT533843896', 'PT924401183', 'PT933602927', 'PT333842562', 'PT524401180', 'PT833653649', 'PT524956505', 'PT933843894', 'PT224401177', 'PT533987885'}}); units.tiers.tier_sample_inds = '-'; label.tiers.tier_sample_inds = 'List of individuals that belong to the name sample'; 


%% Tier parameters
% Cell array with tier parameters
data.tier_pars = 10; units.tier_pars = '-'; label.tier_pars = 'Dummy variable'; comment.tier_pars = 'Tier parameters'; bibkey.tier_pars = '-'; 
tiers.tier_pars = {'p_Am', 'kap_X'}; units.tiers.tier_pars = '-'; label.tiers.tier_pars = 'Tier parameters'; 
metaData.tier_pars = tiers.tier_pars; % Save in metaData to use in pars_init.m

% Initial values for each tier parameter and sample
% Struct with form tier_par_init_values.(par).(tier_sample_id) = value;
metaData.tier_par_init_values = struct('p_Am', struct('CTRL', 4351.3793160766545), 'kap_X', struct('CTRL', 0.20210654757522778)); 



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
ind_data_weights = struct('tW', 1/10);

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
group_data_weights = struct('tJX_grp', 5/10);
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



