
# coding: utf-8

# In[1]:

import math
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


# In[2]:

bg_vals = [10, 20, 50, 100, 200, 500, 1000, 2000, 5000, 10000, 20000, 50000]
x_vals = np.zeros((len(bg_vals),), dtype=np.int)
exp_vals = np.zeros((len(bg_vals),), dtype=np.int)
mod_vals = np.zeros((len(bg_vals),), dtype=np.int)

for i,val in enumerate(bg_vals):
    bg_ave = val
    bg_std = math.sqrt(bg_ave)

    peak_fwhm = 140
    e_channels = 20
    block_width = int(peak_fwhm / e_channels)
    n_channels = 3 * block_width

    reps = 100000
    net_peaks = np.zeros((reps,), dtype=np.int)

    for rep in range(reps):
        ref1 = bg_std * np.random.randn(block_width) + bg_ave
        peak = bg_std * np.random.randn(block_width) + bg_ave
        ref2 = bg_std * np.random.randn(block_width) + bg_ave
    
        ref1_area = np.sum(ref1)
        peak_area = np.sum(peak)
        ref2_area = np.sum(ref2)
    
        background = (ref1_area + ref2_area)/2
        net_peaks[rep] = int(peak_area - background)

    net_peaks_sorted = np.sort(net_peaks)
    per95_k = int(0.95*reps)
    min_peak_model = net_peaks_sorted[per95_k]
    min_peak_exp = 2*math.sqrt(bg_ave*block_width)
    
    x_vals[i] = int(bg_ave*block_width)
    exp_vals[i] = int(min_peak_exp)
    mod_vals[i] = int(min_peak_model)


fig = plt.figure(figsize=(10,6))
ax1 = fig.add_subplot(1,1,1)
ax1.scatter(x_vals, exp_vals, label="Expected")
ax1.scatter(x_vals, mod_vals, label="Modelled")
ax1.legend()
ax1.set_xlabel("Background Area")
ax1.set_ylabel("Min Peak Area for Significance")
plt.show()


# In[6]:

cells = np.random.choice(range(100),33,replace=False)
print(cells)

