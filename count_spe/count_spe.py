
# coding: utf-8

# # Counting SPE Files by Hole and Energy

# In[1]:

import os
import re
import pandas as pd


# Regex tests

# In[55]:

test_str = 'U1489-1H-4A   40.0mm   6s   9kV 250uA No-Filter'
test_search = re.search(r'U[a-zA-Z0-9]{4,5}', test_str)
test_found = test_search.group(0)
test_found


# Building the data structure

# In[59]:

def build_ds(src_root):
    users = os.listdir(src_root)
    energies = set()
    holes = set()
    for root, dirs, files in os.walk(src_root):
        for file in files:
            if (file.find(".spe") != -1):
                kV_search = re.search(r'.{1,2}kV', file)
                try:
                    kV_found = kV_search.group()
                    kV_val = int(kV_found[0:-2])
                    energies.add(kV_val)
                except:
                    pass
                hole_search = re.search(r'U[a-zA-Z0-9]{4,5}', file)
                try:
                    hole_found = hole_search.group()
                    holes.add(hole_found)
                except:
                    pass
    energies = list(energies)
    holes = list(holes)
    stats_dict = {}
    for user in users:
        stats_dict[user] = {}
        for hole in holes:
            stats_dict[user][hole] = {}
            for energy in energies:
                stats_dict[user][hole][energy] = 0
    return stats_dict


# Counting the files

# In[60]:

def count_spe_files(src_root, stats_dict):
    filled_stats = stats_dict.copy()
    users = os.listdir(src_root)
    for user in users:
        src_dir = os.path.join(src_root, user)
        for root, dirs, files in os.walk(src_dir):
            for file in files:
                if (file.find(".spe") != -1):
                    kV_search = re.search(r'.{1,2}kV', file)
                    hole_search = re.search(r'U[a-zA-Z0-9]{4,5}', file)
                    try:
                        kV_found = kV_search.group()
                        kV_val = int(kV_found[0:-2])
                        hole_found = hole_search.group()
                        filled_stats[user][hole_found][kV_val] += 1
                    except:
                        pass
    return filled_stats


# Flattens the data structure to create a dataframe

# In[65]:

# want each row in form {'user':user, 'hole':hole, '9':0, '30':0, '50':0}

def nested_dict_to_df(nested_dict):
    flattened_list = []
    for user in nested_dict:
        for hole in nested_dict[user]:
            row = {'user':user, 'hole':hole}
            for energy in nested_dict[user][hole]:
                row[energy] = nested_dict[user][hole][energy]
            flattened_list.append(row)
    flattened_df = pd.DataFrame(flattened_list)
    return flattened_df


# --- Runs the functions ---

# In[71]:

src_root = 'F:\\363_Old_Host_PC\\Post-Bova_Sort'
out_dir = os.path.join(os.getcwd(),"out")


# In[63]:

stats_dict = build_ds(src_root)


# In[64]:

filled_stats = count_spe_files(src_root, stats_dict)
filled_stats


# In[73]:

flattened_df = nested_dict_to_df(filled_stats)
flattened_df.to_csv(os.path.join(out_dir,"stats_detailed.csv"))
flattened_df


# In[74]:

grouped_df = flattened_df.groupby('user').sum()
grouped_df.to_csv(os.path.join(out_dir,"stats_summary.csv"))
grouped_df


# Comparison test using counting in single pass

# In[75]:

def count_spe_files_simple(src_root):
    all_stats = []
    users = os.listdir(src_root)
    for user in users:
        user_stats = {'user':user,9:0,30:0,50:0}
        src_dir = os.path.join(src_root, user)
        for root, dirs, files in os.walk(src_dir):
            for file in files:
                if (file.find(".spe") != -1):
                    kV_search = re.search(r'.{1,2}kV', file)
                    try:
                        kV_found = kV_search.group()
                        kV_val = int(kV_found[0:-2])
                        user_stats[kV_val] += 1
                    except:
                        pass
        all_stats.append(user_stats)
        stats_df = pd.DataFrame(all_stats)
    return stats_df

simpler_df = count_spe_files_simple(src_root)
simpler_df.to_csv(os.path.join(out_dir,"stats_summary_simple.csv"))
simpler_df

