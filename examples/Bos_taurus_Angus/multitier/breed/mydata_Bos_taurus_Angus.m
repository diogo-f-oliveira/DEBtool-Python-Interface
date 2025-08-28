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
%% Time vs Group daily feed consumption data

data.tJX_grp_Pen_2 = [0 45.43; 1 43.88; 2 26.68; 3 46.87; 4 40.24; 5 41.11; 6 41.15; 7 44.57; 8 45.67; 9 47.08; 10 41.6; 11 33.54; 12 47.22; 13 40.4; 14 38.04; 15 40.91; 16 36.2; 17 38.47; 18 38.95; 19 38.89; 20 40.95; 21 30.58; 22 37.61; 23 48.26; 24 41.03; 25 44.06; 26 43.23; 27 47.73; 28 41.82; 29 43.78; 30 29.79; 31 37.26; 32 29.83; 33 39.34; 34 45.31; 35 36.18; 36 44.02; 37 41.3; 38 43.11; 39 49.12; 40 42.88; 41 41.72; 42 45.65; 43 45.49; 44 44.04; 45 47.26; 46 45.33; 47 49.18; 48 46.08; 49 45.88; 50 47.81; 51 48.36; 52 50.03; 53 51.46; 54 44.68; 55 44.68; 56 39.02; 57 41.58; 58 48.02; 59 42.64; 60 48.65; 61 48.65; 62 45.12; 63 45.12; 64 48.69; 65 55.53; 66 48.89; 67 50.85; 68 54.41; 69 43.74; 70 43.74; 71 53.53; 72 56.51; 73 52.39; 74 54.31; 75 48.46; 76 56.28; 77 57.18; 78 55.06; 79 51.8; 80 59.42; 81 53.68; 82 56.02; 83 56.02];
init.tJX_grp_Pen_2 = struct('PT424401157', 469, 'PT433843806', 507, 'PT624139868', 464, 'PT833653644', 548, 'PT933843912', 545); units.init.tJX_grp_Pen_2 = 'kg'; label.init.tJX_grp_Pen_2 = 'Initial weights for the individuals in the group';
units.tJX_grp_Pen_2 = {'d', 'kg'}; label.tJX_grp_Pen_2 = {'Time since start', 'Daily food consumption of group during test'}; title.tJX_grp_Pen_2 = 'Daily feed consumption of pen Pen_2'; comment.tJX_grp_Pen_2 = 'Data from GreenBeef trial 1, pen Pen_2'; bibkey.tJX_grp_Pen_2 = 'GreenBeefTrial1';

data.tJX_grp_Pen_3 = [0 44.62; 1 44.22; 2 49.87; 3 51.94; 4 50.32; 5 48.06; 6 50.56; 7 43.44; 8 44.01; 9 44.13; 10 45.3; 11 46.98; 12 46.89; 13 48.1; 14 43.96; 15 44.82; 16 49.82; 17 49.13; 18 49.63; 19 46.79; 20 57.49; 21 45.73; 22 45.38; 23 53.4; 24 47.63; 25 53.92; 26 48.62; 27 43.62; 28 51.38; 29 46.98; 30 45.08; 31 52.75; 32 49.09; 33 46.85; 34 47.37; 35 54.65; 36 45.94; 37 47.15; 38 49.74; 39 52.24; 40 50.86; 41 53.62; 42 53.62; 43 56.46; 44 54.56; 45 53.27; 46 54.22; 47 56.37; 48 57.15; 49 52.06; 50 55.25; 51 62.5; 52 62.06; 53 56.63; 54 57.67; 55 57.67; 56 57.58; 57 56.2; 58 55.34; 59 55.17; 60 59.48; 61 59.48; 62 64.91; 63 64.91; 64 50.94; 65 51.89; 66 53.96; 67 60.25; 68 49.69; 69 52.41; 70 52.41; 71 55.43; 72 62.32; 73 56.12; 74 56.29; 75 56.37; 76 57.15; 77 58.44; 78 55.6; 79 52.06; 80 56.72; 81 55.25; 82 55.99; 83 55.99];
init.tJX_grp_Pen_3 = struct('PT333842562', 515, 'PT524401180', 496, 'PT533987885', 436, 'PT833653649', 535, 'PT933843894', 508); units.init.tJX_grp_Pen_3 = 'kg'; label.init.tJX_grp_Pen_3 = 'Initial weights for the individuals in the group';
units.tJX_grp_Pen_3 = {'d', 'kg'}; label.tJX_grp_Pen_3 = {'Time since start', 'Daily food consumption of group during test'}; title.tJX_grp_Pen_3 = 'Daily feed consumption of pen Pen_3'; comment.tJX_grp_Pen_3 = 'Data from GreenBeef trial 1, pen Pen_3'; bibkey.tJX_grp_Pen_3 = 'GreenBeefTrial1';

