
# coding: utf-8

# # X-Ray Source Simulation
# 
# Generates an x-ray source spectrum in units of counts / steradian based on the Ebel (1999) method. Uses xraylib_np for all x-ray and material values.

# ## Imports

# In[322]:

import numpy as np
import xraylib_np as xray
from numba import jit


# ## Equation Components

# In[323]:

## (1-exp(-tau*pz*angle_ratio))/(tau*pz*angle_ratio) in continuum and characteristic ##
@jit
def calc_absorption_factor(Z, kVp, theta_in, theta_out, keV_pz, keV_tau): ##
    Zarr = np.array([Z])
    U0 = kVp / keV_pz
    
    m = 0.1382 - (0.9211 / np.sqrt(Z))
    J = 0.0135*Z
    n = (kVp**m)*(0.1904 - 0.2236*np.log(Z) + 
                  0.1292*(np.log(Z)**2) - 0.0149*(np.log(Z)**3))
    Aarr = xray.AtomicWeight(Zarr)
    A = Aarr[0]
    pz_m = (A/Z)*((0.787*(10**-5))*np.sqrt(J)*(kVp**(3/2)) + (0.735*(10**-6))*(kVp**2))
    pz_num = 0.49269 - 1.0987*n + 0.78557*(n**2)
    pz_den = 0.70256 - 1.09865*n + 1.0046*(n**2)
    
    pz_bar = pz_m*(pz_num/(pz_den + np.log(U0)))*np.log(U0)
    tauE = xray.CS_Photo(Zarr, keV_tau)
    tauE = tauE[0,:]
    angle_ratio = np.sin(np.radians(theta_in))/np.sin(np.radians(theta_out))
    absorption_term = tauE * 2 * pz_bar * angle_ratio
    absorption_term = absorption_term.clip(min=0.00001)
    absorption_factor = ((1-np.exp(-absorption_term))/absorption_term)
    return absorption_factor


# In[324]:

## 1/Sjk in characteristic equation ##
@jit
def calc_stopping_factor(Z, kVp, keV_edge, shell):
    U0 = kVp / keV_edge
    if shell == 0:
        zS = 2
        bS = 0.35
    else:
        zS = 8
        bS = 0.25
    J = 0.0135*Z
    SF = (np.sqrt(U0)*np.log(U0) + 2*(1-np.sqrt(U0)))/(U0*np.log(U0) + 1 - U0)
    SF = (SF * np.sqrt(J/keV_edge) * 16.05) + 1
    SF = SF * (U0*np.log(U0) + 1 - U0) * ((zS * bS)/Z)
    return SF


# In[325]:

## R in characteristic equation ##
@jit
def calc_backscatter_factor(Z, kVp, keV_edge):
    U0 = kVp / keV_edge
    R = 1 - 0.0081517*Z + (3.613*(10**-5))*(Z**2) + 0.009583*Z*np.exp(-U0) + 0.001141*kVp
    return R


# ## Continuum Calculation

# In[326]:

@jit
def generate_continuum(Z, kVp, theta_in, theta_out, dE):
    Zarr = np.array([Z])
    keV = np.arange(1.0,(kVp + dE),dE)
    src = np.zeros(shape=(len(keV),2))
    src[:,0] = keV
    
    const = 1.35 * (10**9)
    x = 1.109 - 0.00435*Z + 0.00175*kVp
    U0 = kVp / keV
    Udiff = U0 - 1
    Udiff[Udiff < 0] = 0
    Ibasic = const * Z * (Udiff**x) * dE
    
    absorption_factor = calc_absorption_factor(Z, kVp, theta_in, theta_out, keV, keV)
    src[:,1] = Ibasic * absorption_factor
    return src


# ## Characteristic Peak Calculation

# In[327]:

