import pandas as pd
import os
import os.path
import re
import numpy as np

import rpy2
import rpy2.robjects as robjects
from rpy2.robjects.packages import importr

#utils = importr('utils')

#utils.install_packages('neonUtilities', repos='https://cran.rstudio.com/')
neonUtilities = importr('neonUtilities')

# -----------------------------------------------------------------------------------------------#


def def_format_sdg(data_dir = os.getcwd() + '/NEON_dissolved-gases-surfacewater.zip'):

    ##### Default values ####
    volH2O = 40 #mL
    volGas = 20 #mL

    #Check if the data is loaded already using loadByProduct
    if 'externalLabData' and 'fieldDataProc' and 'fieldSuperParent' not in locals() or globals():
        print("data is not loaded")  # testing code

        # If data is not loaded, stack field and external lab data
        if os.path.isdir(re.sub("\\.zip", "", data_dir)):
            neonUtilities.stackByTable(dpID="DP1.20097.001", filepath=data_dir)

        externalLabData = pd.read_csv(re.sub("\\.zip", "", data_dir) + "/stackedFiles" + "/sdg_externalLabData.csv")
        fieldDataProc = pd.read_csv(re.sub("\\.zip", "", data_dir) + "/stackedFiles" + "/sdg_fieldDataProc.csv")
        fieldSuperParent = pd.read_csv(re.sub("\\.zip", "", data_dir) + "/stackedFiles" + "/sdg_fieldSuperParent.csv")


    print("Data is loaded") #testing code
    #Flag and set default field values

    if fieldDataProc['waterVolumeSyringe'].isna() is True:
        fieldDataProc['volH2OSource'] = 1
    else:
        fieldDataProc['volH2OSource'] = 0

    if fieldDataProc['gasVolumeSyringe'].isna() is True:
        fieldDataProc['volGasSource'] = 1
    else:
        fieldDataProc['volGasSource'] = 0

    if fieldDataProc['waterVolumeSyringe'].isna() is True:
        fieldDataProc['waterVolumeSyringe'] = volH2O

    if fieldDataProc['gasVolumeSyringe'].isna() is True:
        fieldDataProc['gasVolumeSyringe'] = volGas

    outputDFNames = [
        'waterSampleID',
        'referenceAirSampleID',
        'equilibratedAirSampleID',
        'collectDate',
        'processedDate',
        'stationID',
        'barometricPressure',
        'headspaceTemp',
        'waterTemp',
        'concentrationCO2Air',
        'concentrationCO2Gas',
        'concentrationCH4Air',
        'concentrationCH4Gas',
        'concentrationN2OAir',
        'concentrationN2OGas',
        'waterVolume',
        'gasVolume',
        #'CO2BelowDetection',
        #'CH4BelowDetection',
        #'N2OBelowDetection',
        'volH2OSource',
        'volGasSource'
    ]

    # Assign the number of rows and columns to the new DataFrame, outputDF
    # The number of rows = # of rows there is in fieldDataProc['waterSampleID'] & the number of columns = # of items in the list, outputDFNames
    outputDF = pd.DataFrame(index=np.arange(len(fieldDataProc['waterSampleID'])), columns=np.arange(len(outputDFNames)))
    # Assigns the items inside outputDFNames to the columns in the outputDF DataFrame
    outputDF.columns = outputDFNames

    # Populate the output file with field data
    for k in range(len(outputDF.columns)):
    #for ind, row in fieldDataProc.iterrows():
        if outputDF.columns[k] in fieldDataProc.columns:
            print("Found: " + outputDF.columns[k])

            outputDF.iloc[:,k] = fieldDataProc.loc[:,fieldDataProc.columns == outputDF.columns[k]]

    outputDF['headspaceTemp'] = fieldDataProc['storageWaterTemp']
    outputDF['barometricPressure'] = fieldDataProc['ptBarometricPressure']
    outputDF['waterVolume'] = fieldDataProc['waterVolumeSyringe']
    outputDF['gasVolume'] = fieldDataProc['gasVolumeSyringe']
    outputDF['stationID'] = fieldDataProc['namedLocation']

    #outputDF = np.array(outputDF)
    #externalLabData = np.array(outputDF)

    #Populate the output file with external lab data
    for l in range(len(outputDF['waterSampleID'])):
        try:
            outputDF.loc[outputDF.index[[l]], 'concentrationCO2Air'] = externalLabData.loc[externalLabData.loc[:, 'sampleID'] == outputDF.loc[outputDF.index[[l]], 'referenceAirSampleID'].item(), 'concentrationCO2'].item()
            outputDF.loc[outputDF.index[[l]], 'concentrationCO2Gas'] = externalLabData.loc[externalLabData.loc[:, 'sampleID'] == outputDF.loc[outputDF.index[[l]], 'equilibratedAirSampleID'].item(), 'concentrationCO2'].item()

        except Exception:
            pass
        try:
            outputDF.loc[outputDF.index[[l]], 'concentrationCH4Air'] = externalLabData.loc[externalLabData.loc[:, 'sampleID'] == outputDF.loc[outputDF.index[[l]], 'referenceAirSampleID'].item(), 'concentrationCH4'].item()
            outputDF.loc[outputDF.index[[x]], 'concentrationCH4Gas'] = externalLabData.loc[ externalLabData.loc[:, 'sampleID'] == outputDF.loc[outputDF.index[[l]], 'equilibratedAirSampleID'].item(), 'concentrationCH4'].item()

        except Exception:
            pass

        try:
            outputDF.loc[outputDF.index[[l]], 'concentrationN2OAir'] = externalLabData.loc[externalLabData.loc[:, 'sampleID'] == outputDF.loc[outputDF.index[[l]], 'referenceAirSampleID'].item(), 'concentrationN2O'].item()
            outputDF.loc[outputDF.index[[l]], 'concentrationN2OGas'] = externalLabData.loc[externalLabData.loc[:, 'sampleID'] == outputDF.loc[outputDF.index[[l]], 'equilibratedAirSampleID'].item(), 'concentrationN2O'].item()
        except Exception:
            pass

    #Populate the output file with water temperature data for streams
    for m in range(len(outputDF['waterSampleID'])):
        try:
            outputDF.loc[outputDF.index[[m]], 'waterTemp'] = fieldSuperParent.loc[fieldSuperParent.loc[:, 'parentSampleID'] == outputDF.loc[outputDF.index[[m]], 'waterSampleID'].item(), 'waterTemp'].item()
        except Exception:
            pass
        if pd.isna(outputDF['headspaceTemp'][m]) is True:
            try:
                outputDF.loc[outputDF.index[[m]], 'headspaceTemp'] = fieldSuperParent.loc[fieldSuperParent.loc[:, 'parentSampleID'] == outputDF.loc[outputDF.index[[m]], 'waterSampleID'].item(), 'waterTemp'].item()
            except Exception:
                pass
    
    #Flag values below detection (TBD)
    print("**********************************************************************")
    print("EXTERNAL LAB DATA")
    print(externalLabData)
    print("**********************************************************************")
    print("FIELD DATA PROC")
    print(fieldDataProc)
    print("**********************************************************************")
    print("FIELD SUPER PARENT")
    print(fieldSuperParent)

    return externalLabData, fieldDataProc, fieldSuperParent, outputDF


external_Lab_Data, field_Data_Proc, field_Super_Parent, output_DF = def_format_sdg()
