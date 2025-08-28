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

data.tJX_grp_Pen_5 = [0 50.54; 1 49.18; 2 54.16; 3 50.4; 4 44.68; 5 46.69; 6 54.78; 7 52.23; 8 49.56; 9 52.82; 10 51.15; 11 36.73; 12 46.9; 13 40.68; 14 40.71; 15 43.31; 16 50.74; 17 43.98; 18 44.84; 19 50.21; 20 51.84; 21 33.68; 22 45.75; 23 43.31; 24 41.66; 25 50.81; 26 46.53; 27 47.02; 28 50.54; 29 42.52; 30 28.06; 31 41.5; 32 39.5; 33 41.42; 34 38.32; 35 40.07; 36 40.48; 37 37.73; 38 38.55; 39 43.31; 40 41.5; 41 46.63; 42 43.37; 43 51.62; 44 37.83; 45 49.38; 46 45.57; 47 49.42; 48 40.54; 49 43.49; 50 39.56; 51 43.29; 52 43.23; 53 47.51; 54 45.82; 55 45.82; 56 52.58; 57 51.76; 58 43.07; 59 53.37; 60 53.68; 61 53.68; 62 52.31; 63 52.31; 64 56.4; 65 50.15; 66 56.28; 67 54.39; 68 55.59; 69 49.16; 70 49.16; 71 55.49; 72 57.54; 73 55.22; 74 53.57; 75 52.54; 76 56.79; 77 48.34; 78 49.64; 79 42.56; 80 48.77; 81 42.09; 82 48.34; 83 48.34];
init.tJX_grp_Pen_5 = struct('PT033634130', 453, 'PT233843883', 506, 'PT333653651', 536, 'PT533358890', 477, 'PT724523831', 485); units.init.tJX_grp_Pen_5 = 'kg'; label.init.tJX_grp_Pen_5 = 'Initial weights for the individuals in the group';
units.tJX_grp_Pen_5 = {'d', 'kg'}; label.tJX_grp_Pen_5 = {'Time since start', 'Daily food consumption of group during test'}; title.tJX_grp_Pen_5 = 'Daily feed consumption of pen Pen_5'; comment.tJX_grp_Pen_5 = 'Data from GreenBeef trial 1, pen Pen_5'; bibkey.tJX_grp_Pen_5 = 'GreenBeefTrial1';



% group data types
metaData.group_data_types = {'tJX_grp'}; 


% Struct with form tier_groups.(tier_name) = list_of_groups_of_tier
data.tier_groups = 10; units.tier_groups = '-'; label.tier_groups = 'Dummy variable'; 
tiers.tier_groups = struct('diet', {{}}, 'individual', {{'Pen_2', 'Pen_5'}}); units.tiers.tier_groups = '-'; label.tiers.tier_groups = 'List of groups ids for each tier'; 


%% Entity data
%% Time vs Weight data 

data.tW_PT424401157 = [0 469; 14 482; 21 486; 35 512; 50 540; 63 549; 83 571];
init.tW_PT424401157 = 469; units.init.tW_PT424401157 = 'kg'; label.init.tW_PT424401157 = 'Initial weight';
units.tW_PT424401157 = {'d', 'kg'}; label.tW_PT424401157 = {'Time since start', 'Wet weight'}; title.tW_PT424401157 = 'Growth curve of individual PT424401157'; comment.tW_PT424401157 = 'Data from GreenBeef trial 1, individual PT424401157'; bibkey.tW_PT424401157 = 'GreenBeefTrial1';

data.tW_PT624139868 = [0 464; 14 470; 21 480; 35 508; 50 542; 63 558; 83 582];
init.tW_PT624139868 = 464; units.init.tW_PT624139868 = 'kg'; label.init.tW_PT624139868 = 'Initial weight';
units.tW_PT624139868 = {'d', 'kg'}; label.tW_PT624139868 = {'Time since start', 'Wet weight'}; title.tW_PT624139868 = 'Growth curve of individual PT624139868'; comment.tW_PT624139868 = 'Data from GreenBeef trial 1, individual PT624139868'; bibkey.tW_PT624139868 = 'GreenBeefTrial1';

data.tW_PT433843806 = [0 507; 14 532; 21 532; 35 568; 50 600; 63 607; 83 628];
init.tW_PT433843806 = 507; units.init.tW_PT433843806 = 'kg'; label.init.tW_PT433843806 = 'Initial weight';
units.tW_PT433843806 = {'d', 'kg'}; label.tW_PT433843806 = {'Time since start', 'Wet weight'}; title.tW_PT433843806 = 'Growth curve of individual PT433843806'; comment.tW_PT433843806 = 'Data from GreenBeef trial 1, individual PT433843806'; bibkey.tW_PT433843806 = 'GreenBeefTrial1';