data.tJX_grp_Pen_4 = [0 45.31; 1 46.38; 2 50.99; 3 50.73; 4 49.98; 5 53.4; 6 48.49; 7 48.1; 8 50.04; 9 49.82; 10 47.02; 11 45.17; 12 49.82; 13 47.07; 14 46.72; 15 45.43; 16 47.58; 17 46.2; 18 48.43; 19 43.6; 20 57.75; 21 51.5; 22 50.64; 23 60.38; 24 51.42; 25 56.16; 26 54.31; 27 55.86; 28 53.79; 29 49.39; 30 49.22; 31 55.94; 32 53.4; 33 52.88; 34 47.28; 35 56.2; 36 58.18; 37 54.39; 38 53.7; 39 61.2; 40 56.03; 41 54.22; 42 53.36; 43 54.65; 44 47.93; 45 50.25; 46 51.98; 47 54.74; 48 55.86; 49 53.36; 50 54.65; 51 62.84; 52 66.72; 53 57.88; 54 56.72; 55 56.72; 56 55.17; 57 58.44; 58 55.34; 59 56.63; 60 65.77; 61 65.77; 62 54.82; 63 54.82; 64 60.08; 65 55.51; 66 65.08; 67 60.86; 68 58.92; 69 60.94; 70 60.94; 71 52.32; 72 52.24; 73 52.06; 74 50.08; 75 54.82; 76 57.58; 77 56.81; 78 58.27; 79 59.39; 80 56.37; 81 62.93; 82 59.74; 83 59.74];
init.tJX_grp_Pen_4 = struct('PT224401177', 562, 'PT524956505', 542, 'PT533843896', 480, 'PT924401183', 510, 'PT933602927', 426); units.init.tJX_grp_Pen_4 = 'kg'; label.init.tJX_grp_Pen_4 = 'Initial weights for the individuals in the group';
units.tJX_grp_Pen_4 = {'d', 'kg'}; label.tJX_grp_Pen_4 = {'Time since start', 'Daily food consumption of group during test'}; title.tJX_grp_Pen_4 = 'Daily feed consumption of pen Pen_4'; comment.tJX_grp_Pen_4 = 'Data from GreenBeef trial 1, pen Pen_4'; bibkey.tJX_grp_Pen_4 = 'GreenBeefTrial1';

