
# coding: utf-8

# ## Imports

# In[1]:

import numpy as np
import math
from numba import jit
import matplotlib.pyplot as plt

get_ipython().magic('matplotlib inline')


# ## Solid Angle Functions

# In[2]:

@jit
def calc_omega_cone(radius, distance):
    theta = np.arctan(radius / distance)
    omega = 2 * np.pi * (1 - np.cos(theta))
    return omega


# In[3]:

@jit
def calc_omega_pyramid(a_side, b_side, distance):
    numer = a_side * b_side
    denom = 2 * distance * np.sqrt(4*distance**2 + a_side**2 + a_side**2)
    omega = 4 * np.arctan(numer/denom)
    return omega


# ## Geometry Setup

# In[4]:

@jit
def px_to_cm(px, ref_px=1548, ref_cm=15.0):
    return (ref_cm / ref_px) * px


# In[5]:

@jit
def cm_to_px(cm, ref_px=1548, ref_cm=15.0):
    return int(round((ref_px / ref_cm) * cm))


# In[6]:

img_rows_px = 1548
img_cols_px = 1032
img_rows_cm = 15.0
img_cols_cm = px_to_cm(img_cols_px)
print(img_rows_cm, img_cols_cm)


# ## Section 1: Exposure Time by Omega

# In[7]:

## n_xrays1 = source * omega1 * exposure1
## n_xrays2 = source * omega2 * exposure2
## omega1 * exposure1 = omega2 * exposure2
## omega2 / omega1 = exposure1 / exposure2
## exposure2 = exposure1 * (omega1 / omega2)


# In[8]:

dists = np.arange(20.0, 71.0, 1.0)
omegas = calc_omega_pyramid(img_rows_cm, img_cols_cm, dists)
omega_60cm = omegas[dists == 60.0]

exposures_mult = (omega_60cm / omegas)
exposures_abs = 200.0 * exposures_mult

fig = plt.figure(figsize=(10,18))
ax1 = fig.add_subplot(211)
ax1.plot(dists, exposures_mult)
ax1.set_xlabel('Source Distance (cm)')
ax1.set_ylabel('Exposure Time Multiplier')
ax1.set_title('Relative Exposure Time Based on Source Distance (Constant kVp and mA) [Normalized to 60cm]')
ax1.grid()

ax2 = fig.add_subplot(212)
ax2.plot(dists, exposures_abs)
ax2.set_xlabel('Source Distance (cm)')
ax2.set_ylabel('Exposure Time (ms)')
ax2.set_title('Exposure Time Based on Source Distance (Constant kVp and mA) [Normalized to 200ms at 60cm]') 
ax2.grid()

plt.tight_layout(pad=3.00)
plt.show()


# In[9]:

plt.plot(dists, omegas)
plt.show()


# ## Section 2A: Distortion by Angle

# In[10]:

## tan(theta) = (d/2) / z
## tan(theta) = (x/2) / y
## x = d * (y/z)


# In[11]:

@jit
def core_distortion(base_height, min_y, fig_w, fig_h):
    d = 15.0  ## width of detector
    r_core = 3.6
    r_slices = np.arange(0.0, 8.0, 1.0)
    z_arr = np.arange(20.0, 71.0, 1.0)
    
    fig = plt.figure(figsize=(fig_w,fig_h))
    ax = fig.add_subplot(111)
    
    r_slice = r_core
    h = r_slice + base_height
    yr_arr = z_arr - h
    xr_arr = d * (yr_arr / z_arr)
    ax.plot(z_arr, xr_arr, linewidth=3, label='core slice = {:.1f} cm'.format(r_slice))
    
    for r_slice in r_slices:
        h = r_slice + base_height
        yr_arr = z_arr - h
        xr_arr = d * (yr_arr / z_arr)
        ax.plot(z_arr, xr_arr, linewidth=1, label='core slice = {:.1f} cm'.format(r_slice))
    
    ax.set_xlim([min(z_arr),max(z_arr)])
    ax.set_ylim([min_y, 15.1])
    ax.set_xlabel('Source Height Above Detector (cm)')
    ax.set_ylabel('Width of Plane Visible at Detector (cm)')
    ax.set_title('Projected Width of Plane Onto {:.1f} cm Detector, Core Elevated by {:.1f} cm'.format(d, base_height))
    ax.legend(loc='lower right')
    ax.grid()
    plt.show()


