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
% Both
data.ab = 282.5;        units.ab = 'd';     label.ab = 'age at birth';    bibkey.ab = 'LiveBee1945';
data.am = 32.5*365;     units.am = 'd';     label.am = 'life span';                         bibkey.am = 'DakaMart2006';
data.Ri  =  1/436.7;    units.Ri  = '#/d';  label.Ri  = 'maximum reprod rate';  bibkey.Ri  = 'Bastos2022'; comment.Ri = 'inverse of the interval between parturitions';

% Females
data.tx_f = 200;        units.tx_f = 'd';   label.tx_f = 'time since birth at weaning for females'; bibkey.tx_f = 'Bastos2022';  
data.tp_f = 307;        units.tp_f = 'd';   label.tp_f = 'time since birth at puberty for females'; bibkey.tp_f = 'BeltButt1992';

data.Lhi_f = 135;       units.Lhi_f = 'cm'; label.Lhi_f = 'ultimate withers height for females';   bibkey.Lhi_f = 'FAO2024';

data.Wwb_f = 34.9e3;    units.Wwb_f = 'g';  label.Wwb_f = 'wet weight at birth for females'; bibkey.Wwb_f = 'Bastos2022';
data.Wwx_f = 251.2e3;   units.Wwx_f = 'g';  label.Wwx_f = 'wet weight at weaning for females'; bibkey.Wwx_f = 'Bastos2022';
data.Wwp_f = 301.5e3;   units.Wwp_f = 'g';  label.Wwp_f = 'wet weight at puberty for males'; bibkey.Wwp_f = 'Bastos2022';
data.Wwi_f = 650e3;     units.Wwi_f = 'g';  label.Wwi_f = 'ultimate wet weight for females';   bibkey.Wwi_f = 'FAO2024';

% Males
data.tx_m = 200;        units.tx_m = 'd';   label.tx_m = 'time since birth at weaning for males'; bibkey.tx_m = 'Bastos2022'; 
data.tp_m = 295;        units.tp_m = 'd';   label.tp_m = 'time since birth at puberty for males'; bibkey.tp_m = 'Luns1982';

data.Lhi_m = 145;       units.Lhi_m = 'cm'; label.Lhi_m = 'ultimate withers height for males';   bibkey.Lhi_m = 'FAO2024';

data.Wwb_m = 37.4e3;    units.Wwb_m = 'g';  label.Wwb_m = 'wet weight at birth for males';      bibkey.Wwb_m = 'Bastos2022';
data.Wwx_m = 264.1e3;   units.Wwx_m = 'g';  label.Wwx_m = 'wet weight at weaning for males';    bibkey.Wwx_m = 'Bastos2022';
data.Wwp_m = 374.1e3;   units.Wwp_m = 'g';  label.Wwp_m = 'wet weight at puberty for males';    bibkey.Wwp_m = 'Bastos2022';
data.Wwi_m = 1000e3;    units.Wwi_m = 'g';  label.Wwi_m = 'ultimate wet weight for males';      bibkey.Wwi_m = 'FAO2024';

%% Group data
$group_data

% group data types
$group_data_types

% Cell array of group_ids
$group_list

%% Individual data
$individual_data

% individual data types
$ind_data_types

% Cell array of ind_ids
$ind_list

% Struct with form groups_of_ind.(ind_id) = list_of_groups_ids_ind_belongs_to
$groups_of_ind

% Cell array of tier_sample_ids
$tier_sample_list

% Struct with form 
% tier_sample_inds.(tier_sample_id) = list_of_inds_in_tier_sample
$tier_sample_inds

%% Tier parameters
% Cell array with tier parameters
$tier_pars

% Initial values for each tier parameter and sample
% Struct with form tier_par_init_values.(par).(tier_sample_id) = value;
$tier_par_init_values


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

%% Set weights of individual data
cumulative_data_types = {'tW'};
ind_data_weights = struct('tW', 3/40);

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


%% Set weights of group data
group_data_weights = struct('tJX_grp', 5/40);
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
[data, units, label, weights] = addpseudodata(data, units, label, weights);

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
bibkey = 'DakaMart2006'; type = 'Article'; bib = [ ... 
'author = {D?kay, I., M?rton, D., Keller, K., F?rd?s, A., T?r?k, M., Szab?, F.}, ' ... 
'year = {2006}, ' ...
'title = {Study on the age at first calving and the longevity of beef cows}, ' ...
'journal = {Journal of Central European Agriculture}, ' ...
'volume = {7}, ' ...
'pages = {377--388}'];
metaData.biblist.(bibkey) = ['''@', type, '{', bibkey, ', ' bib, '}'';'];
%
bibkey = 'BeltButt1992'; type = 'Article'; bib = [ ... 
'author = {Beltr?n, J. J. and  Butts, W. T. and Olson, T. A. and Koger, M.}, ' ... 
'year = {1992}, ' ...
'title = {Growth patterns of two lines of Angus cattle selected using predicted growth parameters}, ' ...
'journal = {Journal of Animal Science}, ' ...
'volume = {70}, ' ...
'pages = {734--41}'];
metaData.biblist.(bibkey) = ['''@', type, '{', bibkey, ', ' bib, '}'';'];
%
bibkey = 'LiveBee1945'; type = 'Article'; bib = [ ... 
'author = {Livesay, E. A. and  Bee, Ural G.}' ... 
'year = {1945}, ' ...
'title = {A study of the gestation periods of five breeds of cattle}, ' ...
'journal = {Journal of Animal Science}, ' ...
'volume = {4}, ' ...
'pages = {13--14}'];
metaData.biblist.(bibkey) = ['''@', type, '{', bibkey, ', ' bib, '}'';'];
%
bibkey = 'Luns1982'; type = 'Article'; bib = [ ... 
'author = {Lunstra, D. D.}, ' ... 
'year = {1982}, ' ...
'title = {Testicular development and onset of puberty in beef bulls}, ' ...
'journal = {Beef Research Program Progress Report}, ' ...
'volume = {1}, ' ...
'pages = {26--27}'];
metaData.biblist.(bibkey) = ['''@', type, '{', bibkey, ', ' bib, '}'';'];
%
bibkey = 'Bastos2022'; type = 'MasterThesis'; bib = [ ...
'author = {Bastos, Ana R. P.}, ' ... 
'year = {2022}, ' ...
'title = {Caracterização produtiva e reprodutiva da raça {Aberdeen}-{Angus} em {Portugal} no período 2014-2020}, ' ...
'school = {Universidade de Lisboa, Faculdade de Medicina Veterinária. Instituto Superior de Agronomia}, '
];
metaData.biblist.(bibkey) = ['''@', type, '{', bibkey, ', ' bib, '}'';'];
%
bibkey = 'FAO2024'; type = 'misc'; bib = [...
    'title = "Domestic Animal Diversity Information System ({DAD-IS}) website",' ...
    'author = "{Food and Agriculture Organization of the United nations}",' ...
    'howpublished = \url{https://www.fao.org/dad-is/browse-by-country-and-species/en/},"' ...
    'year = "cited December 2022"'];
metaData.biblist.(bibkey) = ['''@', type, '{', bibkey, ', ' bib, '}'';'];
%
