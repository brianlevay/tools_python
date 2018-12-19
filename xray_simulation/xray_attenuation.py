
# coding: utf-8

# # X-Ray Attenuation and Solid Angle Calculation

# ## Imports

# In[6]:

import numpy as np
import xraylib_np as xraylib
from numba import jit


# ## Utility Functions

# In[7]:

@jit
def unpack(material):
    Z = []
    C = []
    for el in material:
        Z.append(el)
        C.append(material[el])
    return np.asarray(Z), np.asarray(C)


# ## Calculate mu_rho and Attenuation for a Single Material

# In[8]:

@jit
def calc_mu_rho(mat, comps, rhos, energies):
    Z,C = unpack(comps[mat])
    rho = rhos[mat]
    mu_Z = xraylib.CS_Total(Z, energies)
    mu = np.tensordot(mu_Z, C, axes=([0],[0]))
    mu_rho = mu * rho
    return mu_rho


# In[10]:

@jit
def attenuate(incoming, mu_rho, t): 
    transmit = np.copy(incoming)
    interact = np.copy(incoming)
    transmit[:,1] = incoming[:,1] * np.exp(-mu_rho[:] * t)
    interact[:,1] = incoming[:,1] - transmit[:,1]
    return transmit, interact


# ## Calculate mu_rho and Attenuation for Multiple Materials

# Based on materials dictionary and path array of forms: 
# 
# materials = {'mat1': 1, 'mat2': 2, 'mat3': 3, ...}  
# path = [[t1, 1], [t3, 3], [t2, 2], ...]

# In[9]:

@jit
def calc_mu_rho_arr(materials, comps, rhos, energies):
    mu_rho_arr = np.ndarray(shape=(len(energies),(len(materials)+1)), dtype=float)
    mu_rho_arr[:,0] = energies
    for num in materials:
        mat = materials[num]
        mu_rho = calc_mu_rho(mat, comps, rhos, energies)
        mu_rho_arr[:,num] = mu_rho
    return mu_rho_arr


# In[ ]:

def attenuate_path(incoming, path, mu_rho_arr):
    transmit = np.copy(incoming)
    interact = np.copy(incoming)
    for seg in path:
        mu_rho = mu_rho_arr[:,int(seg[1])]
        transmit[:,1] = transmit[:,1] * np.exp(-mu_rho[:] * seg[0])
    interact[:,1] = incoming[:,1] - transmit[:,1]
    return transmit, interact


# ## Calculate Solid Angles

# In[11]:

@jit
def calc_omega_cone(radius, distance):
    theta = np.arctan(radius / distance)
    omega = 2 * np.pi * (1 - np.cos(theta))
    return omega


# In[12]:

@jit
def calc_omega_pyramid(a_side, b_side, distance):
    numer = a_side * b_side
    denom = 2 * distance * np.sqrt(4*distance**2 + a_side**2 + a_side**2)
    omega = 4 * np.arctan(numer/denom)
    return omega

