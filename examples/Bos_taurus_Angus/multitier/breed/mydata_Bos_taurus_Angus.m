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

data.tJX_grp_Pen_2 = [0.0 45.43; 1.0 43.88; 2.0 26.68; 3.0 46.87; 4.0 40.24; 5.0 41.11; 6.0 41.15; 7.0 44.57; 8.0 45.67; 9.0 47.08; 10.0 41.6; 11.0 33.54; 12.0 47.22; 13.0 40.4; 14.0 38.04; 15.0 40.91; 16.0 36.2; 17.0 38.47; 18.0 38.95; 19.0 38.89; 20.0 40.95; 21.0 30.58; 22.0 37.61; 23.0 48.26; 24.0 41.03; 25.0 44.06; 26.0 43.23; 27.0 47.73; 28.0 41.82; 29.0 43.78; 30.0 29.79; 31.0 37.26; 32.0 29.83; 33.0 39.34; 34.0 45.31; 35.0 36.18; 36.0 44.02; 37.0 41.3; 38.0 43.11; 39.0 49.12; 40.0 42.88; 41.0 41.72; 42.0 45.65; 43.0 45.49; 44.0 44.04; 45.0 47.26; 46.0 45.33; 47.0 49.18; 48.0 46.08; 49.0 45.88; 50.0 47.81; 51.0 48.36; 52.0 50.03; 53.0 51.46; 54.0 44.68; 55.0 44.68; 56.0 39.02; 57.0 41.58; 58.0 48.02; 59.0 42.64; 60.0 48.65; 61.0 48.65; 62.0 45.12; 63.0 45.12; 64.0 48.69; 65.0 55.53; 66.0 48.89; 67.0 50.85; 68.0 54.41; 69.0 43.74; 70.0 43.74; 71.0 53.53; 72.0 56.51; 73.0 52.39; 74.0 54.31; 75.0 48.46; 76.0 56.28; 77.0 57.18; 78.0 55.06; 79.0 51.8; 80.0 59.42; 81.0 53.68; 82.0 56.02; 83.0 56.02];
units.tJX_grp_Pen_2 = {'d', 'kg'}; label.tJX_grp_Pen_2 = {'Time since start', 'Daily food consumption of group during test'}; comment.tJX_grp_Pen_2 = 'Data from GreenBeef trial 1'; title.tJX_grp_Pen_2 = 'Daily feed consumption,  Pen_2'; bibkey.tJX_grp_Pen_2 = 'GreenBeefTrial1';
init.tJX_grp_Pen_2 = struct('PT424401157', 469, 'PT433843806', 507, 'PT624139868', 464, 'PT833653644', 548, 'PT933843912', 545); units.init.tJX_grp_Pen_2 = 'kg'; label.init.tJX_grp_Pen_2 = 'Initial weights for the individuals in the group'; 


data.tJX_grp_Pen_3 = [0.0 44.62; 1.0 44.22; 2.0 49.87; 3.0 51.94; 4.0 50.32; 5.0 48.06; 6.0 50.56; 7.0 43.44; 8.0 44.01; 9.0 44.13; 10.0 45.3; 11.0 46.98; 12.0 46.89; 13.0 48.1; 14.0 43.96; 15.0 44.82; 16.0 49.82; 17.0 49.13; 18.0 49.63; 19.0 46.79; 20.0 57.49; 21.0 45.73; 22.0 45.38; 23.0 53.4; 24.0 47.63; 25.0 53.92; 26.0 48.62; 27.0 43.62; 28.0 51.38; 29.0 46.98; 30.0 45.08; 31.0 52.75; 32.0 49.09; 33.0 46.85; 34.0 47.37; 35.0 54.65; 36.0 45.94; 37.0 47.15; 38.0 49.74; 39.0 52.24; 40.0 50.86; 41.0 53.62; 42.0 53.62; 43.0 56.46; 44.0 54.56; 45.0 53.27; 46.0 54.22; 47.0 56.37; 48.0 57.15; 49.0 52.06; 50.0 55.25; 51.0 62.5; 52.0 62.06; 53.0 56.63; 54.0 57.67; 55.0 57.67; 56.0 57.58; 57.0 56.2; 58.0 55.34; 59.0 55.17; 60.0 59.48; 61.0 59.48; 62.0 64.91; 63.0 64.91; 64.0 50.94; 65.0 51.89; 66.0 53.96; 67.0 60.25; 68.0 49.69; 69.0 52.41; 70.0 52.41; 71.0 55.43; 72.0 62.32; 73.0 56.12; 74.0 56.29; 75.0 56.37; 76.0 57.15; 77.0 58.44; 78.0 55.6; 79.0 52.06; 80.0 56.72; 81.0 55.25; 82.0 55.99; 83.0 55.99];
units.tJX_grp_Pen_3 = {'d', 'kg'}; label.tJX_grp_Pen_3 = {'Time since start', 'Daily food consumption of group during test'}; comment.tJX_grp_Pen_3 = 'Data from GreenBeef trial 1'; title.tJX_grp_Pen_3 = 'Daily feed consumption,  Pen_3'; bibkey.tJX_grp_Pen_3 = 'GreenBeefTrial1';
init.tJX_grp_Pen_3 = struct('PT333842562', 515, 'PT524401180', 496, 'PT533987885', 436, 'PT833653649', 535, 'PT933843894', 508); units.init.tJX_grp_Pen_3 = 'kg'; label.init.tJX_grp_Pen_3 = 'Initial weights for the individuals in the group'; 


