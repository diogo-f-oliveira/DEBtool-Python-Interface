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

data.tJX_grp_Pen_4 = [0.0 45.31; 1.0 46.38; 2.0 50.99; 3.0 50.73; 4.0 49.98; 5.0 53.4; 6.0 48.49; 7.0 48.1; 8.0 50.04; 9.0 49.82; 10.0 47.02; 11.0 45.17; 12.0 49.82; 13.0 47.07; 14.0 46.72; 15.0 45.43; 16.0 47.58; 17.0 46.2; 18.0 48.43; 19.0 43.6; 20.0 57.75; 21.0 51.5; 22.0 50.64; 23.0 60.38; 24.0 51.42; 25.0 56.16; 26.0 54.31; 27.0 55.86; 28.0 53.79; 29.0 49.39; 30.0 49.22; 31.0 55.94; 32.0 53.4; 33.0 52.88; 34.0 47.28; 35.0 56.2; 36.0 58.18; 37.0 54.39; 38.0 53.7; 39.0 61.2; 40.0 56.03; 41.0 54.22; 42.0 53.36; 43.0 54.65; 44.0 47.93; 45.0 50.25; 46.0 51.98; 47.0 54.74; 48.0 55.86; 49.0 53.36; 50.0 54.65; 51.0 62.84; 52.0 66.72; 53.0 57.88; 54.0 56.72; 55.0 56.72; 56.0 55.17; 57.0 58.44; 58.0 55.34; 59.0 56.63; 60.0 65.77; 61.0 65.77; 62.0 54.82; 63.0 54.82; 64.0 60.08; 65.0 55.51; 66.0 65.08; 67.0 60.86; 68.0 58.92; 69.0 60.94; 70.0 60.94; 71.0 52.32; 72.0 52.24; 73.0 52.06; 74.0 50.08; 75.0 54.82; 76.0 57.58; 77.0 56.81; 78.0 58.27; 79.0 59.39; 80.0 56.37; 81.0 62.93; 82.0 59.74; 83.0 59.74];
units.tJX_grp_Pen_4 = {'d', 'kg'}; label.tJX_grp_Pen_4 = {'Time since start', 'Daily food consumption of group during test'}; comment.tJX_grp_Pen_4 = 'Data from GreenBeef trial 1'; title.tJX_grp_Pen_4 = 'Daily feed consumption,  Pen_4'; bibkey.tJX_grp_Pen_4 = 'GreenBeefTrial1';
init.tJX_grp_Pen_4 = struct('PT224401177', 562, 'PT524956505', 542, 'PT533843896', 480, 'PT924401183', 510, 'PT933602927', 426);
units.init.tJX_grp_Pen_4 = 'kg'; label.init.tJX_grp_Pen_4 = 'Initial weights for the individuals in the group'; 




% group data types
metaData.group_data_types = {'tJX_grp'}; 


% Struct with form tier_groups.(tier_name) = list_of_groups_of_tier
data.tier_groups = 10;
units.tier_groups = '-'; label.tier_groups = 'Dummy variable'; 
tiers.tier_groups = struct('individual', {{'Pen_4'}});
units.tiers.tier_groups = '-'; label.tiers.tier_groups = 'List of groups ids for each tier'; 


%% Entity data
%% Time vs Weight data 

data.tW_PT924401183 = [0 510; 14 543; 21 555; 35 587; 50 624; 63 648; 83 685];
units.tW_PT924401183 = {'d', 'kg'}; label.tW_PT924401183 = {'Time since start', 'Wet weight'}; comment.tW_PT924401183 = 'Data from GreenBeef trial 1'; title.tW_PT924401183 = 'Wet weight growth curve, individual PT924401183'; bibkey.tW_PT924401183 = 'GreenBeefTrial1';
init.tW_PT924401183 = 510;
units.init.tW_PT924401183 = 'kg'; label.init.tW_PT924401183 = 'Initial weight'; 


data.tW_PT224401177 = [0 562; 14 589; 21 597; 35 632; 50 660; 63 697; 83 723];
units.tW_PT224401177 = {'d', 'kg'}; label.tW_PT224401177 = {'Time since start', 'Wet weight'}; comment.tW_PT224401177 = 'Data from GreenBeef trial 1'; title.tW_PT224401177 = 'Wet weight growth curve, individual PT224401177'; bibkey.tW_PT224401177 = 'GreenBeefTrial1';
init.tW_PT224401177 = 562;
units.init.tW_PT224401177 = 'kg'; label.init.tW_PT224401177 = 'Initial weight'; 


