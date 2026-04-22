function [data, auxData, metaData, txtData, weights] = mydata_Bos_taurus_Angus
% Baseline generic mydata template for DEBtoolPyIF.

%% set metaData
metaData.phylum = 'Chordata';
metaData.class = 'Mammalia';
metaData.order = 'Artiodactyla';
metaData.family = 'Bovidae';
metaData.species = 'Bos taurus Angus';
metaData.species_en = 'Angus cattle';

metaData.T_typical = C2K(38.6); % K, body temperature

metaData.COMPLETE = 3; % using criteria of LikaKear2011

%% Author information
metaData.author = {'Diogo F. Oliveira', 'Goncalo M. Marques'};
metaData.email = 'diogo.miguel.oliveira@tecnico.ulisboa.pt';
metaData.address = 'Instituto Superior Tecnico, Universidade de Lisboa, Portugal';

%% Group data
%% Time vs Group daily feed consumption data

data.tJX_grp_Pen_2 = [0.0 45.43; 1.0 43.88; 2.0 26.68; 3.0 46.87; 4.0 40.24; 5.0 41.11; 6.0 41.15; 7.0 44.57; 8.0 45.67; 9.0 47.08; 10.0 41.6; 11.0 33.54; 12.0 47.22; 13.0 40.4; 14.0 38.04; 15.0 40.91; 16.0 36.2; 17.0 38.47; 18.0 38.95; 19.0 38.89; 20.0 40.95; 21.0 30.58; 22.0 37.61; 23.0 48.26; 24.0 41.03; 25.0 44.06; 26.0 43.23; 27.0 47.73; 28.0 41.82; 29.0 43.78; 30.0 29.79; 31.0 37.26; 32.0 29.83; 33.0 39.34; 34.0 45.31; 35.0 36.18; 36.0 44.02; 37.0 41.3; 38.0 43.11; 39.0 49.12; 40.0 42.88; 41.0 41.72; 42.0 45.65; 43.0 45.49; 44.0 44.04; 45.0 47.26; 46.0 45.33; 47.0 49.18; 48.0 46.08; 49.0 45.88; 50.0 47.81; 51.0 48.36; 52.0 50.03; 53.0 51.46; 54.0 44.68; 55.0 44.68; 56.0 39.02; 57.0 41.58; 58.0 48.02; 59.0 42.64; 60.0 48.65; 61.0 48.65; 62.0 45.12; 63.0 45.12; 64.0 48.69; 65.0 55.53; 66.0 48.89; 67.0 50.85; 68.0 54.41; 69.0 43.74; 70.0 43.74; 71.0 53.53; 72.0 56.51; 73.0 52.39; 74.0 54.31; 75.0 48.46; 76.0 56.28; 77.0 57.18; 78.0 55.06; 79.0 51.8; 80.0 59.42; 81.0 53.68; 82.0 56.02; 83.0 56.02];
units.tJX_grp_Pen_2 = {'d', 'kg'}; label.tJX_grp_Pen_2 = {'Time since start', 'Daily food consumption of group during test'}; comment.tJX_grp_Pen_2 = 'Data from GreenBeef trial 1'; title.tJX_grp_Pen_2 = 'Daily feed consumption,  Pen_2'; bibkey.tJX_grp_Pen_2 = 'GreenBeefTrial1';
init.tJX_grp_Pen_2 = struct('PT424401157', 469, 'PT433843806', 507, 'PT624139868', 464, 'PT833653644', 548, 'PT933843912', 545);
units.init.tJX_grp_Pen_2 = 'kg'; label.init.tJX_grp_Pen_2 = 'Initial weights for the individuals in the group'; 




% group data types
metaData.group_data_types = {'tJX_grp'}; 


% Struct with form tier_groups.(tier_name) = list_of_groups_of_tier
data.tier_groups = 10;
units.tier_groups = '-'; label.tier_groups = 'Dummy variable'; 
tiers.tier_groups = struct('individual', {{'Pen_2'}});
units.tiers.tier_groups = '-'; label.tiers.tier_groups = 'List of groups ids for each tier'; 


%% Entity data
%% Time vs Weight data 