data.tJX_grp_Pen_4 = [0.0 45.31; 1.0 46.38; 2.0 50.99; 3.0 50.73; 4.0 49.98; 5.0 53.4; 6.0 48.49; 7.0 48.1; 8.0 50.04; 9.0 49.82; 10.0 47.02; 11.0 45.17; 12.0 49.82; 13.0 47.07; 14.0 46.72; 15.0 45.43; 16.0 47.58; 17.0 46.2; 18.0 48.43; 19.0 43.6; 20.0 57.75; 21.0 51.5; 22.0 50.64; 23.0 60.38; 24.0 51.42; 25.0 56.16; 26.0 54.31; 27.0 55.86; 28.0 53.79; 29.0 49.39; 30.0 49.22; 31.0 55.94; 32.0 53.4; 33.0 52.88; 34.0 47.28; 35.0 56.2; 36.0 58.18; 37.0 54.39; 38.0 53.7; 39.0 61.2; 40.0 56.03; 41.0 54.22; 42.0 53.36; 43.0 54.65; 44.0 47.93; 45.0 50.25; 46.0 51.98; 47.0 54.74; 48.0 55.86; 49.0 53.36; 50.0 54.65; 51.0 62.84; 52.0 66.72; 53.0 57.88; 54.0 56.72; 55.0 56.72; 56.0 55.17; 57.0 58.44; 58.0 55.34; 59.0 56.63; 60.0 65.77; 61.0 65.77; 62.0 54.82; 63.0 54.82; 64.0 60.08; 65.0 55.51; 66.0 65.08; 67.0 60.86; 68.0 58.92; 69.0 60.94; 70.0 60.94; 71.0 52.32; 72.0 52.24; 73.0 52.06; 74.0 50.08; 75.0 54.82; 76.0 57.58; 77.0 56.81; 78.0 58.27; 79.0 59.39; 80.0 56.37; 81.0 62.93; 82.0 59.74; 83.0 59.74];
units.tJX_grp_Pen_4 = {'d', 'kg'}; label.tJX_grp_Pen_4 = {'Time since start', 'Daily food consumption of group during test'}; comment.tJX_grp_Pen_4 = 'Data from GreenBeef trial 1'; title.tJX_grp_Pen_4 = 'Daily feed consumption,  Pen_4'; bibkey.tJX_grp_Pen_4 = 'GreenBeefTrial1';
init.tJX_grp_Pen_4 = struct('PT224401177', 562, 'PT524956505', 542, 'PT533843896', 480, 'PT924401183', 510, 'PT933602927', 426); units.init.tJX_grp_Pen_4 = 'kg'; label.init.tJX_grp_Pen_4 = 'Initial weights for the individuals in the group'; 


