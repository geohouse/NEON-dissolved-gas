from math import exp
import os

import mpmath as mpmath
import pandas as pd
from numpy import character, nan, math
import numpy as np
import def_format_sdg as deffg
import def_cal_sdg_conc as defcsc
from decimal import Decimal

def def_calc_sdg_sat(
    inputFile,
    baro="barometricPressure",
    waterTemp="waterTemp",
    headspaceTemp="headspaceTemp",
    concCO2="dissolvedCO2",
    sourceCO2="concentrationCO2Air",
    concCH4="dissolvedCH4",
    sourceCH4="concentrationCH4Air",
    concN2O="dissolvedN2O",
    sourceN2O="concentrationN2OAir"
):

    if type(inputFile) is str:

        inputFile = pd.read_csv(inputFile)


    ##### Constants #####
    cGas =8.3144598  # universal gas constant (J K-1 mol-1)
    cKelvin = 273.15  # Conversion factor from Kelvin to Celsius
    cPresConv = 0.000001  # Constant to convert mixing ratio from umol/mol (ppmv) to mol/mol. Unit conversions from kPa to Pa, m^3 to L, cancel out.
    cT0 = 298.15
    # Henry's law constant T0
    cConcPerc = 100  # Convert to percent
    # Henry's law constants and temperature dependence from Sander (2015) DOI: 10.5194/acp-15-4399-2015
    ckHCO2 = 0.00033  # mol m-3 Pa, range: 0.00031 - 0.00045
    ckHCH4 = 0.000014  # mol m-3 Pa, range: 0.0000096 - 0.000092
    ckHN2O = 0.00024  # mol m-3 Pa, range: 0.00018 - 0.00025
    cdHdTCO2 = 2400  # K, range: 2300 - 2600
    cdHdTCH4 = 1900  # K, range: 1400-2400
    cdHdTN2O = 2700  # K, range: 2600 - 3600


    ##### Populate mean global values for reference air where it isn't reported #####
    inputFile.loc[:, sourceCO2] = inputFile.loc[:, sourceCO2].replace(nan, 405)  # use global mean https://www.esrl.noaa.gov/gmd/ccgg/trends/global.html

    inputFile.loc[:, sourceCH4] = inputFile.loc[:, sourceCH4].replace(nan, 1.85)  #https://www.esrl.noaa.gov/gmd/ccgg/trends_ch4/

    inputFile.loc[:, sourceN2O] = inputFile.loc[:, sourceN2O].replace(nan, 0.330)  #https://www.esrl.noaa.gov/gmd/hats/combined/N2O.html

    ##### Calculate dissolved gas concentration at 100% saturation #####

    # 100% saturation occurs when the dissolved gas concentration is in equilibrium
    # with the atmosphere.
    inputFile['satConcCO2'] = np.nan
    test = inputFile.loc[:, waterTemp]
  #  inputFile['satConcCO2'] = (ckHCO2 * np.exp(cdHdTCO2 * (1 / ((test.astype(np.float64)) + cKelvin) - 1 / cT0))) * inputFile.loc[:, sourceCO2] * inputFile.loc[:, baro] * cPresConv
    #for i in inputFile['satConcCO2']:
    inputFile['satConcCO2'] = (ckHCO2 * np.exp(cdHdTCO2 * (1 / ((test.astype(np.float)) + cKelvin) - 1 / cT0))) * inputFile.loc[:,sourceCO2] * inputFile.loc[:, baro] * cPresConv
       # "{:.2E}".format(Decimal(i))
 #   inputFile['satConcCO2'] = (ckHCO2 * np.exp(cdHdTCO2 * (1 / ((test.astype(np.float64)) + cKelvin) - 1 / cT0))) * inputFile.loc[:, sourceCO2] * inputFile.loc[:, baro] * cPresConv
    inputFile['satConcCH4'] = np.nan
  #  inputFile['satConcCH4'] = (ckHCH4 * np.exp(cdHdTCH4 * (1 / ((test.astype(np.float64)) + cKelvin) - 1 / cT0))) * inputFile.loc[:, sourceCH4] * inputFile.loc[:, baro] * cPresConv
    inputFile['satConcN2O'] = np.nan
 #   inputFile['satConcN2O'] = (ckHN2O * np.exp(cdHdTN2O * (1 / ((test.astype(np.float64)) + cKelvin) - 1 / cT0))) * inputFile.loc[:, sourceN2O] * inputFile.loc[:, baro] * cPresConv

    ##### Calculate dissolved gas concentration as % saturation #####                                ['satConcCO2']
    inputFile['CO2PercSat'] = inputFile.loc[:, concCO2] / inputFile['satConcCO2'] * cConcPerc
    inputFile['CH4PercSat'] = inputFile.loc[:, concCH4] / inputFile['satConcCH4'] * cConcPerc
    inputFile['N2OPercSat'] = inputFile.loc[:, concN2O] / inputFile['satConcN2O'] * cConcPerc

    return inputFile


sdgFormatted = deffg.def_format_sdg(data_dir=os.getcwd() + '/NEON_dissolved-gases-surfacewater.zip')
sdgDataPlusConc = defcsc.def_cal_sdg_conc(inputFile=sdgFormatted)
inputFile = def_calc_sdg_sat(inputFile=sdgDataPlusConc)