# In[12]:

core_distortion(3.0, min_y=7.0, fig_w=14, fig_h=12)


# ## Section 2B: Distortion by Angle

# In[13]:

z = 30.0
h = 10.0

x_vals = np.arange(0.0, 16.0, 1.0)
d_vals = x_vals * (z / (z-h))

fig = plt.figure(figsize=(18,10))
ax = fig.add_subplot(111)

ax.scatter(x_vals, np.full(shape=len(x_vals), fill_value=h), s=80)
ax.scatter(d_vals, np.full(shape=len(d_vals), fill_value=0.0), s=80)

for val in d_vals:
    xs = np.array([0.0, val])
    ys = np.array([z, 0.0])
    ax.plot(xs, ys, color='grey')
    
ax.set_xticks(ticks=np.arange(0.0,math.ceil(max(d_vals)),1.0))
ax.set_xlabel('X Position (cm)')
ax.set_ylabel('Y Position (cm)')
ax.set_title('Projections Through Layer to Base')
ax.grid()
plt.show()


# ## Section 3: Projected Pixel Maps

# In[14]:

## Want to create multiple pixel layers at different distances from detector (and source).
## Want to then calculate which pixels a vector betwen detector pixel and source will pass through in each layer
## Finally, stack the contents and map them back to detector pixels


# In[15]:

## i = i_det + [i_src - i_det] * t
## j = i_det + [j_src - j_det] * t
## k = k_det + [k_src - k_det] * t

## k_lay = k_det + (v_k * t_lay)
## k_lay - k_det = v_k * t_lay
## t_lay = (k_lay - k_det) / v_k
## i_lay = i_det + (v_i * t_lay)
## j_lay = j_det + (v_j * t_lay)


# In[16]:

@jit
def pixel_projection(detector_map, layer_px_maps, layer_px_hts, source_px_ht):
    projected_map = np.copy(detector_map)
    
    i_src = int(round(len(detector_map)/2))
    j_src = int(round(len(detector_map[0])/2))
    k_src = source_px_ht
    
    k_det = 0
    for i_det, _ in enumerate(detector_map):
        for j_det, _ in enumerate(detector_map[i_det]):
            v_i = (i_src - i_det)
            v_j = (j_src - j_det)
            v_k = (k_src - k_det)
            for n_map, layer in enumerate(layer_px_maps):
                k_lay = layer_px_hts[n_map]
                t_lay = (k_lay - k_det) / v_k
                i_lay = int(round(i_det + (v_i * t_lay)))
                j_lay = int(round(j_det + (v_j * t_lay)))
                projected_map[i_det, j_det] += layer[i_lay, j_lay]
    
    return projected_map


# In[17]:

@jit
def create_grid_layer(detector_map, height_cm, width_cm, interval_cm, thickness_px):
    nrows, ncols = detector_map.shape
    grid_layer = np.copy(detector_map)
    interval_px = cm_to_px(interval_cm)
    
    t = int(round((thickness_px - 1) / 2))
    n_row_steps = int(round(height_cm / interval_cm))
    for n in range(0, n_row_steps):
        i_c = n * interval_px
        i_min = int(max(0, i_c-t))
        i_max = int(min(nrows-1, i_c+t+1))
        for i in range(i_min, i_max, 1):
            grid_layer[i,:] = 1.0
    
    m_col_steps = int(round(width_cm / interval_cm))
    for m in range(0, m_col_steps):
        j_c = m * interval_px
        j_min = int(max(0, j_c-t))
        j_max = int(min(ncols-1, j_c+t+1))
        for j in range(j_min, j_max, 1): 
            grid_layer[:,j] = 1.0
    
    return grid_layer


# In[18]:

detector_map = np.zeros(shape=(img_rows_px, img_cols_px))
grid_layer = create_grid_layer(detector_map, img_rows_cm, img_cols_cm, 1.0, 4)
grid_px_ht = cm_to_px(3.6)

layer_px_maps = [grid_layer]
layer_px_hts = [grid_px_ht]
source_px_ht = cm_to_px(30.0)
projected_map = pixel_projection(detector_map, layer_px_maps, layer_px_hts, source_px_ht)


width = 12.0
nrows, ncols = projected_map.shape
height = (nrows/ncols)*width
fig = plt.figure(figsize=(width,height))
ax = fig.add_subplot(111)
ax.imshow(projected_map, cmap='gray')
plt.show()