data.tJX_grp_Pen_5 = [0.0 50.54; 1.0 49.18; 2.0 54.16; 3.0 50.4; 4.0 44.68; 5.0 46.69; 6.0 54.78; 7.0 52.23; 8.0 49.56; 9.0 52.82; 10.0 51.15; 11.0 36.73; 12.0 46.9; 13.0 40.68; 14.0 40.71; 15.0 43.31; 16.0 50.74; 17.0 43.98; 18.0 44.84; 19.0 50.21; 20.0 51.84; 21.0 33.68; 22.0 45.75; 23.0 43.31; 24.0 41.66; 25.0 50.81; 26.0 46.53; 27.0 47.02; 28.0 50.54; 29.0 42.52; 30.0 28.06; 31.0 41.5; 32.0 39.5; 33.0 41.42; 34.0 38.32; 35.0 40.07; 36.0 40.48; 37.0 37.73; 38.0 38.55; 39.0 43.31; 40.0 41.5; 41.0 46.63; 42.0 43.37; 43.0 51.62; 44.0 37.83; 45.0 49.38; 46.0 45.57; 47.0 49.42; 48.0 40.54; 49.0 43.49; 50.0 39.56; 51.0 43.29; 52.0 43.23; 53.0 47.51; 54.0 45.82; 55.0 45.82; 56.0 52.58; 57.0 51.76; 58.0 43.07; 59.0 53.37; 60.0 53.68; 61.0 53.68; 62.0 52.31; 63.0 52.31; 64.0 56.4; 65.0 50.15; 66.0 56.28; 67.0 54.39; 68.0 55.59; 69.0 49.16; 70.0 49.16; 71.0 55.49; 72.0 57.54; 73.0 55.22; 74.0 53.57; 75.0 52.54; 76.0 56.79; 77.0 48.34; 78.0 49.64; 79.0 42.56; 80.0 48.77; 81.0 42.09; 82.0 48.34; 83.0 48.34];
units.tJX_grp_Pen_5 = {'d', 'kg'}; label.tJX_grp_Pen_5 = {'Time since start', 'Daily food consumption of group during test'}; comment.tJX_grp_Pen_5 = 'Data from GreenBeef trial 1'; title.tJX_grp_Pen_5 = 'Daily feed consumption,  Pen_5'; bibkey.tJX_grp_Pen_5 = 'GreenBeefTrial1';
init.tJX_grp_Pen_5 = struct('PT033634130', 453, 'PT233843883', 506, 'PT333653651', 536, 'PT533358890', 477, 'PT724523831', 485); units.init.tJX_grp_Pen_5 = 'kg'; label.init.tJX_grp_Pen_5 = 'Initial weights for the individuals in the group'; 




% group data types
metaData.group_data_types = {'tJX_grp'}; 


% Struct with form tier_groups.(tier_name) = list_of_groups_of_tier
data.tier_groups = 10; units.tier_groups = '-'; label.tier_groups = 'Tier structure variable'; 
tiers.tier_groups = struct('breed', {{}}, 'diet', {{}}, 'individual', {{'Pen_2', 'Pen_3', 'Pen_4', 'Pen_5'}}); units.tiers.tier_groups = '-'; label.tiers.tier_groups = 'List of groups ids for each tier'; 


%% Entity data
%% Time vs Milk production data 

data.DMD_CTRL = 0.789;
units.DMD_CTRL = '-'; label.DMD_CTRL = 'Digestibility'; comment.DMD_CTRL = 'Data from GreenBeef trial 1'; title.DMD_CTRL = ', diet CTRL'; bibkey.DMD_CTRL = 'GreenBeefTrial1';

data.DMD_TMR = 0.694;
units.DMD_TMR = '-'; label.DMD_TMR = 'Digestibility'; comment.DMD_TMR = 'Data from GreenBeef trial 1'; title.DMD_TMR = ', diet TMR'; bibkey.DMD_TMR = 'GreenBeefTrial1';


%% Time vs Weight data 

data.tW_PT533358890 = [0 477; 14 493; 21 498; 35 529; 50 551; 63 586; 83 621];
units.tW_PT533358890 = {'d', 'kg'}; label.tW_PT533358890 = {'Time since start', 'Wet weight'}; comment.tW_PT533358890 = 'Data from GreenBeef trial 1'; title.tW_PT533358890 = 'Wet weight growth curve, individual PT533358890'; bibkey.tW_PT533358890 = 'GreenBeefTrial1';
init.tW_PT533358890 = 477; units.init.tW_PT533358890 = 'kg'; label.init.tW_PT533358890 = 'Initial weight'; 


