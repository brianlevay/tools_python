
# coding: utf-8

# # Adding Dates and Merging XRF Standards Files

# In[1]:

import os
import shutil


# In[2]:

src = 'C:\\Users\\levay_b\\Work\\XRF_Data\\Standards\\Standards_Old\\Raw\\Pre-Avaatech'
src_dir = os.path.join(src,"")
#src_dir = os.path.join(os.getcwd(),"src")
out_dir = os.path.join(os.getcwd(),"out")


# In[3]:

def sort_add_dates(src_dir,out_dir):
    for root, dirs, files in os.walk(src_dir):
        dirname = os.path.split(root)[1]
        dest_path = os.path.join(out_dir,"")
        for file in files:
            spe_loc = file.find(".spe")
            if (spe_loc != -1):
                orig_file_path = os.path.join(root,file)
                file_mod = file.replace(",",".").replace("_","-").replace(".spe"," "+dirname+".spe")
                new_file_path = os.path.join(dest_path,file_mod)
                if (os.path.isfile(new_file_path) == False):
                    shutil.copyfile(orig_file_path, new_file_path)
    return None


# In[5]:

sort_add_dates(src_dir,out_dir)