data.tJX_grp_Pen_5 = [0 50.54; 1 49.18; 2 54.16; 3 50.4; 4 44.68; 5 46.69; 6 54.78; 7 52.23; 8 49.56; 9 52.82; 10 51.15; 11 36.73; 12 46.9; 13 40.68; 14 40.71; 15 43.31; 16 50.74; 17 43.98; 18 44.84; 19 50.21; 20 51.84; 21 33.68; 22 45.75; 23 43.31; 24 41.66; 25 50.81; 26 46.53; 27 47.02; 28 50.54; 29 42.52; 30 28.06; 31 41.5; 32 39.5; 33 41.42; 34 38.32; 35 40.07; 36 40.48; 37 37.73; 38 38.55; 39 43.31; 40 41.5; 41 46.63; 42 43.37; 43 51.62; 44 37.83; 45 49.38; 46 45.57; 47 49.42; 48 40.54; 49 43.49; 50 39.56; 51 43.29; 52 43.23; 53 47.51; 54 45.82; 55 45.82; 56 52.58; 57 51.76; 58 43.07; 59 53.37; 60 53.68; 61 53.68; 62 52.31; 63 52.31; 64 56.4; 65 50.15; 66 56.28; 67 54.39; 68 55.59; 69 49.16; 70 49.16; 71 55.49; 72 57.54; 73 55.22; 74 53.57; 75 52.54; 76 56.79; 77 48.34; 78 49.64; 79 42.56; 80 48.77; 81 42.09; 82 48.34; 83 48.34];
init.tJX_grp_Pen_5 = struct('PT033634130', 453, 'PT233843883', 506, 'PT333653651', 536, 'PT533358890', 477, 'PT724523831', 485); units.init.tJX_grp_Pen_5 = 'kg'; label.init.tJX_grp_Pen_5 = 'Initial weights for the individuals in the group';
units.tJX_grp_Pen_5 = {'d', 'kg'}; label.tJX_grp_Pen_5 = {'Time since start', 'Daily food consumption of group during test'}; title.tJX_grp_Pen_5 = 'Daily feed consumption of pen Pen_5'; comment.tJX_grp_Pen_5 = 'Data from GreenBeef trial 1, pen Pen_5'; bibkey.tJX_grp_Pen_5 = 'GreenBeefTrial1';



% group data types
metaData.group_data_types = {'tJX_grp'}; 


% Struct with form tier_groups.(tier_name) = list_of_groups_of_tier
data.tier_groups = 10; units.tier_groups = '-'; label.tier_groups = 'Dummy variable'; 
tiers.tier_groups = struct('breed', {{}}, 'diet', {{}}, 'individual', {{'Pen_2', 'Pen_3', 'Pen_4', 'Pen_5'}}); units.tiers.tier_groups = '-'; label.tiers.tier_groups = 'List of groups ids for each tier'; 


%% Entity data
%% Time vs Weight data 

data.tW_PT424401157 = [0 469; 14 482; 21 486; 35 512; 50 540; 63 549; 83 571];
init.tW_PT424401157 = 469; units.init.tW_PT424401157 = 'kg'; label.init.tW_PT424401157 = 'Initial weight';
units.tW_PT424401157 = {'d', 'kg'}; label.tW_PT424401157 = {'Time since start', 'Wet weight'}; title.tW_PT424401157 = 'Growth curve of individual PT424401157'; comment.tW_PT424401157 = 'Data from GreenBeef trial 1, individual PT424401157'; bibkey.tW_PT424401157 = 'GreenBeefTrial1';

data.tW_PT624139868 = [0 464; 14 470; 21 480; 35 508; 50 542; 63 558; 83 582];
init.tW_PT624139868 = 464; units.init.tW_PT624139868 = 'kg'; label.init.tW_PT624139868 = 'Initial weight';
units.tW_PT624139868 = {'d', 'kg'}; label.tW_PT624139868 = {'Time since start', 'Wet weight'}; title.tW_PT624139868 = 'Growth curve of individual PT624139868'; comment.tW_PT624139868 = 'Data from GreenBeef trial 1, individual PT624139868'; bibkey.tW_PT624139868 = 'GreenBeefTrial1';

data.tW_PT833653649 = [0 535; 14 546; 21 557; 35 586; 50 613; 63 641; 83 656];
init.tW_PT833653649 = 535; units.init.tW_PT833653649 = 'kg'; label.init.tW_PT833653649 = 'Initial weight';
units.tW_PT833653649 = {'d', 'kg'}; label.tW_PT833653649 = {'Time since start', 'Wet weight'}; title.tW_PT833653649 = 'Growth curve of individual PT833653649'; comment.tW_PT833653649 = 'Data from GreenBeef trial 1, individual PT833653649'; bibkey.tW_PT833653649 = 'GreenBeefTrial1';