data.tW_PT833653644 = [0 548; 14 544; 21 553; 35 579; 50 603; 63 623; 83 652];
units.tW_PT833653644 = {'d', 'kg'}; label.tW_PT833653644 = {'Time since start', 'Wet weight'}; comment.tW_PT833653644 = 'Data from GreenBeef trial 1'; title.tW_PT833653644 = 'Wet weight growth curve, individual PT833653644'; bibkey.tW_PT833653644 = 'GreenBeefTrial1';
init.tW_PT833653644 = 548;
units.init.tW_PT833653644 = 'kg'; label.init.tW_PT833653644 = 'Initial weight'; 


data.tW_PT624139868 = [0 464; 14 470; 21 480; 35 508; 50 542; 63 558; 83 582];
units.tW_PT624139868 = {'d', 'kg'}; label.tW_PT624139868 = {'Time since start', 'Wet weight'}; comment.tW_PT624139868 = 'Data from GreenBeef trial 1'; title.tW_PT624139868 = 'Wet weight growth curve, individual PT624139868'; bibkey.tW_PT624139868 = 'GreenBeefTrial1';
init.tW_PT624139868 = 464;
units.init.tW_PT624139868 = 'kg'; label.init.tW_PT624139868 = 'Initial weight'; 


data.tW_PT433843806 = [0 507; 14 532; 21 532; 35 568; 50 600; 63 607; 83 628];
units.tW_PT433843806 = {'d', 'kg'}; label.tW_PT433843806 = {'Time since start', 'Wet weight'}; comment.tW_PT433843806 = 'Data from GreenBeef trial 1'; title.tW_PT433843806 = 'Wet weight growth curve, individual PT433843806'; bibkey.tW_PT433843806 = 'GreenBeefTrial1';
init.tW_PT433843806 = 507;
units.init.tW_PT433843806 = 'kg'; label.init.tW_PT433843806 = 'Initial weight'; 


data.tW_PT424401157 = [0 469; 14 482; 21 486; 35 512; 50 540; 63 549; 83 571];
units.tW_PT424401157 = {'d', 'kg'}; label.tW_PT424401157 = {'Time since start', 'Wet weight'}; comment.tW_PT424401157 = 'Data from GreenBeef trial 1'; title.tW_PT424401157 = 'Wet weight growth curve, individual PT424401157'; bibkey.tW_PT424401157 = 'GreenBeefTrial1';
init.tW_PT424401157 = 469;
units.init.tW_PT424401157 = 'kg'; label.init.tW_PT424401157 = 'Initial weight'; 


data.tW_PT933843912 = [0 545; 14 561; 21 565; 35 581; 50 616; 63 649; 83 668];
units.tW_PT933843912 = {'d', 'kg'}; label.tW_PT933843912 = {'Time since start', 'Wet weight'}; comment.tW_PT933843912 = 'Data from GreenBeef trial 1'; title.tW_PT933843912 = 'Wet weight growth curve, individual PT933843912'; bibkey.tW_PT933843912 = 'GreenBeefTrial1';
init.tW_PT933843912 = 545;
units.init.tW_PT933843912 = 'kg'; label.init.tW_PT933843912 = 'Initial weight'; 




% entity data types
metaData.entity_data_types = {'tW'}; 


% Cell array of entity_ids
data.entity_list = 10;
units.entity_list = '-'; label.entity_list = 'Dummy variable'; 
tiers.entity_list = {'PT424401157', 'PT433843806', 'PT624139868', 'PT833653644', 'PT933843912'};
units.tiers.entity_list = '-'; label.tiers.entity_list = 'List of entities'; 
metaData.entity_list = tiers.entity_list; 


% Struct with form tier_entities.(tier_name) = list_of_entities_of_tier
data.tier_entities = 10;
units.tier_entities = '-'; label.tier_entities = 'Dummy variable'; 
tiers.tier_entities = struct('individual', {{'PT833653644', 'PT624139868', 'PT433843806', 'PT424401157', 'PT933843912'}});
units.tiers.tier_entities = '-'; label.tiers.tier_entities = 'List of entity ids for each tier'; 