@jit
def generate_peaks_for_shell(Z, kVp, theta_in, theta_out, shell, lines):
    Zarr = np.array([Z])
    abs_edge_arr = xray.EdgeEnergy(Zarr, shell)
    abs_edge = abs_edge_arr[0,0]
    fluor_yield_arr = xray.FluorYield(Zarr, shell)
    fluor_yield = fluor_yield_arr[0,0]
    line_keV_arr = xray.LineEnergy(Zarr, lines)
    line_keV = line_keV_arr[0,:]
    line_rate_arr = xray.RadRate(Zarr, lines)
    line_rate = line_rate_arr[0,:]
    
    if (kVp > abs_edge):
        const = 6 * (10**13)
        abs_f = calc_absorption_factor(Z, kVp, theta_in, theta_out, abs_edge, line_keV)
        stop_f = calc_stopping_factor(Z, kVp, abs_edge, shell)
        back_f = calc_backscatter_factor(Z, kVp, abs_edge)
        line_intensity = const * stop_f * back_f * fluor_yield * line_rate * abs_f
        peaks = np.column_stack((line_keV,line_intensity))
        return peaks
    else:
        return np.array([[0.0,0.0]])


# In[328]:

@jit
def generate_K_peaks(Z, kVp, theta_in, theta_out):
    shell = np.array([xray.K_SHELL])
    lines = np.array([xray.KL3_LINE, xray.KL2_LINE, xray.KM3_LINE, xray.KM2_LINE])
    K_peaks = generate_peaks_for_shell(Z, kVp, theta_in, theta_out, shell, lines)
    return K_peaks


# In[329]:

@jit
def generate_L3_peaks(Z, kVp, theta_in, theta_out):
    shell = np.array([xray.L3_SHELL])
    lines = np.array([xray.L3M5_LINE, xray.L3M4_LINE])
    L3_peaks = generate_peaks_for_shell(Z, kVp, theta_in, theta_out, shell, lines)
    return L3_peaks


# In[330]:

@jit
def generate_L2_peaks(Z, kVp, theta_in, theta_out):
    shell = np.array([xray.L2_SHELL])
    lines = np.array([xray.L2M4_LINE])
    L2_peaks = generate_peaks_for_shell(Z, kVp, theta_in, theta_out, shell, lines)
    return L2_peaks


# In[331]:

@jit
def generate_L1_peaks(Z, kVp, theta_in, theta_out):
    shell = np.array([xray.L1_SHELL])
    lines = np.array([xray.L1M3_LINE, xray.L1M2_LINE])
    L1_peaks = generate_peaks_for_shell(Z, kVp, theta_in, theta_out, shell, lines)
    return L1_peaks


# ## Merges the Characteristic Peaks with the Continuum

# In[332]:

@jit
def calc_Erow(Ei, energies):
    minE = energies[0]
    maxE = energies[len(energies)-1]
    delE = energies[1] - energies[0]
    num_steps = np.around((Ei - minE)/delE, decimals=0)
    max_steps = np.around((maxE - minE)/delE, decimals=0)
    if (num_steps < 0):
        num_steps = 0
    elif (num_steps > max_steps):
        num_steps = max_steps
    return int(num_steps)


# In[333]:

@jit
def merge_lines_continuum(cont, char):
    tot = np.copy(cont)
    for i,_ in enumerate(char):
        Erow = calc_Erow(char[i,0], cont[:,0])
        tot[Erow,1] = tot[Erow,1] + char[i,1]
    return tot


# ## Main Function to Call

# In[334]:

@jit
def spectrum(Z, kVp, mA, s, theta_in, theta_out, dE):
    cont = generate_continuum(Z, kVp, theta_in, theta_out, dE)
    K_peaks = generate_K_peaks(Z, kVp, theta_in, theta_out)
    L3_peaks = generate_L3_peaks(Z, kVp, theta_in, theta_out)
    L2_peaks = generate_L2_peaks(Z, kVp, theta_in, theta_out)
    L1_peaks = generate_L1_peaks(Z, kVp, theta_in, theta_out)
    char = np.concatenate((K_peaks, L3_peaks, L2_peaks, L1_peaks), axis=0)
    tot = merge_lines_continuum(cont, char)
    tot[:,1] = mA * s * tot[:,1]
    return tot

