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

data.tJX_grp_Pen_3 = [0.0 44.62; 1.0 44.22; 2.0 49.87; 3.0 51.94; 4.0 50.32; 5.0 48.06; 6.0 50.56; 7.0 43.44; 8.0 44.01; 9.0 44.13; 10.0 45.3; 11.0 46.98; 12.0 46.89; 13.0 48.1; 14.0 43.96; 15.0 44.82; 16.0 49.82; 17.0 49.13; 18.0 49.63; 19.0 46.79; 20.0 57.49; 21.0 45.73; 22.0 45.38; 23.0 53.4; 24.0 47.63; 25.0 53.92; 26.0 48.62; 27.0 43.62; 28.0 51.38; 29.0 46.98; 30.0 45.08; 31.0 52.75; 32.0 49.09; 33.0 46.85; 34.0 47.37; 35.0 54.65; 36.0 45.94; 37.0 47.15; 38.0 49.74; 39.0 52.24; 40.0 50.86; 41.0 53.62; 42.0 53.62; 43.0 56.46; 44.0 54.56; 45.0 53.27; 46.0 54.22; 47.0 56.37; 48.0 57.15; 49.0 52.06; 50.0 55.25; 51.0 62.5; 52.0 62.06; 53.0 56.63; 54.0 57.67; 55.0 57.67; 56.0 57.58; 57.0 56.2; 58.0 55.34; 59.0 55.17; 60.0 59.48; 61.0 59.48; 62.0 64.91; 63.0 64.91; 64.0 50.94; 65.0 51.89; 66.0 53.96; 67.0 60.25; 68.0 49.69; 69.0 52.41; 70.0 52.41; 71.0 55.43; 72.0 62.32; 73.0 56.12; 74.0 56.29; 75.0 56.37; 76.0 57.15; 77.0 58.44; 78.0 55.6; 79.0 52.06; 80.0 56.72; 81.0 55.25; 82.0 55.99; 83.0 55.99];
units.tJX_grp_Pen_3 = {'d', 'kg'}; label.tJX_grp_Pen_3 = {'Time since start', 'Daily food consumption of group during test'}; comment.tJX_grp_Pen_3 = 'Data from GreenBeef trial 1'; title.tJX_grp_Pen_3 = 'Daily feed consumption,  Pen_3'; bibkey.tJX_grp_Pen_3 = 'GreenBeefTrial1';
init.tJX_grp_Pen_3 = struct('PT333842562', 515, 'PT524401180', 496, 'PT533987885', 436, 'PT833653649', 535, 'PT933843894', 508);
units.init.tJX_grp_Pen_3 = 'kg'; label.init.tJX_grp_Pen_3 = 'Initial weights for the individuals in the group'; 




% group data types
metaData.group_data_types = {'tJX_grp'}; 


% Struct with form tier_groups.(tier_name) = list_of_groups_of_tier
data.tier_groups = 10;
units.tier_groups = '-'; label.tier_groups = 'Dummy variable'; 
tiers.tier_groups = struct('individual', {{'Pen_3'}});
units.tiers.tier_groups = '-'; label.tiers.tier_groups = 'List of groups ids for each tier'; 


%% Entity data
%% Time vs Weight data 

data.tW_PT833653649 = [0 535; 14 546; 21 557; 35 586; 50 613; 63 641; 83 656];
units.tW_PT833653649 = {'d', 'kg'}; label.tW_PT833653649 = {'Time since start', 'Wet weight'}; comment.tW_PT833653649 = 'Data from GreenBeef trial 1'; title.tW_PT833653649 = 'Wet weight growth curve, individual PT833653649'; bibkey.tW_PT833653649 = 'GreenBeefTrial1';
init.tW_PT833653649 = 535;
units.init.tW_PT833653649 = 'kg'; label.init.tW_PT833653649 = 'Initial weight'; 


data.tW_PT933843894 = [0 508; 14 521; 21 534; 35 563; 50 583; 63 610; 83 639];
units.tW_PT933843894 = {'d', 'kg'}; label.tW_PT933843894 = {'Time since start', 'Wet weight'}; comment.tW_PT933843894 = 'Data from GreenBeef trial 1'; title.tW_PT933843894 = 'Wet weight growth curve, individual PT933843894'; bibkey.tW_PT933843894 = 'GreenBeefTrial1';
init.tW_PT933843894 = 508;
units.init.tW_PT933843894 = 'kg'; label.init.tW_PT933843894 = 'Initial weight'; 


