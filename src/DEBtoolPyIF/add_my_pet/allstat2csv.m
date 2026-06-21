function allstat2csv(allStatPath, saveFilePath)
    load(allStatPath, "allStat");

    %% Create table
    speciesList = fieldnames(allStat);
    numSpecies = length(speciesList);

    % We do not know all columns beforehand, so preallocate just a few
    taxonomyCols = {'species_en', 'family', 'order', 'class', 'phylum', 'id_CoL'};
    columnNames = {
        taxonomyCols{:}, ...
        'model', 'MRE', 'SMSE', 'completeness', 'date',
    };
    numCols = length(columnNames);
    varTypes = {
        'string', 'string', 'string', 'string', 'string', 'string', ...
         'string', 'double', 'double', 'double', 'string',
    };

    allStatTable = table( ...
        'Size', [numSpecies, numCols], ...
        'VariableTypes', varTypes, ...
        'VariableNames', columnNames, ...
        'RowNames', speciesList ...
    );

    for i=1:numSpecies
        % Copy sepcies struct
        species = speciesList{i};
        stat = allStat.(species);
        speciesStats = fieldnames(stat);

        % Save species taxonomy
        for t=1:length(taxonomyCols)
            taxon = taxonomyCols{t};
            allStatTable{species, taxon} = string(stat.(taxon));
        end
        % Save estimation info
        allStatTable{species, 'model'} = string(stat.model);
        allStatTable{species, 'MRE'} = stat.MRE;
        allStatTable{species, 'SMSE'} = stat.SMSE;
        allStatTable{species, 'completeness'} = stat.COMPLETE;
        allStatTable{species, 'date'} = sprintf("%d-%d-%d", stat.date_acc(:));

        % Save parameters
        for p=1:length(speciesStats)
            par = speciesStats{p};
            value = stat.(par);
            if isnumeric(value) && isscalar(value)
                allStatTable{species, par} = value;
            end
        end

        % Save table every 1000
        if mod(i, 1000) == 0
            writetable(allStatTable, saveFilePath,'WriteRowNames',true);
            fprintf('[%5d | %5d] Table saved in %s\n', i, numSpecies, saveFilePath);
        end
    end

    %% Save table
    writetable(allStatTable, saveFilePath,'WriteRowNames',true);
    fprintf('[%5d | %5d] Table saved in %s\n', i, numSpecies, saveFilePath);




