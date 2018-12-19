
# coding: utf-8

# # X-Ray Fluorescence and Scattering
# 
# Generates an x-ray emission spectrum in units of counts / steradian based on the de Boer (1990) model for fluorescence. Includes Compton and Rayleigh scattering using similar forms of the de Boer equation. Uses xraylib_np for all x-ray and material values.

# ## Imports

# In[44]:

import numpy as np
import xraylib_np as xraylib
from numba import jit


# ## Support Functions

# In[45]:

@jit
def div_aDa(num_a, den_a):
    return np.divide(num_a, den_a, out=np.zeros_like(num_a), where=den_a!=0)


# In[46]:

@jit
def div_aDn(num_a, den_n):
    if den_n != 0:
        return num_a / den_n
    else:
        return np.zeros_like(num_a)


# In[47]:

@jit
def div_nDa(num_n, den_a):
    num_a = np.full(len(den_a), num_n, dtype=den_a.dtype)
    return np.divide(num_a, den_a, out=np.zeros_like(num_a), where=den_a!=0)


# In[48]:

@jit
def div_nDn(num_n, den_n):
    if den_n != 0:
        return num_n / den_n
    else:
        return 0.0


# ## Functions for Energy Conversions

# In[49]:

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


# In[50]:

@jit
def compton_shift(compton_E, EC):
    shifted = np.copy(compton_E)
    shifted[:,1] = 0
    for i,_ in enumerate(EC):
        Erow = calc_Erow(EC[i], compton_E[:,0])
        shifted[Erow,1] = shifted[Erow,1] + compton_E[i,1]
    return shifted


# ## Functions for X-Ray Emission

# In[51]:

@jit
def fluor_K_bulk(Z_arr, C_arr, beam, phi_in, phi_out):
    fluor = np.copy(beam)
    fluor[:,1] = 0
    sin_phi1 = np.sin(np.radians(phi_in))
    sin_phi2 = np.sin(np.radians(phi_out))
    lines = np.array([xraylib.KL3_LINE, xraylib.KL2_LINE, 
                      xraylib.KL1_LINE, xraylib.KM3_LINE, 
                      xraylib.KN3_LINE, xraylib.KM2_LINE, 
                      xraylib.KN5_LINE, xraylib.KM5_LINE])
    shells = np.array([xraylib.K_SHELL])
    
    ## Values from xraylib ##
    EKL = xraylib.LineEnergy(Z_arr, lines)  ## [Z,line]
    muE = xraylib.CS_Total(Z_arr, beam[:,0])  ## [Z,E]
    tauE = xraylib.CS_Photo(Z_arr, beam[:,0])  ## [Z,E]
    sigmaKE = xraylib.CS_Photo_Partial(Z_arr, shells, beam[:,0])  ## [Z,shell,E]
    wK = xraylib.FluorYield(Z_arr, shells)  ## [Z,shell]
    pKL = xraylib.RadRate(Z_arr, lines)  ## [Z,line]
    
    ## muSE is mass attenuation coefficient for sample ##
    muSE = np.tensordot(muE, C_arr, axes=([0],[0]))
    muSE_in = muSE / sin_phi1
    muSE_out = muSE / sin_phi2

    for i,_ in enumerate(Z_arr):
        for k,_ in enumerate(lines):
            Erow_i = calc_Erow(EKL[i,k], beam[:,0])
            eps_i = div_aDa(sigmaKE[i,0,:],tauE[i,:]) * wK[i,0] * pKL[i,k]
            mu_corr_i = div_nDa(1.0,(muSE_in[:] + muSE_out[Erow_i]))
            
            P_arr = (1.0/(4.0*np.pi)) * (1.0/sin_phi1) * C_arr[i] * eps_i * tauE[i,:] * mu_corr_i
            fluor[Erow_i,1] = np.sum(beam[:,1] * P_arr)    
    
            for j,_ in enumerate(Z_arr):
                for m,_ in enumerate(lines):
                    if ((i!=j) and (k!=m)):
                        Erow_j = calc_Erow(EKL[j,m], beam[:,0])
                        eps_j = div_aDa(sigmaKE[j,0,:], tauE[j,:]) * wK[j,0] * pKL[j,m]
                        Jratio = div_nDa(sigmaKE[i,0,Erow_j], sigmaKE[i,0,:])
                        tau_corr = (div_aDa(tauE[j,:], tauE[i,:]) * 
                                    div_nDn(tauE[i,Erow_j], muSE[Erow_j]))
                        L1 = (div_nDn(muSE[Erow_j], muSE_out[Erow_i]) * 
                              np.log(1.0 + div_nDn(muSE_out[Erow_i], muSE[Erow_j])))
                        L2 = (div_nDa(muSE[Erow_j], muSE_in[:]) * 
                              np.log(1.0 + div_aDn(muSE_in[:], muSE[Erow_j])))
                        L = L1 + L2
                        
                        S_arr = P_arr * (1.0/2.0) * C_arr[j] * eps_j * Jratio * tau_corr * L
                        fluor[Erow_i,1] = fluor[Erow_i,1] + np.sum(beam[:,1] * S_arr)
    return fluor


