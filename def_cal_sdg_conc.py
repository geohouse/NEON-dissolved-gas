import os

import pandas as pd
#from def_format_sdg import def_format_sdg
from numpy import nan

import def_format_sdg as deffg
import math
import numpy as np


#sdgFormatted = deffg.def_format_sdg(data_dir=os.getcwd() + '/NEON_dissolved-gases-surfacewater.zip')
#inputFile = sdgFormatted


def def_cal_sdg_conc(
    inputFile,
    volGas="gasVolume",
    volH2O="waterVolume",
    baro="barometricPressure",
    waterTemp="waterTemp",
    headspaceTemp="headspaceTemp",
    eqCO2="concentrationCO2Gas",
    sourceCO2="concentrationCO2Air",
    eqCH4="concentrationCH4Gas",
    sourceCH4="concentrationCH4Air",
    eqN2O="concentrationN2OGas",
    sourceN2O="concentrationN2OAir"
):

    if type(inputFile) is str:
        inputFile = pd.read_csv(inputFile)

    ##### Constants #####
    cGas = 8.3144598  # universal gas constant (J K-1 mol-1)
    cKelvin = 273.15  # Conversion factor from Kelvin to Celsius
    cPresConv = 0.000001  # Constant to convert mixing ratio from umol/mol (ppmv) to mol/mol. Unit conversions from kPa to Pa, m^3 to L, cancel out.
    cT0 = 298.15
    # Henry's law constant T0
    # Henry's law constants and temperature dependence from Sander (2015) DOI: 10.5194/acp-15-4399-2015
    ckHCO2 = 0.00033  # mol m-3 Pa, range: 0.00031 - 0.00045
    ckHCH4 = 0.000014  # mol m-3 Pa, range: 0.0000096 - 0.000092
    ckHN2O = 0.00024  # mol m-3 Pa, range: 0.00018 - 0.00025
    cdHdTCO2 = 2400  # K, range: 2300 - 2600
    cdHdTCH4 = 1900  # K, range: 1400-24
    cdHdTN2O = 2700  # K, range: 2600 - 3600

    ##### Populate mean global values for reference air where it isn't reported #####

    inputFile.loc[:, sourceCO2] = inputFile.loc[:, sourceCO2].replace(nan, 405)  # use global mean https://www.esrl.noaa.gov/gmd/ccgg/trends/global.html

    inputFile.loc[:, sourceCH4] = inputFile.loc[:, sourceCH4].replace(nan, 1.85)  #https://www.esrl.noaa.gov/gmd/ccgg/trends_ch4/

    inputFile.loc[:, sourceN2O] = inputFile.loc[:, sourceN2O].replace(nan, 0.330)  #https://www.esrl.noaa.gov/gmd/hats/combined/N2O.html

    ##### Calculate dissolved gas concentration in original water sample #####
    inputFile['dissolvedCO2'] = np.nan
    inputFile['dissolvedCO2'] = inputFile.loc[:, baro] * cPresConv * (inputFile.loc[:, volGas] * (inputFile.loc[:, eqCO2] - inputFile.loc[:, sourceCO2]) / (
                                                    cGas * (inputFile.loc[:, headspaceTemp] + cKelvin) * inputFile.loc[:, volH2O]) +
                                                    ckHCO2 * np.exp(cdHdTCO2 * (1 / (inputFile.loc[:, headspaceTemp] + cKelvin) - 1 / cT0)) * inputFile.loc[:, eqCO2])

    inputFile['dissolvedCH4'] = np.nan
    inputFile['dissolvedCH4'] = inputFile.loc[:, baro] * cPresConv * (inputFile.loc[:, volGas] * (inputFile.loc[:, eqCH4] - inputFile.loc[:, sourceCH4]) / (
                                                  cGas * (inputFile.loc[:, headspaceTemp] + cKelvin) * inputFile.loc[:, volH2O]) +
                                                  ckHCH4 * np.exp(cdHdTCH4 * (1 / (inputFile.loc[:, headspaceTemp] + cKelvin) - 1 / cT0)) * inputFile.loc[:, eqCH4])

    inputFile['dissolvedN2O'] = np.nan
    inputFile['dissolvedN2O'] = inputFile.loc[:, baro] * cPresConv * (inputFile.loc[:, volGas] * (inputFile.loc[:, eqN2O] - inputFile.loc[:, sourceN2O]) / (
                                                  cGas * (inputFile.loc[:, headspaceTemp] + cKelvin) * inputFile.loc[:, volH2O]) +
                                                  ckHN2O * np.exp(cdHdTN2O * (1 / (inputFile.loc[:, headspaceTemp] + cKelvin) - 1 / cT0)) * inputFile.loc[:, eqN2O])

    ##### Step-by-step Calculation of dissolved gas concentrations for testing #####

    # Dissolved gas concentration in the original water samples (dissolvedGas) is
    # calculated from a mass balance of the measured headspace concentration (eqGas), the
    # calculated concentration in the equilibrated headspace water (eqHeadspaceWaterCO2),
    # and the volumes of the headspace water and headspace gas, following:

    #dissolvedGas = ((eqGas * volGas) + (eqHeadspaceWaterGas * volH2O) - (sourceGas * volGas)) / volH2O

    # Measured headspace concentration should be expressed as mol L- for the mass
    # balance calculation and as partial pressure for the equilibrium calculation.

    # #Temperature corrected Henry's Law Constant
    #HCO2 = ckHCO2 * exp(cdHdTCO2 * ((1/(headspaceTemp+cKelvin)) - (1/cT0)))
    # HCH4 <- ckHCH4 * exp(cdHdTCH4 * ((1/(headspaceTemp+cKelvin)) - (1/cT0)))
    # HN2O <- ckHN2O * exp(cdHdTN2O * ((1/(headspaceTemp+cKelvin)) - (1/cT0)))
    #
    # #Mol of gas in equilibrated water (using Henry's law)
    # CO2eqWat <- HCO2 * eqCO2 * cPresConv * baro * (volH2O/1000)
    # CH4eqWat <- HCH4 * eqCH4 * cPresConv * baro * (volH2O/1000)
    # N2OeqWat <- HN2O * eqN2O * cPresConv * baro * (volH2O/1000)
    #
    # #Mol of gas in equilibrated air (using ideal gas law)
    # CO2eqAir <- (eqCO2 * cPresConv * baro * (volGas/1000))/(cGas * (headspaceTemp + cKelvin))
    # CH4eqAir <- (eqCH4 * cPresConv * baro * (volGas/1000))/(cGas * (headspaceTemp + cKelvin))
    # N2OeqAir <- (eqN2O * cPresConv * baro * (volGas/1000))/(cGas * (headspaceTemp + cKelvin))
    #
    # #Mol of gas in source gas (using ideal gas law)
    # CO2air <- (inputFile[,sourceCO2] * cPresConv * baro * (volGas/1000))/(cGas * (headspaceTemp + cKelvin))
    # CH4air <- (inputFile[,sourceCH4] * cPresConv * baro * (volGas/1000))/(cGas * (headspaceTemp + cKelvin))
    # N2Oair <- (inputFile[,sourceN2O] * cPresConv * baro * (volGas/1000))/(cGas * (headspaceTemp + cKelvin))
    #
    # #Total mol of gas is sum of equilibrated water and equilibrated air
    # CO2tot <- CO2eqWat + CO2eqAir
    # CH4tot <- CH4eqWat + CH4eqAir
    # N2Otot <- N2OeqWat + N2OeqAir
    #
    # #Total mol of gas minus reference air mol gas to get water mol gas before equilibration
    # CO2wat <- CO2tot - CO2air
    # CH4wat <- CH4tot - CH4air
    # N2Owat <- N2Otot - N2Oair
    #
    # #Concentration is mol of gas divided by volume of water
    # inputFile$dissolvedCO2 <- CO2wat/(volH2O/1000)
    # inputFile$dissolvedCH4 <- CH4wat/(volH2O/1000)
    # inputFile$dissolvedN2O <- N2Owat/(volH2O/1000)


    # Round to significant figures
   # inputFile['dissolvedCO2'] = round_sig(inputFile['dissolvedCO2'])
  #  inputFile['dissolvedCH4'] = round_sig(inputFile['dissolvedCH4'])

   # inputFile['dissolvedN2O'] = sign_if(inputFile['dissolvedN2O'])

    return inputFile
#'%s' % float('%.1g' % 0.12)

def sign_if(x, digits = 3):
    if x == 0 or not math.isfinite(x):
        return x
    digits -= math.ceil(math.log10(abs(x)))
    return round(x, digits)



def round_sig(x, sig=3):
    return round(x, sig - int(math.floor(math.log10(abs(x)))) - 1)

  #  return round(x, sig - int(math.floor(math.log10(abs(x)))) - 1)


sdgFormatted = deffg.def_format_sdg(data_dir=os.getcwd() + '/NEON_dissolved-gases-surfacewater.zip')
inputFile = def_cal_sdg_conc(inputFile=sdgFormatted)


#sdgFormatted = def_format_sdg(data_dir=os.getcwd() + '/NEON_dissolved-gases-surfacewater.zip')
#sdgDataPlusConce = def_calc_sdg_concentration(sdgFormatted)

#inputFile = sdgFormatted
#inputFile = def_calc_sdg_concentration(sdgDataPlusConc)


