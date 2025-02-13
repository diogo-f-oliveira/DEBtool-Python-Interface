%% deb_lossfun
% gets value of loss function

%%
function lf_val = deb_lossfun(data, prdData, weights, par, includePseudoData)

%% Syntax
%% Description
% Gets value of loss function
%
% Input:
%
% * data: structure as specified by mydata-files
% * prdData: structure as specified by predict-files
% * weights: structure as specified by mydata-files
%
% Output:
%
% * lf_val: value of loss function

%% Remarks
% the output can include contributions from pseudo-data.

% Remove pseudo data from data struct if not wanted
if ~includePseudoData
    if isfield(data,'psd')
        data = rmfield(data,'psd');
    end
% Else, predict pseudo_data from par
else
    prdData = predict_pseudodata(par, data, prdData);
end

% prepare variable
%   st: structure with dependent data values only
st = data;
[nm, nst] = fieldnmnst_st(st); % nst: number of data sets

for i = 1:nst   % makes st only with dependent variables
    fieldsInCells = textscan(nm{i},'%s','Delimiter','.');
    auxVar = getfield(st, fieldsInCells{1}{:});   % data in field nm{i}
    [~, k, npage] = size(auxVar);
    if k>=2 && npage==1% columns 2,3,.. are treated as data to be predicted if npage==1
        st = setfield(st, fieldsInCells{1}{:}, auxVar(:,2:end));
    end
end

% Y: vector with all dependent data, NaN's omitted
% W: vector with all weights, but those that correspond NaN's in data omitted
[Y, meanY] = struct2vector(st, nm, st);
W = struct2vector(weights, nm, st);
[P, meanP] = struct2vector(prdData, nm, st);
lf_val = lossfunction_sb(Y, meanY, P, meanP, W);
    
end

function [vec, meanVec] = struct2vector(struct, fieldNames, structRef)
% structRef has the same structure as struct, but some values can be NaN's; the values themselves are not used
% struct2vector is called for data (which might have NaN's), but also for predictions, which do not have NaN's
vec = []; meanVec = [];
for i = 1:size(fieldNames, 1)
    fieldsInCells = textscan(fieldNames{i},'%s','Delimiter','.');
    aux = getfield(struct, fieldsInCells{1}{:}); aux = aux(:);
    auxRef = getfield(structRef, fieldsInCells{1}{:}); auxRef = auxRef(:);
    aux = aux(~isnan(auxRef)); % remove values that have NaN's in structRef
    vec = [vec; aux];
    meanVec = [meanVec; ones(length(aux), 1) * mean(aux)];
end
end
