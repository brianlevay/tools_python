
# coding: utf-8

# # Convert Batch of SPE Files to a Single CSV

# In[1]:

import os
import re
import numpy as np
import pandas as pd


# In[2]:

src = 'C:\\Users\\levay_b\\Work\\Lab_Documents\\For_Project\\Data_Processing_and_QC\\XMI-Output'
src_dir = os.path.join(src,"")
out_dir = os.path.join(os.getcwd(),"out")
print(src_dir)
print(out_dir)


# In[3]:

def get_spe_data(src_dir, out_dir):
    channels = np.arange(2048)
    maxE = 0.02*2048
    energies = np.arange(0.0, maxE, 0.02, dtype=np.float)
    spe_df = pd.DataFrame(data={'channels':channels, 'keV':energies})
    
    counts = np.zeros(2048)
    for root, dirs, files in os.walk(src_dir):
        for fname in files:
            if (fname.find(".spe") != -1):
                valCt = 0
                dataFlag = False
                channelFlag = False
                with open(os.path.join(root, fname)) as f:
                    lines = f.readlines()
                for line in lines:
                    vals = line.strip().split()
                    if (len(vals) == 1):
                        if (vals[0] == "$DATA:"):
                            dataFlag = True
                    if (len(vals) >= 2):
                        if (vals[0] == "0") & (vals[1] == "2047"):
                            channelFlag = True
                        elif (dataFlag == True) & (channelFlag == True):
                            for val in vals:
                                counts[valCt] = val
                                valCt = valCt + 1
                spe_df[fname] = counts
    return spe_df


# In[4]:

spe_df = get_spe_data(src_dir, out_dir)
spe_df.to_csv(os.path.join(out_dir,"data.csv"),index=False)
spe_df