data.tW_PT333653651 = [0 536; 14 548; 21 561; 35 589; 50 603; 63 615; 83 632];
init.tW_PT333653651 = 536; units.init.tW_PT333653651 = 'kg'; label.init.tW_PT333653651 = 'Initial weight';
units.tW_PT333653651 = {'d', 'kg'}; label.tW_PT333653651 = {'Time since start', 'Wet weight'}; title.tW_PT333653651 = 'Growth curve of individual PT333653651'; comment.tW_PT333653651 = 'Data from GreenBeef trial 1, individual PT333653651'; bibkey.tW_PT333653651 = 'GreenBeefTrial1';

data.tW_PT724523831 = [0 485; 14 505; 21 510; 35 474; 50 504; 63 581; 83 565];
init.tW_PT724523831 = 485; units.init.tW_PT724523831 = 'kg'; label.init.tW_PT724523831 = 'Initial weight';
units.tW_PT724523831 = {'d', 'kg'}; label.tW_PT724523831 = {'Time since start', 'Wet weight'}; title.tW_PT724523831 = 'Growth curve of individual PT724523831'; comment.tW_PT724523831 = 'Data from GreenBeef trial 1, individual PT724523831'; bibkey.tW_PT724523831 = 'GreenBeefTrial1';

data.tW_PT833653644 = [0 548; 14 544; 21 553; 35 579; 50 603; 63 623; 83 652];
init.tW_PT833653644 = 548; units.init.tW_PT833653644 = 'kg'; label.init.tW_PT833653644 = 'Initial weight';
units.tW_PT833653644 = {'d', 'kg'}; label.tW_PT833653644 = {'Time since start', 'Wet weight'}; title.tW_PT833653644 = 'Growth curve of individual PT833653644'; comment.tW_PT833653644 = 'Data from GreenBeef trial 1, individual PT833653644'; bibkey.tW_PT833653644 = 'GreenBeefTrial1';

data.tW_PT933843912 = [0 545; 14 561; 21 565; 35 581; 50 616; 63 649; 83 668];
init.tW_PT933843912 = 545; units.init.tW_PT933843912 = 'kg'; label.init.tW_PT933843912 = 'Initial weight';
units.tW_PT933843912 = {'d', 'kg'}; label.tW_PT933843912 = {'Time since start', 'Wet weight'}; title.tW_PT933843912 = 'Growth curve of individual PT933843912'; comment.tW_PT933843912 = 'Data from GreenBeef trial 1, individual PT933843912'; bibkey.tW_PT933843912 = 'GreenBeefTrial1';

data.tW_PT533358890 = [0 477; 14 493; 21 498; 35 529; 50 551; 63 586; 83 621];
init.tW_PT533358890 = 477; units.init.tW_PT533358890 = 'kg'; label.init.tW_PT533358890 = 'Initial weight';
units.tW_PT533358890 = {'d', 'kg'}; label.tW_PT533358890 = {'Time since start', 'Wet weight'}; title.tW_PT533358890 = 'Growth curve of individual PT533358890'; comment.tW_PT533358890 = 'Data from GreenBeef trial 1, individual PT533358890'; bibkey.tW_PT533358890 = 'GreenBeefTrial1';

data.tW_PT233843883 = [0 506; 14 525; 21 533; 35 561; 50 583; 63 592; 83 620];
init.tW_PT233843883 = 506; units.init.tW_PT233843883 = 'kg'; label.init.tW_PT233843883 = 'Initial weight';
units.tW_PT233843883 = {'d', 'kg'}; label.tW_PT233843883 = {'Time since start', 'Wet weight'}; title.tW_PT233843883 = 'Growth curve of individual PT233843883'; comment.tW_PT233843883 = 'Data from GreenBeef trial 1, individual PT233843883'; bibkey.tW_PT233843883 = 'GreenBeefTrial1';

data.tW_PT033634130 = [0 453; 14 468; 21 471; 35 500; 50 517; 63 526; 83 556];
init.tW_PT033634130 = 453; units.init.tW_PT033634130 = 'kg'; label.init.tW_PT033634130 = 'Initial weight';
units.tW_PT033634130 = {'d', 'kg'}; label.tW_PT033634130 = {'Time since start', 'Wet weight'}; title.tW_PT033634130 = 'Growth curve of individual PT033634130'; comment.tW_PT033634130 = 'Data from GreenBeef trial 1, individual PT033634130'; bibkey.tW_PT033634130 = 'GreenBeefTrial1';



