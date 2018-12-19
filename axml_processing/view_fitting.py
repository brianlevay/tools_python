
# coding: utf-8

# ## Imports

# In[1]:

import os
import datetime
import math
import pandas as pd
import matplotlib.pyplot as plt

get_ipython().magic('matplotlib inline')


# ## Read Data

# In[4]:

folder = 'C:\\Users\\levay_b\\Work\\XRF_Data\\Model_Tests\\Standards_Fittings\\ReducedMinDiff'

XRF1_datapath = os.path.join(folder, 'XRF1_Standards_wFit.csv')
XRF2_datapath = os.path.join(folder, 'XRF2_Standards_wFit.csv')

XRF1_data = pd.read_csv(XRF1_datapath)
XRF2_data = pd.read_csv(XRF2_datapath)


# ## Filter Bad Data

# In[5]:

XRF1_locations = XRF1_data[XRF1_data['Sample'].isin([50,100,150])]
XRF2_locations = XRF2_data[XRF2_data['Sample'].isin([50,100,150])]

XRF1_counts = XRF1_locations[XRF1_locations['Throughput'] > 10000]
XRF2_counts = XRF2_locations[XRF2_locations['Throughput'] > 10000]

XRF1_filtered = XRF1_counts[XRF1_counts['Ar-Ka Area'] < -1000]
XRF2_filtered = XRF2_counts[XRF2_counts['Ar-Ka Area'] < -1000]

XRF2_filtered = XRF2_filtered[XRF2_filtered['Noise Val'] > 0.00]
XRF2_filtered = XRF2_filtered[XRF2_filtered['Noise Val'] < 0.12]
XRF2_filtered = XRF2_filtered[XRF2_filtered['Fano Val'] < 0.14]


# ## Create Date Column For Plotting

# In[6]:

def create_datetime(row):
    timepts = row['Acquisition time'].split(":")
    return datetime.datetime(row['Year'], row['Month'], row['Day'], 
                             int(timepts[0]), int(timepts[1]), int(timepts[2]))


# In[7]:

XRF1_datetime = XRF1_filtered.apply(create_datetime, axis=1)
XRF2_datetime = XRF2_filtered.apply(create_datetime, axis=1)

XRF1_df = XRF1_filtered.copy()
XRF2_df = XRF2_filtered.copy()

XRF1_df['Datetime'] = XRF1_datetime
XRF2_df['Datetime'] = XRF2_datetime


# In[8]:

XRF1_df.columns


# ## Plot Data

# In[9]:

def plot_data(df, cols, width, height, title):
    df_50 = df[df['Sample'] == 50]
    df_100 = df[df['Sample'] == 100]
    df_150 = df[df['Sample'] == 150]
    
    n_subs = len(cols)
    fig_width = width
    fig_height = n_subs * height
    
    fig = plt.figure(figsize=(fig_width,fig_height))
    for i, col in enumerate(cols):
        ax = fig.add_subplot(n_subs, 1, (i+1))
        ax.plot_date(df_50['Datetime'], df_50[col], label='50mm')
        ax.plot_date(df_100['Datetime'], df_100[col], label='100mm')
        ax.plot_date(df_150['Datetime'], df_150[col], label='150mm')
        ax.set_xlabel('Date')
        ax.set_ylabel('Value')
        ax.set_title(title + " " + col)
        ax.legend()

    plt.tight_layout()
    plt.show()


# In[10]:

cols = ['Throughput', 'Oveall Chi2', 'Zero Val', 'Gain Val', 'Noise Val', 'Fano Val']

plot_data(XRF1_df, cols, 15.0, 7.5, "XRF1")


# In[11]:

plot_data(XRF2_df, cols, 15.0, 7.5, "XRF2")


# ## Sensitivity to Gain and Offset

# In[12]:

XRF1_ch = XRF1_df.copy()

XRF1_ch['Gain Mean'] = XRF1_ch['Gain Val'].mean()
XRF1_ch['Zero Ref'] = 0.0


# In[13]:

def channel(energy, gain, zero):
    return round((energy - zero) / gain)


# In[14]:

def channel_diffs(df, peaks, gain_ref, zero_ref):
    bins_ch = [-3.5, -2.5, -1.5, -0.5, 0.5, 1.5, 2.5, 3.5]
    n_rows = int(math.ceil(len(peaks)/2))
    n_cols = 2
    
    fig_width = n_cols * 8
    fig_height = n_rows * 7
    fig = plt.figure(figsize=(fig_width,fig_height))
    
    for i, (peak, energy) in enumerate(peaks.items()):
        col_name = peak + " DelCh"
        df[col_name] = (df.apply(lambda x: channel(energy, x[gain_ref], x[zero_ref]), axis=1) - 
                        df.apply(lambda x: channel(energy, x['Gain Val'], x['Zero Val']), axis=1))

        ax = fig.add_subplot(3, 2, (i+1))
        ax.hist(df[col_name], bins=bins_ch)
        ax.set_title(col_name)

    plt.tight_layout()
    plt.show()


# In[ ]:

# Si Ka = 1.74 keV
# Ca Ka = 3.692 keV
# Fe Ka = 6.404 keV
# Sr Ka = 14.166 keV
# Ag Ka = 22.163 keV
# Ba Ka = 32.194 keV

peaks = {'Si-Ka': 1.74, 'Ca-Ka': 3.692, 'Fe-Ka': 6.404, 'Sr-Ka': 14.166, 'Ag-Ka': 22.163, 'Ba-Ka': 32.194}

channel_diffs(XRF1_ch, peaks, 'Gain Val', 'Zero Ref')

