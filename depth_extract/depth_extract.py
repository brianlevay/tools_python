
# coding: utf-8

# # Extracting a List of Depths from XRF Files

# Fill in later...

# In[8]:

import os
import re
import numpy as np
import pandas as pd


# In[34]:

def get_stats(fpath):
    with open(fpath) as f:
        lines = f.readlines()
    cpsLine = 1
    timeLine = 1
    cps = 0
    measured = 0
    actual = 0
    for i,line in enumerate(lines):
        if (line == "$TotalCPS:\n"):
            cpsLine = i+1
        if (line == "$MEAS_TIM:\n"):
            timeLine = i+1
    try:
        cps = int(lines[cpsLine])
        times = lines[timeLine].split()
        measured = int(times[0])
        actual = int(times[1])
    except:
        pass
    stats = {"cps":cps, "meas":measured, "act":actual}
    return stats


# In[15]:

def get_xrf_points_old(src_dir,out_dir):
    cols = ['sample','x','y','dc','cc','kV','cps','meas','act']
    rows_list = []
    for root, dirs, files in os.walk(src_dir):
        for fn in files:
            success = True
            if (fn.find(".spe") != -1):
                fn_pts = fn.split()
                sample = fn_pts[0]
                x_search = re.search(r'X\s*.{3,6}mm', fn)
                x = x_search.group()
                y_search = re.search(r'Y\s*.{1,6}mm', fn)
                y = y_search.group()
                dc_search = re.search(r'DC\s*.{1,6}mm', fn)
                dc = dc_search.group()
                cc_search = re.search(r'CC\s*.{1,6}mm', fn)
                cc = cc_search.group()
                kV_search = re.search(r'.{1,2}kV', fn)
                kV = kV_search.group()
                try:
                    x = float(x[1:-2])
                    y = float(y[1:-2])
                    dc = float(dc[2:-2])
                    cc = float(cc[2:-2])
                    kV = int(kV[0:-2])
                except:
                    success = False
                if (success == True):
                    stats = get_stats(os.path.join(root, fn))
                    row = {'sample':sample,'x':x,'y':y,'dc':dc,'cc':cc,'kV':kV,'cps':stats['cps'],'meas':stats['meas'],'act':stats['act']}
                    rows_list.append(row)
    points_df = pd.DataFrame(rows_list)
    return points_df


# In[16]:

def get_xrf_points_new(src_dir,out_dir):
    cols = ['sample','x','y','dc','cc','kV']
    rows_list = []
    for root, dirs, files in os.walk(src_dir):
        for fn in files:
            success = True
            if (fn.find(".spe") != -1):
                fn_pts = fn.split("!")
                sample = fn_pts[0]
                x = fn_pts[9]
                y = fn_pts[10]
                dc = fn_pts[12]
                cc = fn_pts[13]
                kV = fn_pts[7]
                try:
                    x = float(x)
                    y = float(y)
                    dc = float(dc)
                    cc = float(cc)
                    kV = int(kV)
                except:
                    success = False
                if (success == True):
                    stats = get_stats(os.path.join(root, fn))
                    row = {'sample':sample,'x':x,'y':y,'dc':dc,'cc':cc,'kV':kV,'cps':stats['cps'],'meas':stats['meas'],'act':stats['act']}
                    rows_list.append(row)
    points_df = pd.DataFrame(rows_list)
    return points_df


# In[12]:

def get_unique_pts(points_df, sample="All"):
    if (sample == "All"):
        sample_vals = points_df["sample"].unique()
    else:
        sample_vals[sample]
    for sample in sample_vals:
        sample_set = points_df[points_df["sample"]==sample]
        y_vals = sample_set["y"].unique()
        for y in y_vals:
            y_set = sample_set[sample_set["y"]==y]
            cc_vals = y_set["cc"].unique()
            for cc in cc_vals:
                cc_set = y_set[y_set["cc"]==cc]
                dc_vals = cc_set["dc"].unique()
                for dc in dc_vals:
                    dc_set = cc_set[cc_set["dc"]==dc]
                    unique_x = dc_set["x"].unique()
                    filename = sample + "-Y" + str(y) + "-CC" + str(cc) + "-DC" + str(dc) + ".txt"
                    file_path = os.path.join(os.getcwd(),"out",filename)
                    new_file = open(file_path,"w")
                    for item in unique_x:
                        new_file.write("%s\n" % item)
                    new_file.close()
    return None


# In[36]:

#src = 'C:\\Users\\levay_b\\Work\\XRF_Data\\Users\\367\\U1499A'
src_dir = os.path.join(os.getcwd(),"src")
out_dir = os.path.join(os.getcwd(),"out")

points_df = get_xrf_points_new(src_dir,out_dir)
points_df.to_csv(os.path.join(out_dir,"stats.csv"))

#get_unique_pts(points_df)

