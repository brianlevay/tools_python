# Contrast Enhancement

import numpy as np
import primary_calcs as primary


#####################################################################################################
## SUPPORT FUNCTIONS ##
#####################################################################################################


def stretch(murhot0, cfg):
    I_16b_bounds = (0.0, 65535.0)
    
    O_min = primary.calculate_murhot(np.array([cfg['I_high']]))[0]
    O_peak = primary.calculate_murhot(np.array([cfg['I_peak']]))[0]
    O_max = primary.calculate_murhot(np.array([cfg['I_low']]))[0]
    
    N_min = I_16b_bounds[0]
    N_max = I_16b_bounds[1]
    
    X = ((murhot0 - O_min)/(O_max - O_min))
    X[X < 0.0] = 0.0
    X[X > 1.0] = 1.0
    
    X_peak = ((O_peak - O_min)/(O_max - O_min))
    n = np.log(0.5)/np.log(X_peak)
    P = X**n
    
    S_X = 0.5*np.sin((X - 0.5)*(np.pi)) + 0.5
    S_P = 0.5*np.sin((P - 0.5)*(np.pi)) + 0.5
    
    wt = 1.0 - (2.0 * abs(X_peak - 0.5))**2
    Y = wt*S_P + (1-wt)*S_X
    N = ((N_max - N_min)/1.0) * (Y) + N_min
    
    I_proc = -1*N + N_max
    return I_proc