data.tW_PT533843896 = [0 480; 14 492; 21 506; 35 536; 50 551; 63 574; 83 586];
init.tW_PT533843896 = 480; units.init.tW_PT533843896 = 'kg'; label.init.tW_PT533843896 = 'Initial weight';
units.tW_PT533843896 = {'d', 'kg'}; label.tW_PT533843896 = {'Time since start', 'Wet weight'}; title.tW_PT533843896 = 'Growth curve of individual PT533843896'; comment.tW_PT533843896 = 'Data from GreenBeef trial 1, individual PT533843896'; bibkey.tW_PT533843896 = 'GreenBeefTrial1';

data.tW_PT933843894 = [0 508; 14 521; 21 534; 35 563; 50 583; 63 610; 83 639];
init.tW_PT933843894 = 508; units.init.tW_PT933843894 = 'kg'; label.init.tW_PT933843894 = 'Initial weight';
units.tW_PT933843894 = {'d', 'kg'}; label.tW_PT933843894 = {'Time since start', 'Wet weight'}; title.tW_PT933843894 = 'Growth curve of individual PT933843894'; comment.tW_PT933843894 = 'Data from GreenBeef trial 1, individual PT933843894'; bibkey.tW_PT933843894 = 'GreenBeefTrial1';

data.tW_PT433843806 = [0 507; 14 532; 21 532; 35 568; 50 600; 63 607; 83 628];
init.tW_PT433843806 = 507; units.init.tW_PT433843806 = 'kg'; label.init.tW_PT433843806 = 'Initial weight';
units.tW_PT433843806 = {'d', 'kg'}; label.tW_PT433843806 = {'Time since start', 'Wet weight'}; title.tW_PT433843806 = 'Growth curve of individual PT433843806'; comment.tW_PT433843806 = 'Data from GreenBeef trial 1, individual PT433843806'; bibkey.tW_PT433843806 = 'GreenBeefTrial1';

data.tW_PT333653651 = [0 536; 14 548; 21 561; 35 589; 50 603; 63 615; 83 632];
init.tW_PT333653651 = 536; units.init.tW_PT333653651 = 'kg'; label.init.tW_PT333653651 = 'Initial weight';
units.tW_PT333653651 = {'d', 'kg'}; label.tW_PT333653651 = {'Time since start', 'Wet weight'}; title.tW_PT333653651 = 'Growth curve of individual PT333653651'; comment.tW_PT333653651 = 'Data from GreenBeef trial 1, individual PT333653651'; bibkey.tW_PT333653651 = 'GreenBeefTrial1';

data.tW_PT224401177 = [0 562; 14 589; 21 597; 35 632; 50 660; 63 697; 83 723];
init.tW_PT224401177 = 562; units.init.tW_PT224401177 = 'kg'; label.init.tW_PT224401177 = 'Initial weight';
units.tW_PT224401177 = {'d', 'kg'}; label.tW_PT224401177 = {'Time since start', 'Wet weight'}; title.tW_PT224401177 = 'Growth curve of individual PT224401177'; comment.tW_PT224401177 = 'Data from GreenBeef trial 1, individual PT224401177'; bibkey.tW_PT224401177 = 'GreenBeefTrial1';

data.tW_PT724523831 = [0 485; 14 505; 21 510; 35 474; 50 504; 63 581; 83 565];
init.tW_PT724523831 = 485; units.init.tW_PT724523831 = 'kg'; label.init.tW_PT724523831 = 'Initial weight';
units.tW_PT724523831 = {'d', 'kg'}; label.tW_PT724523831 = {'Time since start', 'Wet weight'}; title.tW_PT724523831 = 'Growth curve of individual PT724523831'; comment.tW_PT724523831 = 'Data from GreenBeef trial 1, individual PT724523831'; bibkey.tW_PT724523831 = 'GreenBeefTrial1';