data.tW_PT524956505 = [0 542; 14 567; 21 577; 35 603; 50 638; 63 664; 83 707];
units.tW_PT524956505 = {'d', 'kg'}; label.tW_PT524956505 = {'Time since start', 'Wet weight'}; comment.tW_PT524956505 = 'Data from GreenBeef trial 1'; title.tW_PT524956505 = 'Wet weight growth curve, individual PT524956505'; bibkey.tW_PT524956505 = 'GreenBeefTrial1';
init.tW_PT524956505 = 542;
units.init.tW_PT524956505 = 'kg'; label.init.tW_PT524956505 = 'Initial weight'; 


data.tW_PT933602927 = [0 426; 14 450; 21 462; 35 482; 50 497; 63 524; 83 539];
units.tW_PT933602927 = {'d', 'kg'}; label.tW_PT933602927 = {'Time since start', 'Wet weight'}; comment.tW_PT933602927 = 'Data from GreenBeef trial 1'; title.tW_PT933602927 = 'Wet weight growth curve, individual PT933602927'; bibkey.tW_PT933602927 = 'GreenBeefTrial1';
init.tW_PT933602927 = 426;
units.init.tW_PT933602927 = 'kg'; label.init.tW_PT933602927 = 'Initial weight'; 


data.tW_PT533843896 = [0 480; 14 492; 21 506; 35 536; 50 551; 63 574; 83 586];
units.tW_PT533843896 = {'d', 'kg'}; label.tW_PT533843896 = {'Time since start', 'Wet weight'}; comment.tW_PT533843896 = 'Data from GreenBeef trial 1'; title.tW_PT533843896 = 'Wet weight growth curve, individual PT533843896'; bibkey.tW_PT533843896 = 'GreenBeefTrial1';
init.tW_PT533843896 = 480;
units.init.tW_PT533843896 = 'kg'; label.init.tW_PT533843896 = 'Initial weight'; 




% entity data types
metaData.entity_data_types = {'tW'}; 


% Cell array of entity_ids
data.entity_list = 10;
units.entity_list = '-'; label.entity_list = 'Dummy variable'; 
tiers.entity_list = {'PT224401177', 'PT524956505', 'PT533843896', 'PT924401183', 'PT933602927'};
units.tiers.entity_list = '-'; label.tiers.entity_list = 'List of entities'; 
metaData.entity_list = tiers.entity_list; 


% Struct with form tier_entities.(tier_name) = list_of_entities_of_tier
data.tier_entities = 10;
units.tier_entities = '-'; label.tier_entities = 'Dummy variable'; 
tiers.tier_entities = struct('individual', {{'PT924401183', 'PT224401177', 'PT524956505', 'PT933602927', 'PT533843896'}});
units.tiers.tier_entities = '-'; label.tiers.tier_entities = 'List of entity ids for each tier'; 


% Struct with form groups_of_entity.(entity_id) = list_of_groups_ids_entity_belongs_to
data.groups_of_entity = 10;
units.groups_of_entity = '-'; label.groups_of_entity = 'Dummy variable'; 
tiers.groups_of_entity = struct('PT924401183', {{'Pen_4'}}, 'PT224401177', {{'Pen_4'}}, 'PT524956505', {{'Pen_4'}}, 'PT933602927', {{'Pen_4'}}, 'PT533843896', {{'Pen_4'}});
units.tiers.groups_of_entity = '-'; label.tiers.groups_of_entity = 'Groups each entity belongs to'; 

    
% Tier subtree
% Lists entities that are below entity_id for each tier below
% Struct with form tier_subtree.(entity_id).(tier_name) = list_of_entities_below
data.tier_subtree = 10;
units.tier_subtree = '-'; label.tier_subtree = 'Dummy variable'; 
tiers.tier_subtree = struct('PT224401177', struct(), 'PT524956505', struct(), 'PT533843896', struct(), 'PT924401183', struct(), 'PT933602927', struct());
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
metaData.tier_par_init_values = struct('p_Am', struct('PT224401177', 2336.7622667211635, 'PT524956505', 2336.7622667211635, 'PT533843896', 2336.7622667211635, 'PT924401183', 2336.7622667211635, 'PT933602927', 2336.7622667211635), 'kap_X', struct('PT224401177', 0.21889793801136814, 'PT524956505', 0.21889793801136814, 'PT533843896', 0.21889793801136814, 'PT924401183', 0.21889793801136814, 'PT933602927', 0.21889793801136814)); 


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


