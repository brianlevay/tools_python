
# coding: utf-8

# # X-Ray Detection
# 
# Converts an x-ray emission spectrum to a detected spectrum containing noise and peak overlap

# ## Imports

# In[18]:

import numpy as np
from numba import jit


# ## Gaussian Function

# In[19]:

## g(x) = [1/(std*sqrt(2pi))]*exp(-(1/2)*((x-mean)/std)^2)

@jit
def gaussian_noise(energies, Emean, Estd):
    noise = np.copy(energies)
    delta = energies[1] - energies[0]
    b = Emean
    c = Estd
    a = (1/(c*np.sqrt(2*np.pi)))
    en = -(energies-b)**2
    ed = 2*c**2
    noise = delta*a*np.exp(en/ed)
    return noise


# ## Main Function to Call

# In[20]:

@jit
def detected(emission, offset_noise, gain_noise):
    detected = np.copy(emission)
    detected[:,1] = 0
    energies = emission[:,0]
    for e,_ in enumerate(energies):
        noise = gain_noise*e + offset_noise
        vals = emission[e,1] * gaussian_noise(energies, e, noise)
        detected[:,1] = detected[:,1] + vals
    return detected