data.tW_PT333842562 = [0 515; 14 535; 21 539; 35 566; 50 594; 63 630; 83 652];
init.tW_PT333842562 = 515; units.init.tW_PT333842562 = 'kg'; label.init.tW_PT333842562 = 'Initial weight';
units.tW_PT333842562 = {'d', 'kg'}; label.tW_PT333842562 = {'Time since start', 'Wet weight'}; title.tW_PT333842562 = 'Growth curve of individual PT333842562'; comment.tW_PT333842562 = 'Data from GreenBeef trial 1, individual PT333842562'; bibkey.tW_PT333842562 = 'GreenBeefTrial1';

data.tW_PT833653644 = [0 548; 14 544; 21 553; 35 579; 50 603; 63 623; 83 652];
init.tW_PT833653644 = 548; units.init.tW_PT833653644 = 'kg'; label.init.tW_PT833653644 = 'Initial weight';
units.tW_PT833653644 = {'d', 'kg'}; label.tW_PT833653644 = {'Time since start', 'Wet weight'}; title.tW_PT833653644 = 'Growth curve of individual PT833653644'; comment.tW_PT833653644 = 'Data from GreenBeef trial 1, individual PT833653644'; bibkey.tW_PT833653644 = 'GreenBeefTrial1';

data.tW_PT533987885 = [0 436; 14 449; 21 460; 35 486; 50 502; 63 515; 83 542];
init.tW_PT533987885 = 436; units.init.tW_PT533987885 = 'kg'; label.init.tW_PT533987885 = 'Initial weight';
units.tW_PT533987885 = {'d', 'kg'}; label.tW_PT533987885 = {'Time since start', 'Wet weight'}; title.tW_PT533987885 = 'Growth curve of individual PT533987885'; comment.tW_PT533987885 = 'Data from GreenBeef trial 1, individual PT533987885'; bibkey.tW_PT533987885 = 'GreenBeefTrial1';

data.tW_PT524401180 = [0 496; 14 503; 21 508; 35 532; 50 560; 63 586; 83 610];
init.tW_PT524401180 = 496; units.init.tW_PT524401180 = 'kg'; label.init.tW_PT524401180 = 'Initial weight';
units.tW_PT524401180 = {'d', 'kg'}; label.tW_PT524401180 = {'Time since start', 'Wet weight'}; title.tW_PT524401180 = 'Growth curve of individual PT524401180'; comment.tW_PT524401180 = 'Data from GreenBeef trial 1, individual PT524401180'; bibkey.tW_PT524401180 = 'GreenBeefTrial1';

data.tW_PT933843912 = [0 545; 14 561; 21 565; 35 581; 50 616; 63 649; 83 668];
init.tW_PT933843912 = 545; units.init.tW_PT933843912 = 'kg'; label.init.tW_PT933843912 = 'Initial weight';
units.tW_PT933843912 = {'d', 'kg'}; label.tW_PT933843912 = {'Time since start', 'Wet weight'}; title.tW_PT933843912 = 'Growth curve of individual PT933843912'; comment.tW_PT933843912 = 'Data from GreenBeef trial 1, individual PT933843912'; bibkey.tW_PT933843912 = 'GreenBeefTrial1';

data.tW_PT533358890 = [0 477; 14 493; 21 498; 35 529; 50 551; 63 586; 83 621];
init.tW_PT533358890 = 477; units.init.tW_PT533358890 = 'kg'; label.init.tW_PT533358890 = 'Initial weight';
units.tW_PT533358890 = {'d', 'kg'}; label.tW_PT533358890 = {'Time since start', 'Wet weight'}; title.tW_PT533358890 = 'Growth curve of individual PT533358890'; comment.tW_PT533358890 = 'Data from GreenBeef trial 1, individual PT533358890'; bibkey.tW_PT533358890 = 'GreenBeefTrial1';

data.tW_PT924401183 = [0 510; 14 543; 21 555; 35 587; 50 624; 63 648; 83 685];
init.tW_PT924401183 = 510; units.init.tW_PT924401183 = 'kg'; label.init.tW_PT924401183 = 'Initial weight';
units.tW_PT924401183 = {'d', 'kg'}; label.tW_PT924401183 = {'Time since start', 'Wet weight'}; title.tW_PT924401183 = 'Growth curve of individual PT924401183'; comment.tW_PT924401183 = 'Data from GreenBeef trial 1, individual PT924401183'; bibkey.tW_PT924401183 = 'GreenBeefTrial1';

