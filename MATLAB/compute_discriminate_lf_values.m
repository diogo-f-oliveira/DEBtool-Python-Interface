function lf_values = compute_discriminate_lf_values(data, prdData, weights, metaData)

global lossfunction

lossfunctions = {'sb'};

% create a copy of weights will all weights set to 0
nm = fieldnames(data);
for i = 1:numel(nm)
    field = nm{i};
    empty_weights.(field) = zeros(size(weights.(field)));
end
all_sum = sum_weights(weights);

% creates a weight struct with original weights for zero-variate data and 0
% otherwise
zerovar_weights = empty_weights;
for i=1:length(metaData.data_0)
    zerovar_weights.(metaData.data_0{i}) = weights.(metaData.data_0{i});
end
zerovar_sum = sum_weights(zerovar_weights);
% creates a weight struct with original weights for uni-variate data and 0
% otherwise
univar_weights = empty_weights;
for i=1:length(metaData.data_1)
    univar_weights.(metaData.data_1{i}) = weights.(metaData.data_1{i});
end
univar_sum = sum_weights(univar_weights);

% compute loss function
for lf=1:length(lossfunctions)
    lossfunction = lossfunctions{lf};
    all_lf = lossfun(data, prdData, weights);
    zero_lf = lossfun(data, prdData, zerovar_weights);
    uni_lf = lossfun(data, prdData, univar_weights);
    
    lf_values.(lossfunctions{lf})            = all_lf;
    lf_values.([lossfunctions{lf} '_avg'])   = all_lf / all_sum;
    lf_values.([lossfunctions{lf} '_0'])     = zero_lf;
    lf_values.([lossfunctions{lf} '_0_avg']) = zero_lf / zerovar_sum;  
    lf_values.([lossfunctions{lf} '_1'])     = uni_lf;
    lf_values.([lossfunctions{lf} '_1_avg']) = uni_lf / univar_sum;
end
end

function weight_sum = sum_weights(weight_struct)
wnm = fieldnames(weight_struct);
weight_sum = 0;
for k=1:numel(wnm)
    % Ignore psd struct
    if strcmp(wnm{k},'psd')
        continue
    elseif isstruct(weight_struct.(wnm{k}))
        weight_sum = weight_sum + sum_weights(weight_struct.(wnm{k}));
    else
        weight_sum = weight_sum + sum(weight_struct.(wnm{k}));
    end
end
end