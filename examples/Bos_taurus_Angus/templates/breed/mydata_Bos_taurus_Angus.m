$function_header

$metadata_block

$typical_temperature_block

$completeness_level_block

$author_info_block

%% Species zero-variate data
% Both males and females
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
$group_data_block

% group data types
$group_data_types

% Struct with form tier_groups.(tier_name) = list_of_groups_of_tier
$tier_groups

%% Entity data
$entity_data_block

% entity data types
$entity_data_types

% Cell array of entity_ids
$entity_list

% Struct with form tier_entities.(tier_name) = list_of_entities_of_tier
$tier_entities

% Struct with form groups_of_entity.(entity_id) = list_of_groups_ids_entity_belongs_to
$groups_of_entity

% Tier subtree
% Lists entities that are below entity_id for each tier below
% Struct with form tier_subtree.(entity_id).(tier_name) = list_of_entities_below
$tier_subtree

%% Tier parameters
% Cell array with tier parameters
$tier_pars

% Initial values for each tier parameter and entity
% Struct with form tier_par_init_values.(par).(entity_id) = value;
$tier_par_init_values

$weights_block

$save_fields_block
$save_fields_by_variate_type_block

temp = struct();
$set_temperature_equal_to_typical_block

$remove_dummy_weights_block

%% Set weights of individual data
cumulative_data_types = {'tW'};
ind_data_weights = struct('tW', 3/20);

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


%% Set weights of group data
group_data_weights = struct('tJX_grp', 5/20);

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
$add_pseudodata_block
$multitier_pseudodata_block


%% Data Sources and References
%
refkey = 'DakaMart2006'; type = 'Article'; bib = [ ...
'author = {D?kay, I., M?rton, D., Keller, K., F?rd?s, A., T?r?k, M., Szab?, F.}, ' ...
'year = {2006}, ' ...
'title = {Study on the age at first calving and the longevity of beef cows}, ' ...
'journal = {Journal of Central European Agriculture}, ' ...
'volume = {7}, ' ...
'pages = {377--388}'];
metaData.biblist.(refkey) = ['''@', type, '{', refkey, ', ' bib, '}'';'];
%
refkey = 'BeltButt1992'; type = 'Article'; bib = [ ...
'author = {Beltr?n, J. J. and  Butts, W. T. and Olson, T. A. and Koger, M.}, ' ...
'year = {1992}, ' ...
'title = {Growth patterns of two lines of Angus cattle selected using predicted growth parameters}, ' ...
'journal = {Journal of Animal Science}, ' ...
'volume = {70}, ' ...
'pages = {734--41}'];
metaData.biblist.(refkey) = ['''@', type, '{', refkey, ', ' bib, '}'';'];
%
refkey = 'LiveBee1945'; type = 'Article'; bib = [ ...
'author = {Livesay, E. A. and  Bee, Ural G.}' ...
'year = {1945}, ' ...
'title = {A study of the gestation periods of five breeds of cattle}, ' ...
'journal = {Journal of Animal Science}, ' ...
'volume = {4}, ' ...
'pages = {13--14}'];
metaData.biblist.(refkey) = ['''@', type, '{', refkey, ', ' bib, '}'';'];
%
refkey = 'Luns1982'; type = 'Article'; bib = [ ...
'author = {Lunstra, D. D.}, ' ...
'year = {1982}, ' ...
'title = {Testicular development and onset of puberty in beef bulls}, ' ...
'journal = {Beef Research Program Progress Report}, ' ...
'volume = {1}, ' ...
'pages = {26--27}'];
metaData.biblist.(refkey) = ['''@', type, '{', refkey, ', ' bib, '}'';'];
%
refkey = 'Bastos2022'; type = 'MasterThesis'; bib = [ ...
'author = {Bastos, Ana R. P.}, ' ...
'year = {2022}, ' ...
'title = {CaracterizaÃ§Ã£o produtiva e reprodutiva da raÃ§a {Aberdeen}-{Angus} em {Portugal} no perÃ­odo 2014-2020}, ' ...
'school = {Universidade de Lisboa, Faculdade de Medicina VeterinÃ¡ria. Instituto Superior de Agronomia}, '
];
metaData.biblist.(refkey) = ['''@', type, '{', refkey, ', ' bib, '}'';'];
%
refkey = 'FAO2024'; type = 'misc'; bib = [...
    'title = "Domestic Animal Diversity Information System ({DAD-IS}) website",' ...
    'author = "{Food and Agriculture Organization of the United nations}",' ...
'howpublished = \url{https://www.fao.org/dad-is/browse-by-country-and-species/en/},"' ...
'year = "cited December 2022"'];
metaData.biblist.(refkey) = ['''@', type, '{', refkey, ', ' bib, '}'';'];
%
$packing_block