data.tW_PT333842562 = [0 515; 14 535; 21 539; 35 566; 50 594; 63 630; 83 652];
units.tW_PT333842562 = {'d', 'kg'}; label.tW_PT333842562 = {'Time since start', 'Wet weight'}; comment.tW_PT333842562 = 'Data from GreenBeef trial 1'; title.tW_PT333842562 = 'Wet weight growth curve, individual PT333842562'; bibkey.tW_PT333842562 = 'GreenBeefTrial1';
init.tW_PT333842562 = 515;
units.init.tW_PT333842562 = 'kg'; label.init.tW_PT333842562 = 'Initial weight'; 


data.tW_PT524401180 = [0 496; 14 503; 21 508; 35 532; 50 560; 63 586; 83 610];
units.tW_PT524401180 = {'d', 'kg'}; label.tW_PT524401180 = {'Time since start', 'Wet weight'}; comment.tW_PT524401180 = 'Data from GreenBeef trial 1'; title.tW_PT524401180 = 'Wet weight growth curve, individual PT524401180'; bibkey.tW_PT524401180 = 'GreenBeefTrial1';
init.tW_PT524401180 = 496;
units.init.tW_PT524401180 = 'kg'; label.init.tW_PT524401180 = 'Initial weight'; 


data.tW_PT533987885 = [0 436; 14 449; 21 460; 35 486; 50 502; 63 515; 83 542];
units.tW_PT533987885 = {'d', 'kg'}; label.tW_PT533987885 = {'Time since start', 'Wet weight'}; comment.tW_PT533987885 = 'Data from GreenBeef trial 1'; title.tW_PT533987885 = 'Wet weight growth curve, individual PT533987885'; bibkey.tW_PT533987885 = 'GreenBeefTrial1';
init.tW_PT533987885 = 436;
units.init.tW_PT533987885 = 'kg'; label.init.tW_PT533987885 = 'Initial weight'; 




% entity data types
metaData.entity_data_types = {'tW'}; 


% Cell array of entity_ids
data.entity_list = 10;
units.entity_list = '-'; label.entity_list = 'Dummy variable'; 
tiers.entity_list = {'PT333842562', 'PT524401180', 'PT533987885', 'PT833653649', 'PT933843894'};
units.tiers.entity_list = '-'; label.tiers.entity_list = 'List of entities'; 
metaData.entity_list = tiers.entity_list; 


% Struct with form tier_entities.(tier_name) = list_of_entities_of_tier
data.tier_entities = 10;
units.tier_entities = '-'; label.tier_entities = 'Dummy variable'; 
tiers.tier_entities = struct('individual', {{'PT833653649', 'PT933843894', 'PT333842562', 'PT524401180', 'PT533987885'}});
units.tiers.tier_entities = '-'; label.tiers.tier_entities = 'List of entity ids for each tier'; 


% Struct with form groups_of_entity.(entity_id) = list_of_groups_ids_entity_belongs_to
data.groups_of_entity = 10;
units.groups_of_entity = '-'; label.groups_of_entity = 'Dummy variable'; 
tiers.groups_of_entity = struct('PT833653649', {{'Pen_3'}}, 'PT933843894', {{'Pen_3'}}, 'PT333842562', {{'Pen_3'}}, 'PT524401180', {{'Pen_3'}}, 'PT533987885', {{'Pen_3'}});
units.tiers.groups_of_entity = '-'; label.tiers.groups_of_entity = 'Groups each entity belongs to'; 

    
% Tier subtree
% Lists entities that are below entity_id for each tier below
% Struct with form tier_subtree.(entity_id).(tier_name) = list_of_entities_below
data.tier_subtree = 10;
units.tier_subtree = '-'; label.tier_subtree = 'Dummy variable'; 
tiers.tier_subtree = struct('PT333842562', struct(), 'PT524401180', struct(), 'PT533987885', struct(), 'PT833653649', struct(), 'PT933843894', struct());
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
metaData.tier_par_init_values = struct('p_Am', struct('PT333842562', 5809.310086107758, 'PT524401180', 5809.310086107758, 'PT533987885', 5809.310086107758, 'PT833653649', 5809.310086107758, 'PT933843894', 5809.310086107758), 'kap_X', struct('PT333842562', 0.196993616023738, 'PT524401180', 0.196993616023738, 'PT533987885', 0.196993616023738, 'PT833653649', 0.196993616023738, 'PT933843894', 0.196993616023738)); 


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

