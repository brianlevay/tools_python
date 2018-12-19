
# coding: utf-8

# # Matrix Files

# Generate .spe matrix files from PyMCA csv outputs

# In[20]:

import os
import pandas as pd


# In[21]:

def extract_matrix(src_dir, out_dir):
    for root, dirs, files in os.walk(src_dir):
        for fname in files:
            if (fname.find(".csv") != -1):
                contents = pd.read_csv(os.path.join(root, fname))
                matrix = contents['ymatrix'].tolist()
                with open(os.path.join(out_dir, fname.replace(".csv",".spe")),'w') as f:
                    f.write("$DATA:\n0 2047\n")
                    for i,val in enumerate(matrix):
                        if ((i+1) % 10 == 0) | (i == len(matrix)-1):
                            f.write("{0:.0f}\n".format(val))
                        else:
                            f.write("{0:.0f}  ".format(val))
                        
    return None


# In[22]:

src_dir = os.path.join(os.getcwd(),"src")
out_dir = os.path.join(os.getcwd(),"out")

extract_matrix(src_dir, out_dir)

