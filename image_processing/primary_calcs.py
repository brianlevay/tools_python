# Primary Calculations

import numpy as np
import core_axis as core
import thickness_model as thickness


#####################################################################################################
## MAIN FUNCTIONS ##
#####################################################################################################


def calculate_murhot(I_raw):
    I_14b_bounds = (0.0, 16383.0)
    I_max = I_14b_bounds[1]
    murhot = np.log(I_max) - np.log(I_raw + 1.0)
    murhot[murhot < 0.0] = 0.0
    return murhot


def calculate_murhot0(I_raw, geom, cfg):
    murhot = calculate_murhot(I_raw)
    xy_ax, theta = core.estimate_axis(I_raw, geom)
    tmodel = thickness.calc_t_model(xy_ax, theta, geom)
    tref = np.amax(tmodel)
    tcorr = np.divide(tref, tmodel, out=np.zeros_like(tmodel), where=tmodel!=0)
    tcorr_trim = np.where(tmodel >= cfg['t_min'], tcorr, 1.0)
    murhot0 = murhot * tcorr_trim
    ###################################################################
    edges = np.logical_and(tmodel > 0.0, tmodel < cfg['t_min'])
    murhot0 = np.where(edges, np.amax(murhot0), murhot0)
    return murhot0

    