data.tW_PT524956505 = [0 542; 14 567; 21 577; 35 603; 50 638; 63 664; 83 707];
init.tW_PT524956505 = 542; units.init.tW_PT524956505 = 'kg'; label.init.tW_PT524956505 = 'Initial weight';
units.tW_PT524956505 = {'d', 'kg'}; label.tW_PT524956505 = {'Time since start', 'Wet weight'}; title.tW_PT524956505 = 'Growth curve of individual PT524956505'; comment.tW_PT524956505 = 'Data from GreenBeef trial 1, individual PT524956505'; bibkey.tW_PT524956505 = 'GreenBeefTrial1';

data.tW_PT233843883 = [0 506; 14 525; 21 533; 35 561; 50 583; 63 592; 83 620];
init.tW_PT233843883 = 506; units.init.tW_PT233843883 = 'kg'; label.init.tW_PT233843883 = 'Initial weight';
units.tW_PT233843883 = {'d', 'kg'}; label.tW_PT233843883 = {'Time since start', 'Wet weight'}; title.tW_PT233843883 = 'Growth curve of individual PT233843883'; comment.tW_PT233843883 = 'Data from GreenBeef trial 1, individual PT233843883'; bibkey.tW_PT233843883 = 'GreenBeefTrial1';

data.tW_PT033634130 = [0 453; 14 468; 21 471; 35 500; 50 517; 63 526; 83 556];
init.tW_PT033634130 = 453; units.init.tW_PT033634130 = 'kg'; label.init.tW_PT033634130 = 'Initial weight';
units.tW_PT033634130 = {'d', 'kg'}; label.tW_PT033634130 = {'Time since start', 'Wet weight'}; title.tW_PT033634130 = 'Growth curve of individual PT033634130'; comment.tW_PT033634130 = 'Data from GreenBeef trial 1, individual PT033634130'; bibkey.tW_PT033634130 = 'GreenBeefTrial1';

data.tW_PT933602927 = [0 426; 14 450; 21 462; 35 482; 50 497; 63 524; 83 539];
init.tW_PT933602927 = 426; units.init.tW_PT933602927 = 'kg'; label.init.tW_PT933602927 = 'Initial weight';
units.tW_PT933602927 = {'d', 'kg'}; label.tW_PT933602927 = {'Time since start', 'Wet weight'}; title.tW_PT933602927 = 'Growth curve of individual PT933602927'; comment.tW_PT933602927 = 'Data from GreenBeef trial 1, individual PT933602927'; bibkey.tW_PT933602927 = 'GreenBeefTrial1';



% entity data types
metaData.entity_data_types = {'tW'}; 


% Cell array of entity_ids
data.entity_list = 10; units.entity_list = '-'; label.entity_list = 'Dummy variable'; 
tiers.entity_list = {'male'}; units.tiers.entity_list = '-'; label.tiers.entity_list = 'List of entities'; 
metaData.entity_list = tiers.entity_list; % Save in metaData to use in pars_init.m

% Struct with form tier_entities.(tier_name) = list_of_entities_of_tier
data.tier_entities = 10; units.tier_entities = '-'; label.tier_entities = 'Dummy variable'; 
tiers.tier_entities = struct('breed', {{'male'}}, 'diet', {{'CTRL', 'TMR'}}, 'individual', {{'PT424401157', 'PT624139868', 'PT833653649', 'PT533843896', 'PT933843894', 'PT433843806', 'PT333653651', 'PT224401177', 'PT724523831', 'PT333842562', 'PT833653644', 'PT533987885', 'PT524401180', 'PT933843912', 'PT533358890', 'PT924401183', 'PT524956505', 'PT233843883', 'PT033634130', 'PT933602927'}}); units.tiers.tier_entities = '-'; label.tiers.tier_entities = 'List of entity ids for each tier'; 


