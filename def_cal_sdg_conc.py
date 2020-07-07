import pandas as pd
import math
#import format_sdg
from numpy.ma import exp
from rpy2.rinterface import NA

#from def_format_sdg import def_format_sdg


def sign_if(x, digits = 3):
    if x == 0 or not math.isfinite(x):
        return x
    digits -= math.ceil(math.log10(abs(x)))
    return round(x, digits)

def def_calc_sdg_concentration(
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
    cdHdTCH4 = 1900  # K, range: 1400-2400
    cdHdTN2O = 2700  # K, range: 2600 - 3600

    ##### Populate mean global values for reference air where it isn't reported #####
    if inputFile.iloc[:, sourceCO2].isna() is True:
        inputFile.iloc[:, sourceCO2] = 405  # use global mean https://www.esrl.noaa.gov/gmd/ccgg/trends/global.html

    if inputFile.iloc[:, sourceCH4].isna() is True:
        inputFile.iloc[:, sourceCH4] = 1.85  # https://www.esrl.noaa.gov/gmd/ccgg/trends_ch4/

    if inputFile.iloc[:, sourceN2O].isna() is True:
        inputFile.iloc[:, sourceN2O] = 0.330  # https://www.esrl.noaa.gov/gmd/hats/combined/N2O.html

    ##### Calculate dissolved gas concentration in original water sample #####
    inputFile['dissolvedCO2'] = NA
    inputFile['dissolvedCO2'] = inputFile.iloc[:, baro] * cPresConv * (inputFile.iloc[:, volGas] * (inputFile.iloc[:, eqCO2] - inputFile.iloc[:, sourceCO2]) / (
                                                cGas * (inputFile.iloc[:, headspaceTemp] + cKelvin)* inputFile.iloc[:, volH2O]) + ckHCO2 * exp(cdHdTCO2 *
                                                (1 / (inputFile.iloc[:, headspaceTemp] + cKelvin) - 1 / cT0)) * inputFile.iloc[:, eqCO2])

    inputFile['dissolvedCH4'] = NA
    inputFile['dissolvedCH4'] = inputFile.iloc[:, baro] * cPresConv *(inputFile.iloc[:, volGas] * (inputFile.iloc[:, eqCH4] - inputFile.iloc[:, sourceCH4]) / (
                                                  cGas * (inputFile.iloc[:, headspaceTemp] + cKelvin) * inputFile.iloc[:, volH2O]) +
                                                  ckHCH4 * exp(cdHdTCH4 * (1 / (inputFile.iloc[:, headspaceTemp] + cKelvin) - 1 / cT0)) * inputFile.iloc[:, eqCH4])

    inputFile['dissolvedN2O'] = NA
    inputFile['dissolvedN2O'] = inputFile.iloc[:, baro] * cPresConv * (inputFile.iloc[:, volGas] * (inputFile.iloc[:, eqN2O] - inputFile.iloc[:, sourceN2O]) / (
                                                  cGas * (inputFile.iloc[:, headspaceTemp] + cKelvin) * inputFile.iloc[:, volH2O]) +
                                                  ckHN2O * exp(cdHdTN2O * (1 / (inputFile.iloc[:, headspaceTemp] + cKelvin) - 1 / cT0)) * inputFile.iloc[:, eqN2O])

    ##### Step-by-step Calculation of dissolved gas concentrations for testing #####

    # Dissolved gas concentration in the original water samples (dissolvedGas) is
    # calculated from a mass balance of the measured headspace concentration (eqGas), the
    # calculated concentration in the equilibrated headspace water (eqHeadspaceWaterCO2),
    # and the volumes of the headspace water and headspace gas, following:

    #dissolvedGas = ((eqGas * volGas) + (eqHeadspaceWaterGas * volH2O) - (sourceGas * volGas)) / volH2O

    # Measured headspace concentration should be expressed as mol L- for the mass
    # balance calculation and as partial pressure for the equilibrium calculation.

    # #Temperature corrected Henry's Law Constant
    # HCO2 <- ckHCO2 * exp(cdHdTCO2 * ((1/(headspaceTemp+cKelvin)) - (1/cT0)))
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
    inputFile['dissolvedCO2'] = sign_if(inputFile['dissolvedCO2'], 3)
    inputFile['dissolvedCH4'] = sign_if(inputFile['dissolvedCH4'], 3)
    inputFile['dissolvedN2O'] = sign_if(inputFile['dissolvedN2O'], 3)

    return inputFile


#sdgFormatted = def_format_sdg(data_dir= data_dir)
#sdgDataPlusConc = def_calc_sdg_conc(inputFile=sdgFormatted)


