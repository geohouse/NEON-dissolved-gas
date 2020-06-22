import pandas as pd
import os
import os.path
import re

import sklearn as sklearn
import pandas as pd
from sklearn import datasets

import rpy2
import rpy2.robjects as robjects
from rpy2.robjects.packages import importr

base = importr('base')
utils = importr('utils')
stats = importr('stats')


utils.install_packages('neonUtilities', repos='https://cran.rstudio.com/');
neonUtilities = importr('neonUtilities')

#Join data files: stackByTable()
#neonUtilities.stackByTable(filepath='~/Downloads/NEON_dissolved-gases-surfacewater.zip');
#Read downloaded and stacked files into Python
##os.listdir('Downloads/filesToStack10003/stackedFiles/')
# -----------------------------------------------------------------------------------------------#
# data_dir = '/NEON_dissolved-gases-surfacewater.zip' #default
def def_format_sdg(data_dir = os.getcwd() + '/NEON_dissolved-gases-surfacewater.zip'):

    ##### Default values #####
    volH2O = 40 #mL
    volGas = 20 #mL

    #Check if the data is loaded already using loadByProduct
    if 'externalLabData' and 'fieldDataProc' and 'fieldSuperParent' in locals() is False:
        print("data is not loaded")  # testing code

        # If data is not loaded, stack field and external lab data
        if os.path.isdir(re.sub("\\.zip", "", data_dir)) is False:
            neonUtilities.stackByTable(dpID="DP1.20097.001", filepath=data_dir)

        externalLabData = pd.read_csv(re.sub("\\.zip", "", data_dir) + "/stackedFiles" + "/sdg_externalLabData.csv")
        fieldDataProc = pd.read_csv(re.sub("\\.zip", "", data_dir) + "/stackedFiles" + "/sdg_fieldDataProc.csv")
        fieldSuperParent = pd.read_csv(re.sub("\\.zip", "", data_dir) + "/stackedFiles" + "/sdg_fieldSuperParent.csv")

        df_externalLabData = pd.DataFrame(externalLabData)
        df_fieldDataProc = pd.DataFrame(fieldDataProc)
        df_fieldSuperParent = pd.DataFrame(fieldSuperParent)

    print("Data is loaded") #testing code
    #Flag and set default field values

    if pd.isna(df_fieldDataProc['waterVolumeSyringe']):
        df_fieldDataProc['volH2OSource'] == 1
    else:
        df_fieldDataProc['volH2OSource'] == 0

    if pd.isna(df_fieldDataProc['gasVolumeSyringe']):
        df_fieldDataProc['volGasSource'] == 1
    else:
        df_fieldDataProc['volGasSource'] == 0

    df_fieldDataProc['waterVolumeSyringe'][pd.isna(fieldDataProc['waterVolumeSyringe'])] = volH2O
    df_fieldDataProc['gasVolumeSyringe'][pd.isna(fieldDataProc['gasVolumeSyringe'])] = volGas


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
    
    outputDF = robjects.r('matrix(data=np.nan, columns=length(outputDFNames), rows=length(fieldDataProc$waterSampleID)')
    outputDF.columns = outputDFNames
    
    
    #Populate the output file with field data

    for k in 1,len(outputDF.columns):
        if outputDF.columns[k] in fieldDataProc.columns:
          outputDF[k] = fieldDataProc[fieldDataProc.columns == outputDF.columns[k]]

        outputDF['headspaceTemp'] = fieldDataProc['storageWaterTemp']
        outputDF['barometricPressure'] = fieldDataProc['ptBarometricPressure']
        outputDF['waterVolume'] = fieldDataProc['waterVolumeSyringe']
        outputDF['gasVolume'] = fieldDataProc['gasVolumeSyringe']
        outputDF['stationID'] = fieldDataProc['namedLocation']


    #Populate the output file with external lab data
    for l in 1,len(outputDF['waterSampleID']):
        try:
          outputDF['concentrationCO2Air'][l] = externalLabData['concentrationCO2'][externalLabData['sampleID'] == outputDF['referenceAirSampleID'][l]]
          outputDF['concentrationCO2Gas'][l] = externalLabData['concentrationCO2'][externalLabData['sampleID'] == outputDF['equilibratedAirSampleID'][l]]

        try:
          outputDF['concentrationCH4Air'][l] = externalLabData['concentrationCH4'][externalLabData['sampleID'] == outputDF['referenceAirSampleID'][l]]
        except NameError:
          outputDF['concentrationCH4Gas'][l] = externalLabData['concentrationCH4'][externalLabData['sampleID'] == outputDF['equilibratedAirSampleID'][l]]

        try:
          outputDF['concentrationN2OAir'][l] <- externalLabData['concentrationN2O'][externalLabData['sampleID'] == outputDF['referenceAirSampleID'][l]]
        except NameError:
          outputDF['concentrationN2OGas'][l] <- externalLabData['concentrationN2O'][externalLabData['sampleID'] == outputDF['equilibratedAirSampleID'][l]]

    
    #Populate the output file with water temperature data for streams
    for m in 1,len(outputDF['waterSampleID']):
        try:
            outputDF['waterTemp'][m] = fieldSuperParent['waterTemp'][fieldSuperParent['parentSampleID'] == outputDF['waterSampleID'][m]]
        except NameError:
            if pd.isna(outputDF['headspaceTemp'][m]):
              try:
                outputDF['headspaceTemp'][m] = fieldSuperParent['waterTemp'][fieldSuperParent['parentSampleID'] == outputDF['waterSampleID'][m]]

    
    #Flag values below detection (TBD)
    
     # return(outputDF)