% entity data types
metaData.entity_data_types = {'tW'}; 


% Cell array of entity_ids
data.entity_list = 10; units.entity_list = '-'; label.entity_list = 'Dummy variable'; 
tiers.entity_list = {'TMR'}; units.tiers.entity_list = '-'; label.tiers.entity_list = 'List of entities'; 
metaData.entity_list = tiers.entity_list; % Save in metaData to use in pars_init.m

% Struct with form tier_entities.(tier_name) = list_of_entities_of_tier
data.tier_entities = 10; units.tier_entities = '-'; label.tier_entities = 'Dummy variable'; 
tiers.tier_entities = struct('diet', {{'TMR'}}, 'individual', {{'PT424401157', 'PT624139868', 'PT433843806', 'PT333653651', 'PT724523831', 'PT833653644', 'PT933843912', 'PT533358890', 'PT233843883', 'PT033634130'}}); units.tiers.tier_entities = '-'; label.tiers.tier_entities = 'List of entity ids for each tier'; 


% Struct with form groups_of_entity.(entity_id) = list_of_groups_ids_entity_belongs_to
data.groups_of_entity = 10; units.groups_of_entity = '-'; label.groups_of_entity = 'Dummy variable'; 
tiers.groups_of_entity = struct('PT424401157', {{'Pen_2'}}, 'PT624139868', {{'Pen_2'}}, 'PT433843806', {{'Pen_2'}}, 'PT333653651', {{'Pen_5'}}, 'PT724523831', {{'Pen_5'}}, 'PT833653644', {{'Pen_2'}}, 'PT933843912', {{'Pen_2'}}, 'PT533358890', {{'Pen_5'}}, 'PT233843883', {{'Pen_5'}}, 'PT033634130', {{'Pen_5'}}); units.tiers.groups_of_entity = '-'; label.tiers.groups_of_entity = 'Groups each entity belongs to'; 

    
% Tier subtree
% Lists entities that are below entity_id for each tier below
% Struct with form tier_subtree.(entity_id).(tier_name) = list_of_entities_below
data.tier_subtree = 10; units.tier_subtree = '-'; label.tier_subtree = 'Dummy variable'; 
tiers.tier_subtree = struct('TMR', struct('individual', {{'PT424401157', 'PT624139868', 'PT433843806', 'PT333653651', 'PT724523831', 'PT833653644', 'PT933843912', 'PT533358890', 'PT233843883', 'PT033634130'}})); units.tiers.tier_subtree = '-'; label.tiers.tier_subtree = 'Tier subtree'; 


%% Tier parameters
% Cell array with tier parameters
data.tier_pars = 10; units.tier_pars = '-'; label.tier_pars = 'Dummy variable'; comment.tier_pars = 'Tier parameters'; 
tiers.tier_pars = {'p_Am', 'kap_X'}; units.tiers.tier_pars = '-'; label.tiers.tier_pars = 'Tier parameters'; 
metaData.tier_pars = tiers.tier_pars; % Save in metaData to use in pars_init.m

% Initial values for each tier parameter and entity
% Struct with form tier_par_init_values.(par).(entity_id) = value;
metaData.tier_par_init_values = struct('p_Am', struct('TMR', 2124.371378681546), 'kap_X', struct('TMR', 0.21713680397830953)); 


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

for dt=1:length(metaData.entity_data_types)
    data_type = metaData.entity_data_types{dt};
    cumulative = strcmp(data_type, cumulative_data_types);
    for i=1:length(tiers.tier_entities.individual)
        ind_id = tiers.tier_entities.individual{i};
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
    for g=1:length(tiers.tier_groups.individual)
        g_id = tiers.tier_groups.individual{g};
        data_varname = [data_type '_' g_id];
    
        if isfield(data, data_varname)
            n_inds_in_data = length(fieldnames(init.(data_varname)));
            weights.(data_varname) = weights.(data_varname) * group_data_weights.(data_type) * n_inds_in_data;
        end
    end
end

%% Set pseudo-data for tier parameters
for e=1:length(tiers.entity_list)
    entity_id = tiers.entity_list{e};
    for p=1:length(tiers.tier_pars)
        par_name = tiers.tier_pars{p};
        varname = [par_name '_' entity_id];
        
        data.psd.(varname) = metaData.tier_par_init_values.(par_name).(entity_id);
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