% Struct with form groups_of_entity.(entity_id) = list_of_groups_ids_entity_belongs_to
data.groups_of_entity = 10;
units.groups_of_entity = '-'; label.groups_of_entity = 'Dummy variable'; 
tiers.groups_of_entity = struct('PT833653644', {{'Pen_2'}}, 'PT624139868', {{'Pen_2'}}, 'PT433843806', {{'Pen_2'}}, 'PT424401157', {{'Pen_2'}}, 'PT933843912', {{'Pen_2'}});
units.tiers.groups_of_entity = '-'; label.tiers.groups_of_entity = 'Groups each entity belongs to'; 

    
% Tier subtree
% Lists entities that are below entity_id for each tier below
% Struct with form tier_subtree.(entity_id).(tier_name) = list_of_entities_below
data.tier_subtree = 10;
units.tier_subtree = '-'; label.tier_subtree = 'Dummy variable'; 
tiers.tier_subtree = struct('PT424401157', struct(), 'PT433843806', struct(), 'PT624139868', struct(), 'PT833653644', struct(), 'PT933843912', struct());
units.tiers.tier_subtree = '-'; label.tiers.tier_subtree = 'Tier subtree'; 


%% Tier parameters
% Cell array with tier parameters
data.tier_pars = 10;
units.tier_pars = '-'; label.tier_pars = 'Dummy variable'; comment.tier_pars = 'Tier parameters'; 
tiers.tier_pars = {'p_Am', 'kap_X'};
units.tiers.tier_pars = '-'; label.tiers.tier_pars = 'Tier parameters'; 
metaData.tier_pars = tiers.tier_pars; 


% Initial values for each tier parameter and entity
% Struct with form tier_par_init_values.(par).(entity_id) = value;
metaData.tier_par_init_values = struct('p_Am', struct('PT424401157', 5588.926425728412, 'PT433843806', 5588.926425728412, 'PT624139868', 5588.926425728412, 'PT833653644', 5588.926425728412, 'PT933843912', 5588.926425728412), 'kap_X', struct('PT424401157', 0.21959189993722267, 'PT433843806', 0.21959189993722267, 'PT624139868', 0.21959189993722267, 'PT833653644', 0.21959189993722267, 'PT933843912', 0.21959189993722267)); 


%% Set default weights
weights = setweights(data, []);

%% Save dataset field names
metaData.data_fields = fieldnames(data);

%% Save data fields into zero-variate and univariate
metaData.data_0     = {};
metaData.data_1     = {};
for i = 1:length(metaData.data_fields)
    field = metaData.data_fields{i};
    if length(data.(field)) > 1
        metaData.data_1{end+1} = field; %#ok<AGROW>
    else
        metaData.data_0{end+1} = field; %#ok<AGROW>
    end
end

temp = struct();
%% Set temperature metadata
for i = 1:length(metaData.data_fields)
    field = metaData.data_fields{i};

    if ~isfield(temp, field)
        temp.(field) = metaData.T_typical;
        units.temp.(field) = 'K';
        label.temp.(field) = 'temperature';
    end
end

%% Remove weights from dummy variables
for i = 1:length(metaData.data_fields)
    field = metaData.data_fields{i};
    if strcmp(label.(field), 'Dummy variable')
        weights.(field) = 0;
    end
end

%% Set weight of individual data
cumulative_data_types = {'tW'};
ind_data_weights = struct('tW', 1/5);

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
group_data_weights = struct('tJX_grp', 1);

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


%% Set generic and multitier pseudo-data
%% Add generic pseudo-data
[data, units, label, weights] = addpseudodata(data, units, label, weights);
%% Add multitier pseudo-data from previous-tier estimates
for e = 1:length(tiers.entity_list)
    entity_id = tiers.entity_list{e};
    for p = 1:length(tiers.tier_pars)
        par_name = tiers.tier_pars{p};
        varname = [par_name '_' entity_id];

        data.psd.(varname) = metaData.tier_par_init_values.(par_name).(entity_id);
        units.psd.(varname) = '';
        label.psd.(varname) = '';
        weights.psd.(varname) = 0.1;
    end
end

%% Data Sources and References
%
%% pack auxData and txtData for output
auxData.temp = temp;
auxData.tiers = tiers;
auxData.init = init;
txtData.units = units;
txtData.label = label;
txtData.bibkey = bibkey;
txtData.comment = comment;
txtData.title = title;

end

