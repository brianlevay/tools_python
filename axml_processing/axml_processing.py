
# coding: utf-8

# ## AXML Data Extraction

# Within XML root (bAxil results):
# 
# * SpectralData [0]
# * ExperimentalConditions [1]
# * Model [2]
#   * Calibration [0]
#     * Zero [0]
#       * Initial [0]
#       * InitialConstraint [1]
#       * Fitted [2]
#       * FittedConstraint [3]
#       * StandardDeviation [4]
#     * Gain [1]
#       * See above
#     * Noise [2]
#       * See above
#     * Fano [3]
#       * See above
#   * ...
# * ...

# ## Imports

# In[7]:

import os
import xml.etree.ElementTree as ET


# ## Functions to Collect Each AXML Model Fit and Write to File

# In[8]:

def axml_calibration_to_csv(input_folder, output_folder, output_name):
    output_path = os.path.join(output_folder, (output_name + ".csv"))
    output_file = open(output_path, 'w+')
    output_file.write("FileName, Zero Val, Zero Std, Gain Val, Gain Std, Noise Val, Noise Std, Fano Val, Fano Std\n")
    
    for root, dirs, files in os.walk(input_folder):
        for file in files:
            path = os.path.join(root, file)
            name, ext = os.path.splitext(file)
            if ext == '.axml':
                xml_tree = ET.parse(path)
                xml_root = xml_tree.getroot()
                model = xml_root[2]
                calibration = model[0]
                zero = calibration[0]
                gain = calibration[1]
                noise = calibration[2]
                fano = calibration[3]

                zero_val = float(zero[2].text)
                zero_std = float(zero[4].text)
                gain_val = float(gain[2].text)
                gain_std = float(gain[4].text)
                noise_val = float(noise[2].text)
                noise_std = float(noise[4].text)
                fano_val = float(fano[2].text)
                fano_std = float(fano[4].text)

                output_file.write("{:s},{:.6e},{:.6e},{:.6e},{:.6e},{:.6e},{:.6e},{:.6e},{:.6e}\n".format(
                    name, zero_val, zero_std, gain_val, gain_std, 
                    noise_val, noise_std, fano_val, fano_std))
    output_file.close()


# ## Running the Program

# In[10]:

inp_folder = 'C:\\Users\\levay_b\\Work\\XRF_Data\\Model_Tests\\Standards_Fittings\\AXML_XRF_1'
out_folder = 'C:\\Users\\levay_b\\Work\\XRF_Data\\Model_Tests\\Standards_Fittings'

axml_calibration_to_csv(inp_folder, out_folder, "AXML_XRF_1_Fittings")