# In[52]:

@jit
def rayleigh_bulk(Z_arr, C_arr, beam, phi_in, phi_out):
    rayleigh = np.copy(beam)
    rayleigh[:,1] = 0
    sin_phi1 = np.sin(np.radians(phi_in))
    sin_phi2 = np.sin(np.radians(phi_out))
    theta = np.radians((180 - phi_in - phi_out))
    
    ## Values from xraylib ##
    muE = xraylib.CS_Total(Z_arr, beam[:,0])  ## [Z,E]
    sigmaRE = xraylib.DCS_Rayl(Z_arr, beam[:,0], np.array([theta]))  ## [Z,E,theta]
    
    for i,_ in enumerate(Z_arr):
        Ra_arr = ((1.0/sin_phi1) * C_arr[i] * sigmaRE[i,:,0] *
                  div_nDa(1.0, ((muE[i,:]/sin_phi1)+(muE[i,:]/sin_phi2))))
        rayleigh[:,1] = rayleigh[:,1] + (beam[:,1] * Ra_arr[:])
    
    return rayleigh


# In[53]:

@jit
def compton_bulk(Z_arr, C_arr, beam, phi_in, phi_out):
    compton_E = np.copy(beam)
    compton_E[:,1] = 0
    sin_phi1 = np.sin(np.radians(phi_in))
    sin_phi2 = np.sin(np.radians(phi_out))
    theta = np.radians((180.0 - phi_in - phi_out))
    
    ## Values from xraylib ##
    EC = xraylib.ComptonEnergy(beam[:,0], np.array([theta]))  ## [E,theta]
    muE = xraylib.CS_Total(Z_arr, beam[:,0])  ## [Z,E]
    muEC = xraylib.CS_Total(Z_arr, EC[:,0])  ## [Z,E]
    sigmaCE = xraylib.DCS_Compt(Z_arr, beam[:,0], np.array([theta]))  ## [Z,E,theta]
    
    for i,_ in enumerate(Z_arr):
        Co_arr = ((1.0/sin_phi1) * C_arr[i] * sigmaCE[i,:,0] *
                  div_nDa(1.0/((muE[i,:]/sin_phi1)+(muEC[i,:]/sin_phi2))))
        compton_E[:,1] = compton_E[:,1] + (beam[:,1] * Co_arr[:])
    
    compton = compton_shift(compton_E, EC[:,0])
    return compton


# ## Main Function to Call

# In[54]:

@jit
def emission_bulk(Z_arr, C_arr, beam, phi_in, phi_out):
    fluor = fluor_K_bulk(Z_arr, C_arr, beam, phi_in, phi_out)
    rayleigh = rayleigh_bulk(Z_arr, C_arr, beam, phi_in, phi_out)
    compton = compton_bulk(Z_arr, C_arr, beam, phi_in, phi_out)
    total = np.copy(fluor)
    total[:,1] = fluor[:,1] + rayleigh[:,1] + compton[:,1]
    return total

