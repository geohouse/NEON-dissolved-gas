from def_format_sdg import outputDF, externalLabData

for x in range(len(outputDF['waterSampleID'])):
    # print(x)
    # FOR DEMO
    holder = outputDF.loc[outputDF.index[[x]], 'referenceAirSampleID']
    # FOR DEMO
    holder2 = externalLabData.loc[:, 'sampleID']
    # Need to actually access the single cell value (string) in holder using .item()
    # FOR DEMO
    booleanHolder = holder2 == holder.item()
    # FOR DEMO
    holder3 = externalLabData.loc[booleanHolder, 'concentrationCO2']

    # This is all of the above intermediate variables put together into one line, and is the right hand side of the
    # assignment into the 'concentrationCO2Air' column of the outputDF data frame (at row 'x')
    # FOR DEMO
    rhsOfAssignment = externalLabData.loc[externalLabData.loc[:, 'sampleID'] == outputDF.loc[
        outputDF.index[[x]], 'referenceAirSampleID'].item(), 'concentrationCO2']

    # This needs to be in a try block because the outputDF has sampleIDs that are populated from the field samples,
    # and this is looping through those sampleIDs to look for matches with the lab data, but for recently
    # collected samples, there won't be lab data for them (but will obviously still be field samples) so this
    # look-up will fail. Put it in a try block with nothing in the except block to imitate the silent try
    # that this code has in R
    try:
        outputDF.loc[outputDF.index[[x]], 'concentrationCO2Air'] = externalLabData.loc[
            externalLabData.loc[:, 'sampleID'] == outputDF.loc[
                outputDF.index[[x]], 'referenceAirSampleID'].item(), 'concentrationCO2'].item()
        # NEEDS THE OTHER ASSIGNMENT LINE HERE (THERE ARE 2 ASSIGNMENT LINES WITHIN EACH TRY BLOCK IN THE R CODE)

    except Exception:
        pass