data.tW_PT933602927 = [0 426; 14 450; 21 462; 35 482; 50 497; 63 524; 83 539];
units.tW_PT933602927 = {'d', 'kg'}; label.tW_PT933602927 = {'Time since start', 'Wet weight'}; comment.tW_PT933602927 = 'Data from GreenBeef trial 1'; title.tW_PT933602927 = 'Wet weight growth curve, individual PT933602927'; bibkey.tW_PT933602927 = 'GreenBeefTrial1';
init.tW_PT933602927 = 426; units.init.tW_PT933602927 = 'kg'; label.init.tW_PT933602927 = 'Initial weight'; 


data.tW_PT333842562 = [0 515; 14 535; 21 539; 35 566; 50 594; 63 630; 83 652];
units.tW_PT333842562 = {'d', 'kg'}; label.tW_PT333842562 = {'Time since start', 'Wet weight'}; comment.tW_PT333842562 = 'Data from GreenBeef trial 1'; title.tW_PT333842562 = 'Wet weight growth curve, individual PT333842562'; bibkey.tW_PT333842562 = 'GreenBeefTrial1';
init.tW_PT333842562 = 515; units.init.tW_PT333842562 = 'kg'; label.init.tW_PT333842562 = 'Initial weight'; 


data.tW_PT233843883 = [0 506; 14 525; 21 533; 35 561; 50 583; 63 592; 83 620];
units.tW_PT233843883 = {'d', 'kg'}; label.tW_PT233843883 = {'Time since start', 'Wet weight'}; comment.tW_PT233843883 = 'Data from GreenBeef trial 1'; title.tW_PT233843883 = 'Wet weight growth curve, individual PT233843883'; bibkey.tW_PT233843883 = 'GreenBeefTrial1';
init.tW_PT233843883 = 506; units.init.tW_PT233843883 = 'kg'; label.init.tW_PT233843883 = 'Initial weight'; 


data.tW_PT524401180 = [0 496; 14 503; 21 508; 35 532; 50 560; 63 586; 83 610];
units.tW_PT524401180 = {'d', 'kg'}; label.tW_PT524401180 = {'Time since start', 'Wet weight'}; comment.tW_PT524401180 = 'Data from GreenBeef trial 1'; title.tW_PT524401180 = 'Wet weight growth curve, individual PT524401180'; bibkey.tW_PT524401180 = 'GreenBeefTrial1';
init.tW_PT524401180 = 496; units.init.tW_PT524401180 = 'kg'; label.init.tW_PT524401180 = 'Initial weight'; 


data.tW_PT333653651 = [0 536; 14 548; 21 561; 35 589; 50 603; 63 615; 83 632];
units.tW_PT333653651 = {'d', 'kg'}; label.tW_PT333653651 = {'Time since start', 'Wet weight'}; comment.tW_PT333653651 = 'Data from GreenBeef trial 1'; title.tW_PT333653651 = 'Wet weight growth curve, individual PT333653651'; bibkey.tW_PT333653651 = 'GreenBeefTrial1';
init.tW_PT333653651 = 536; units.init.tW_PT333653651 = 'kg'; label.init.tW_PT333653651 = 'Initial weight'; 


data.tW_PT833653644 = [0 548; 14 544; 21 553; 35 579; 50 603; 63 623; 83 652];
units.tW_PT833653644 = {'d', 'kg'}; label.tW_PT833653644 = {'Time since start', 'Wet weight'}; comment.tW_PT833653644 = 'Data from GreenBeef trial 1'; title.tW_PT833653644 = 'Wet weight growth curve, individual PT833653644'; bibkey.tW_PT833653644 = 'GreenBeefTrial1';
init.tW_PT833653644 = 548; units.init.tW_PT833653644 = 'kg'; label.init.tW_PT833653644 = 'Initial weight'; 


data.tW_PT933843912 = [0 545; 14 561; 21 565; 35 581; 50 616; 63 649; 83 668];
units.tW_PT933843912 = {'d', 'kg'}; label.tW_PT933843912 = {'Time since start', 'Wet weight'}; comment.tW_PT933843912 = 'Data from GreenBeef trial 1'; title.tW_PT933843912 = 'Wet weight growth curve, individual PT933843912'; bibkey.tW_PT933843912 = 'GreenBeefTrial1';
init.tW_PT933843912 = 545; units.init.tW_PT933843912 = 'kg'; label.init.tW_PT933843912 = 'Initial weight'; 


