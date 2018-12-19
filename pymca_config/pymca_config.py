
# coding: utf-8

# # PyMCA Configuration File Generator

# This (for now) populates a pymca configuration file with a dictionary of custom material compositions

# In[51]:

import os
import pandas as pd


# In[52]:

def get_materials(mat_fname):
    materials = pd.read_csv(os.path.join(src_dir, mat_fname))
    return materials


# In[53]:

def create_mixes(materials, n_steps):
    mat_list = ["Clays and Shales", "Sandstones", "Deep-Sea Carbonates"]
    abb_list = ["CS", "SS", "CC"]
    rho_list = [2.2, 2.5, 2.8]
    mixes = []
    amt = round(1/n_steps,2)
    elementStr = ", ".join(map(str, materials['Element (wt%)'].values))
    for n in range(0,n_steps+1):
        amt1 = amt*(n_steps - n)
        amt2 = amt*n
        for i, valI in enumerate(mat_list):
            for j, valJ in enumerate(mat_list):
                if (j > i):
                    mix = (amt1*materials[mat_list[i]] + amt2*materials[mat_list[j]])/100
                    name = "{2:s}*{0:d}-{3:s}*{1:d}".format(int(100*amt1),int(100*amt2),abb_list[i],abb_list[j])
                    title = "[materials.{0:s}]".format(name)
                    compStr = ", ".join(map(str, mix))
                    mixes.append(title)
                    mixes.append("Comment = New Material")
                    mixes.append("Density = {0:.2f}".format(amt1*rho_list[i] + amt2*rho_list[j]))
                    mixes.append("Thickness = 3.0")
                    mixes.append("CompoundList = {0:s}".format(elementStr))
                    mixes.append("CompoundFraction = {0:s}".format(compStr))
                    mixes.append("")
    mixesStr = "\n".join(mixes)
    return mixesStr


# In[54]:

def mixes_to_cfg(mixes, cfg_fname):
    with open(os.path.join(src_dir, cfg_fname),'r') as fIn:
        lines = fIn.readlines()
    fIn.close()
    with open(os.path.join(out_dir,"mixes_config.cfg"),'w') as fOut:
        for line in lines:
            fOut.write(line)
            if (line == "[materials]\n"):
                fOut.write("\n" + mixes + "\n")
    fOut.close()
    return None


# In[55]:

src = 'C:\\Users\\levay_b\\Work\\General_Scripts\\python\\pymca_config\src'
src_dir = os.path.join(src,"")
out_dir = os.path.join(os.getcwd(),"out")

materials = get_materials("Sediment_Mix.csv")
mixesStr = create_mixes(materials, 10)
mixes_to_cfg(mixesStr, "pymca_v2_settings.cfg")

