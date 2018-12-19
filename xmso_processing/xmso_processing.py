
# coding: utf-8

# ## XMSO Data Extraction

# Within XML root (xmimsim-results):
# 
#  [0] = inputfile  
#  [1] = spectrum conv (convoluted with detector)  
#  [2] = spectrum unconv (unconvoluted with detector)  
#  ...  
# 
# Within each XML channel element:
#  
#  [0] = channel number  
#  [1] = energy  
#  [2] = counts, interaction number 1  
#  [3] = counts, interaction number 2  
#  [4] = counts, interaction number 3  
#  [5] = counts, interaction number 4

# ## Imports

# In[1]:

import os
import xml.etree.ElementTree as ET


# ## Functions to Write Each XMSO Output to a New File

# In[2]:

def xmso_to_csv(input_folder, output_folder):
    for root, dirs, files in os.walk(input_folder):
        for file in files:
            path = os.path.join(root, file)
            name, ext = os.path.splitext(file)
            if ext == '.xmso':
                data = []
                xml_tree = ET.parse(path)
                xml_root = xml_tree.getroot()
                xml_spectrum_conv = xml_root[1]
                for channel in xml_spectrum_conv:
                    data.append([channel[1].text, channel[5].text])

                output_name = name + ".csv"
                output_path = os.path.join(output_folder, output_name)
                output_file = open(output_path, 'w+')
                for value in data:
                    output_file.write("{:s},{:s}\n".format(value[0],value[1]))
                output_file.close()


# In[3]:

def xmso_to_spe(input_folder, output_folder):
    for root, dirs, files in os.walk(input_folder):
        for file in files:
            path = os.path.join(root, file)
            name, ext = os.path.splitext(file)
            if ext == '.xmso':
                data = []
                xml_tree = ET.parse(path)
                xml_root = xml_tree.getroot()
                xml_spectrum_conv = xml_root[1]
                for channel in xml_spectrum_conv:
                    data.append(channel[5].text)
                ndata = len(data)
                
                output_name = name + ".spe"
                output_path = os.path.join(output_folder, output_name)
                output_file = open(output_path, 'w+')
                
                output_file.write("$DATA:\n")
                output_file.write("0   2047\n")
                for i, value in enumerate(data):
                    if ((((i+1)%6 == 0) and (i > 0)) or (i == (ndata-1))):
                        output_file.write("{:s}\n".format(value))
                    else:
                        output_file.write("{:s}    ".format(value))
                
                output_file.close()


# ## Running the Program

# In[4]:

input_folder = 'C:\\Users\\levay_b\\Work\\XRF_Data\\Accessory_Tests\\Simulation\\outputs\\30kVp'
output_folder = 'C:\\Users\\levay_b\\Work\\XRF_Data\\Accessory_Tests\\Simulation\\outputs\\30kVp\\spe'
os.listdir(input_folder)


# In[5]:

xmso_to_spe(input_folder, output_folder)