data.tW_PT524956505 = [0 542; 14 567; 21 577; 35 603; 50 638; 63 664; 83 707];
units.tW_PT524956505 = {'d', 'kg'}; label.tW_PT524956505 = {'Time since start', 'Wet weight'}; comment.tW_PT524956505 = 'Data from GreenBeef trial 1'; title.tW_PT524956505 = 'Wet weight growth curve, individual PT524956505'; bibkey.tW_PT524956505 = 'GreenBeefTrial1';
init.tW_PT524956505 = 542; units.init.tW_PT524956505 = 'kg'; label.init.tW_PT524956505 = 'Initial weight'; 


data.tW_PT924401183 = [0 510; 14 543; 21 555; 35 587; 50 624; 63 648; 83 685];
units.tW_PT924401183 = {'d', 'kg'}; label.tW_PT924401183 = {'Time since start', 'Wet weight'}; comment.tW_PT924401183 = 'Data from GreenBeef trial 1'; title.tW_PT924401183 = 'Wet weight growth curve, individual PT924401183'; bibkey.tW_PT924401183 = 'GreenBeefTrial1';
init.tW_PT924401183 = 510; units.init.tW_PT924401183 = 'kg'; label.init.tW_PT924401183 = 'Initial weight'; 


data.tW_PT933843894 = [0 508; 14 521; 21 534; 35 563; 50 583; 63 610; 83 639];
units.tW_PT933843894 = {'d', 'kg'}; label.tW_PT933843894 = {'Time since start', 'Wet weight'}; comment.tW_PT933843894 = 'Data from GreenBeef trial 1'; title.tW_PT933843894 = 'Wet weight growth curve, individual PT933843894'; bibkey.tW_PT933843894 = 'GreenBeefTrial1';
init.tW_PT933843894 = 508; units.init.tW_PT933843894 = 'kg'; label.init.tW_PT933843894 = 'Initial weight'; 


data.tW_PT724523831 = [0 485; 14 505; 21 510; 35 474; 50 504; 63 581; 83 565];
units.tW_PT724523831 = {'d', 'kg'}; label.tW_PT724523831 = {'Time since start', 'Wet weight'}; comment.tW_PT724523831 = 'Data from GreenBeef trial 1'; title.tW_PT724523831 = 'Wet weight growth curve, individual PT724523831'; bibkey.tW_PT724523831 = 'GreenBeefTrial1';
init.tW_PT724523831 = 485; units.init.tW_PT724523831 = 'kg'; label.init.tW_PT724523831 = 'Initial weight'; 


data.tW_PT833653649 = [0 535; 14 546; 21 557; 35 586; 50 613; 63 641; 83 656];
units.tW_PT833653649 = {'d', 'kg'}; label.tW_PT833653649 = {'Time since start', 'Wet weight'}; comment.tW_PT833653649 = 'Data from GreenBeef trial 1'; title.tW_PT833653649 = 'Wet weight growth curve, individual PT833653649'; bibkey.tW_PT833653649 = 'GreenBeefTrial1';
init.tW_PT833653649 = 535; units.init.tW_PT833653649 = 'kg'; label.init.tW_PT833653649 = 'Initial weight'; 


data.tW_PT224401177 = [0 562; 14 589; 21 597; 35 632; 50 660; 63 697; 83 723];
units.tW_PT224401177 = {'d', 'kg'}; label.tW_PT224401177 = {'Time since start', 'Wet weight'}; comment.tW_PT224401177 = 'Data from GreenBeef trial 1'; title.tW_PT224401177 = 'Wet weight growth curve, individual PT224401177'; bibkey.tW_PT224401177 = 'GreenBeefTrial1';
init.tW_PT224401177 = 562; units.init.tW_PT224401177 = 'kg'; label.init.tW_PT224401177 = 'Initial weight'; 


