# Thickness Modelling for X-Ray Image Processing

# Assumptions:
# The primary assumptions are that the cylinder axis is always at the same z and is aligned with the y axis. If it's not aligned with y, a simple xy axis rotation can be performed so that y' is aligned with the axis. This will keep the math the same (and simple).  

# x and y of final image relates to column (j) and row (i) of data

import numpy as np


def _detector_coordinates(geom):
    x_row = geom['px_size'] * np.arange(0, geom['ncols'], 1) + (geom['px_size']/2.0)
    y_col = geom['px_size'] * np.arange(0, geom['nrows'], 1) + (geom['px_size']/2.0)
    x_arr = np.tile(x_row, (geom['nrows'], 1))
    y_arr = np.tile(y_col, (geom['ncols'], 1)).transpose()
    z_arr = np.zeros(shape=(geom['nrows'],geom['ncols']))
    return (x_arr, y_arr, z_arr)


def _rotate_coordinates(vals, theta):
    x_vals, y_vals, z_vals = vals
    xr_vals = x_vals * np.cos(np.radians(theta)) - y_vals * np.sin(np.radians(theta))
    yr_vals = x_vals * np.sin(np.radians(theta)) + y_vals * np.cos(np.radians(theta))
    zr_vals = z_vals
    return (xr_vals, yr_vals, zr_vals)


def _calculate_unit_vectors(src_pt, det_pts):
    vx = det_pts[0] - src_pt[0]
    vy = det_pts[1] - src_pt[1]
    vz = det_pts[2] - src_pt[2]
    vm = np.sqrt(vx**2 + vy**2 + vz**2)
    vx = vx / vm
    vy = vx / vm
    vz = vz / vm
    return (vx, vy, vz)


def calc_t_model(xy_ax, theta, geom):
    ## Calculate points in cartesian space ##
    p_det = _detector_coordinates(geom)
    p_src = (geom['x_src'], geom['y_src'], geom['src_ht'])
    p_ax = (xy_ax[0], xy_ax[1], geom['core_ht']+geom['radius'])
    
    ## Rotate coordinates ##
    pr_det = _rotate_coordinates(p_det, theta)
    pr_src = _rotate_coordinates(p_src, theta)
    pr_ax = _rotate_coordinates(p_ax, theta)
    vr = _calculate_unit_vectors(pr_src, pr_det)
    
    ## Calculate intersections ##
    A = vr[0]**2 + vr[2]**2
    B = 2*vr[0]*(pr_src[0] - pr_ax[0]) + 2*vr[2]*(pr_src[2] - pr_ax[2])
    C = (pr_src[0]**2 - 2*pr_src[0]*pr_ax[0] + pr_ax[0]**2 + 
         pr_src[2]**2 - 2*pr_src[2]*pr_ax[2] + pr_ax[2]**2 - 
         geom['radius']**2)
    det = B**2 - 4*A*C
    det[det < 0] = 0
    t2 = (-B + np.sqrt(det))/(2*A)
    t1 = (-B - np.sqrt(det))/(2*A)
    tZ = (pr_ax[2] - pr_src[2])/vr[2]
    
    ## Calculate ray path distances ##
    enter_below_tZ = ((tZ - t1) < 0)
    leave_above_tZ = ((tZ - t2) > 0)
    no_intersect = (det == 0)
    wr = t2 - t1
    hr = t2 - tZ
    hr[enter_below_tZ] = wr[enter_below_tZ]
    hr[leave_above_tZ] = 0.0
    hr[no_intersect] = 0.0
    
    if geom['core_type'] == 'WR':
        return wr
    else:
        return hr
