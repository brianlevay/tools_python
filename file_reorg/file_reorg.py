
# coding: utf-8

# # File Sorting For XRF Data

# This code will search through all subdirectories in "src_dir", looking for folders with "Run" and "{E}kV" in the name, where {E} is a specified energy value. It will then copy all files in those folders to the appropriate folders in "out_dir", based on {E}.

# In[1]:

import os
import shutil

src = 'C:\\Users\\levay_b\\Work\\XRF_Data\\Users\\367\\U1499A'
src_dir = os.path.join(src,"")
out_dir = os.path.join(os.getcwd(),"out")


# In[2]:

def sort_by_energy(src_dir,out_dir,energies):
    for energy in energies:
        energy_path = os.path.join(out_dir,str(energy)+"kV")
        if (os.path.isdir(energy_path) == False):
            os.mkdir(energy_path)

    for root, dirs, files in os.walk(src_dir):
        dirname = os.path.split(root)[1]
        run_loc = dirname.find("Run")
        if (run_loc) != -1:
            for energy in energies:
                energy_str = str(energy) + "kV"
                energy_loc = dirname.find(energy_str)
                if (energy_loc) != -1:
                    dest_path = os.path.join(out_dir,energy_str)
                    for file in files:
                        orig_file_path = os.path.join(root,file)
                        new_file_path = os.path.join(dest_path,file)
                        if (os.path.isfile(new_file_path) == False):
                            shutil.copy(orig_file_path, dest_path)
    return None


# In[3]:

sort_by_energy(src_dir,out_dir,[10,30,50])