data.tW_PT533987885 = [0 436; 14 449; 21 460; 35 486; 50 502; 63 515; 83 542];
units.tW_PT533987885 = {'d', 'kg'}; label.tW_PT533987885 = {'Time since start', 'Wet weight'}; comment.tW_PT533987885 = 'Data from GreenBeef trial 1'; title.tW_PT533987885 = 'Wet weight growth curve, individual PT533987885'; bibkey.tW_PT533987885 = 'GreenBeefTrial1';
init.tW_PT533987885 = 436; units.init.tW_PT533987885 = 'kg'; label.init.tW_PT533987885 = 'Initial weight'; 


data.tW_PT424401157 = [0 469; 14 482; 21 486; 35 512; 50 540; 63 549; 83 571];
units.tW_PT424401157 = {'d', 'kg'}; label.tW_PT424401157 = {'Time since start', 'Wet weight'}; comment.tW_PT424401157 = 'Data from GreenBeef trial 1'; title.tW_PT424401157 = 'Wet weight growth curve, individual PT424401157'; bibkey.tW_PT424401157 = 'GreenBeefTrial1';
init.tW_PT424401157 = 469; units.init.tW_PT424401157 = 'kg'; label.init.tW_PT424401157 = 'Initial weight'; 


data.tW_PT433843806 = [0 507; 14 532; 21 532; 35 568; 50 600; 63 607; 83 628];
units.tW_PT433843806 = {'d', 'kg'}; label.tW_PT433843806 = {'Time since start', 'Wet weight'}; comment.tW_PT433843806 = 'Data from GreenBeef trial 1'; title.tW_PT433843806 = 'Wet weight growth curve, individual PT433843806'; bibkey.tW_PT433843806 = 'GreenBeefTrial1';
init.tW_PT433843806 = 507; units.init.tW_PT433843806 = 'kg'; label.init.tW_PT433843806 = 'Initial weight'; 


data.tW_PT533843896 = [0 480; 14 492; 21 506; 35 536; 50 551; 63 574; 83 586];
units.tW_PT533843896 = {'d', 'kg'}; label.tW_PT533843896 = {'Time since start', 'Wet weight'}; comment.tW_PT533843896 = 'Data from GreenBeef trial 1'; title.tW_PT533843896 = 'Wet weight growth curve, individual PT533843896'; bibkey.tW_PT533843896 = 'GreenBeefTrial1';
init.tW_PT533843896 = 480; units.init.tW_PT533843896 = 'kg'; label.init.tW_PT533843896 = 'Initial weight'; 


data.tW_PT033634130 = [0 453; 14 468; 21 471; 35 500; 50 517; 63 526; 83 556];
units.tW_PT033634130 = {'d', 'kg'}; label.tW_PT033634130 = {'Time since start', 'Wet weight'}; comment.tW_PT033634130 = 'Data from GreenBeef trial 1'; title.tW_PT033634130 = 'Wet weight growth curve, individual PT033634130'; bibkey.tW_PT033634130 = 'GreenBeefTrial1';
init.tW_PT033634130 = 453; units.init.tW_PT033634130 = 'kg'; label.init.tW_PT033634130 = 'Initial weight'; 


data.tW_PT624139868 = [0 464; 14 470; 21 480; 35 508; 50 542; 63 558; 83 582];
units.tW_PT624139868 = {'d', 'kg'}; label.tW_PT624139868 = {'Time since start', 'Wet weight'}; comment.tW_PT624139868 = 'Data from GreenBeef trial 1'; title.tW_PT624139868 = 'Wet weight growth curve, individual PT624139868'; bibkey.tW_PT624139868 = 'GreenBeefTrial1';
init.tW_PT624139868 = 464; units.init.tW_PT624139868 = 'kg'; label.init.tW_PT624139868 = 'Initial weight'; 




% entity data types
metaData.entity_data_types = {'DMD', 'tW'}; 


% Cell array of entity_ids
data.entity_list = 10; units.entity_list = '-'; label.entity_list = 'Tier structure variable'; 
tiers.entity_list = {'male'}; units.tiers.entity_list = '-'; label.tiers.entity_list = 'List of entities'; 
metaData.entity_list = tiers.entity_list; 