% Struct with form groups_of_entity.(entity_id) = list_of_groups_ids_entity_belongs_to
data.groups_of_entity = 10; units.groups_of_entity = '-'; label.groups_of_entity = 'Dummy variable'; 
tiers.groups_of_entity = struct('PT424401157', {{'Pen_2'}}, 'PT624139868', {{'Pen_2'}}, 'PT833653649', {{'Pen_3'}}, 'PT533843896', {{'Pen_4'}}, 'PT933843894', {{'Pen_3'}}, 'PT433843806', {{'Pen_2'}}, 'PT333653651', {{'Pen_5'}}, 'PT224401177', {{'Pen_4'}}, 'PT724523831', {{'Pen_5'}}, 'PT333842562', {{'Pen_3'}}, 'PT833653644', {{'Pen_2'}}, 'PT533987885', {{'Pen_3'}}, 'PT524401180', {{'Pen_3'}}, 'PT933843912', {{'Pen_2'}}, 'PT533358890', {{'Pen_5'}}, 'PT924401183', {{'Pen_4'}}, 'PT524956505', {{'Pen_4'}}, 'PT233843883', {{'Pen_5'}}, 'PT033634130', {{'Pen_5'}}, 'PT933602927', {{'Pen_4'}}); units.tiers.groups_of_entity = '-'; label.tiers.groups_of_entity = 'Groups each entity belongs to'; 

    
% Tier subtree
% Lists entities that are below entity_id for each tier below
% Struct with form tier_subtree.(entity_id).(tier_name) = list_of_entities_below
data.tier_subtree = 10; units.tier_subtree = '-'; label.tier_subtree = 'Dummy variable'; 
tiers.tier_subtree = struct('male', struct('diet', {{'CTRL', 'TMR'}}, 'individual', {{'PT424401157', 'PT624139868', 'PT833653649', 'PT533843896', 'PT933843894', 'PT433843806', 'PT333653651', 'PT224401177', 'PT724523831', 'PT333842562', 'PT833653644', 'PT533987885', 'PT524401180', 'PT933843912', 'PT533358890', 'PT924401183', 'PT524956505', 'PT233843883', 'PT033634130', 'PT933602927'}})); units.tiers.tier_subtree = '-'; label.tiers.tier_subtree = 'Tier subtree'; 


%% Tier parameters
% Cell array with tier parameters
data.tier_pars = 10; units.tier_pars = '-'; label.tier_pars = 'Dummy variable'; comment.tier_pars = 'Tier parameters'; 
tiers.tier_pars = {'p_Am', 'kap_X', 'p_M', 'v', 'kap', 'E_G', 'E_Hb', 'E_Hx', 'E_Hp', 'h_a', 't_0', 'del_M', 'p_Am_f', 'E_Hp_f'}; units.tiers.tier_pars = '-'; label.tiers.tier_pars = 'Tier parameters'; 
metaData.tier_pars = tiers.tier_pars; % Save in metaData to use in pars_init.m

% Initial values for each tier parameter and entity
% Struct with form tier_par_init_values.(par).(entity_id) = value;
metaData.tier_par_init_values = struct('p_Am', struct('male', 5000), 'kap_X', struct('male', 0.2), 'p_M', struct('male', 80), 'v', struct('male', 0.05), 'kap', struct('male', 0.97), 'E_G', struct('male', 7800), 'E_Hb', struct('male', 2000000.0), 'E_Hx', struct('male', 20000000.0), 'E_Hp', struct('male', 60000000.0), 'h_a', struct('male', 5e-10), 't_0', struct('male', 80), 'del_M', struct('male', 0.15), 'p_Am_f', struct('male', 4500), 'E_Hp_f', struct('male', 60000000.0)); 


%% Set temperature data and remove weights for dummy variables
weights = setweights(data, []);

metaData.data_fields = fieldnames(data);
temp = struct();
for i=1:length(metaData.data_fields)
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

