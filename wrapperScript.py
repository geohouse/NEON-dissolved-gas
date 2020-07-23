#from def_format_sdg import def_format_sdg
#from def_cal_sdg_conc import def_cal_sdg_conc

import def_format_sdg as deffg
import def_calc_sdg_conc as defcsc

import os

sdgFormatted = deffg.def_format_sdg(data_dir=os.getcwd() + '/NEON_dissolved-gases-surfacewater.zip')
sdgDataPlusConc = defcsc(inputFile=sdgFormatted)

print(sdgFormatted)
print(sdgDataPlusConc)