% Struct with form tier_entities.(tier_name) = list_of_entities_of_tier
data.tier_entities = 10; units.tier_entities = '-'; label.tier_entities = 'Tier structure variable'; 
tiers.tier_entities = struct('breed', {{'male'}}, 'diet', {{'CTRL', 'TMR'}}, 'individual', {{'PT533358890', 'PT933602927', 'PT333842562', 'PT233843883', 'PT524401180', 'PT333653651', 'PT833653644', 'PT933843912', 'PT524956505', 'PT924401183', 'PT933843894', 'PT724523831', 'PT833653649', 'PT224401177', 'PT533987885', 'PT424401157', 'PT433843806', 'PT533843896', 'PT033634130', 'PT624139868'}}); units.tiers.tier_entities = '-'; label.tiers.tier_entities = 'List of entity ids for each tier'; 


% Struct with form groups_of_entity.(entity_id) = list_of_groups_ids_entity_belongs_to
data.groups_of_entity = 10; units.groups_of_entity = '-'; label.groups_of_entity = 'Tier structure variable'; 
tiers.groups_of_entity = struct('CTRL', {{}}, 'TMR', {{}}, 'PT533358890', {{'Pen_5'}}, 'PT933602927', {{'Pen_4'}}, 'PT333842562', {{'Pen_3'}}, 'PT233843883', {{'Pen_5'}}, 'PT524401180', {{'Pen_3'}}, 'PT333653651', {{'Pen_5'}}, 'PT833653644', {{'Pen_2'}}, 'PT933843912', {{'Pen_2'}}, 'PT524956505', {{'Pen_4'}}, 'PT924401183', {{'Pen_4'}}, 'PT933843894', {{'Pen_3'}}, 'PT724523831', {{'Pen_5'}}, 'PT833653649', {{'Pen_3'}}, 'PT224401177', {{'Pen_4'}}, 'PT533987885', {{'Pen_3'}}, 'PT424401157', {{'Pen_2'}}, 'PT433843806', {{'Pen_2'}}, 'PT533843896', {{'Pen_4'}}, 'PT033634130', {{'Pen_5'}}, 'PT624139868', {{'Pen_2'}}); units.tiers.groups_of_entity = '-'; label.tiers.groups_of_entity = 'Groups each entity belongs to'; 

    
% Tier subtree
% Lists entities that are below entity_id for each tier below
% Struct with form tier_subtree.(entity_id).(tier_name) = list_of_entities_below
data.tier_subtree = 10; units.tier_subtree = '-'; label.tier_subtree = 'Tier structure variable'; 
tiers.tier_subtree = struct('male', struct('diet', {{'CTRL', 'TMR'}}, 'individual', {{'PT533358890', 'PT933602927', 'PT333842562', 'PT233843883', 'PT524401180', 'PT333653651', 'PT833653644', 'PT933843912', 'PT524956505', 'PT924401183', 'PT933843894', 'PT724523831', 'PT833653649', 'PT224401177', 'PT533987885', 'PT424401157', 'PT433843806', 'PT533843896', 'PT033634130', 'PT624139868'}})); units.tiers.tier_subtree = '-'; label.tiers.tier_subtree = 'Tier subtree'; 


%% Tier parameters
% Cell array with tier parameters
data.tier_pars = 10; units.tier_pars = '-'; label.tier_pars = 'Tier structure variable'; comment.tier_pars = 'Tier parameters'; 
tiers.tier_pars = {'p_Am', 'kap_X', 'kap_P', 'p_M', 'v', 'kap', 'E_G', 'E_Hb', 'E_Hx', 'E_Hp', 'h_a', 't_0', 'del_M', 'p_Am_f', 'E_Hp_f'}; units.tiers.tier_pars = '-'; label.tiers.tier_pars = 'Tier parameters'; 
metaData.tier_pars = tiers.tier_pars; 


% Initial values for each tier parameter and entity
% Struct with form tier_par_init_values.(par).(entity_id) = value;
metaData.tier_par_init_values = struct('p_Am', struct('male', 5000), 'kap_X', struct('male', 0.2), 'kap_P', struct('male', 0.1), 'p_M', struct('male', 80), 'v', struct('male', 0.05), 'kap', struct('male', 0.97), 'E_G', struct('male', 7800), 'E_Hb', struct('male', 2000000.0), 'E_Hx', struct('male', 20000000.0), 'E_Hp', struct('male', 60000000.0), 'h_a', struct('male', 5e-10), 't_0', struct('male', 80), 'del_M', struct('male', 0.15), 'p_Am_f', struct('male', 4500), 'E_Hp_f', struct('male', 60000000.0)); 


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

