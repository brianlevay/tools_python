# Core Axis Determination

import numpy as np


def _linear_regression(x_data, y_data, x_pred):
    x_m = np.mean(x_data)
    y_m = np.mean(y_data)
    del_x = x_data - x_m
    del_y = y_data - y_m
    beta = np.sum(del_x * del_y) / np.sum(del_x * del_x)
    alpha = y_m - beta * x_m
    return (beta * x_pred) + alpha


def _calculate_edges(I_raw, geom):
    I_bin = np.zeros(shape=I_raw.shape)
    I_bin[I_raw < 0.8*np.amax(I_raw)] = 1.0
    I_left = np.zeros(shape=(geom['nrows'], geom['ncols']+1))
    I_right = np.zeros(shape=(geom['nrows'], geom['ncols']+1))
    I_diff = np.zeros(shape=(geom['nrows'], geom['ncols']+1))
    I_left[:,:-1] = I_bin
    I_right[:,1:] = I_bin
    I_diff = I_right - I_left
    return I_diff


def _get_center_pts(I_diff, px_diam, min_width=0.5):
    rows = []
    middles = []
    for i, row in enumerate(I_diff):
        max_gap = 0
        start = 0
        end = 0
        for j, col in enumerate(row):
            if col == -1:
                start = j
            if col == 1:
                end = j
                if (end - start) > max_gap:
                    max_gap = (end - start)
                    left = start
                    right = end
        if max_gap > min_width*px_diam:
            rows.append(i)
            middles.append((right - left)/2 + left)
    return (rows, middles)


def default_axis(I_raw, geom):
    x_ax = geom['px_size'] * (geom['ncols']/2) + (geom['px_size']/2.0)
    y_ax = geom['px_size'] * (geom['nrows']/2) + (geom['px_size']/2.0)
    theta = 0.0
    return (x_ax, y_ax), theta


def estimate_axis(I_raw, geom):
    I_diff = _calculate_edges(I_raw, geom)
    px_diam = (2*geom['radius'])/geom['px_size']
    rows, middles = _get_center_pts(I_diff, px_diam, min_width=0.5)
    
    rows_all = np.arange(0, geom['nrows'], 1)
    col_pred = _linear_regression(rows, middles, rows_all)
    x_ax = geom['px_size'] * col_pred[0] + (geom['px_size']/2.0)
    y_ax = geom['px_size'] * rows_all[0] + (geom['px_size']/2.0)
    xy_ax = (x_ax, y_ax)
    theta = np.degrees(np.arctan(col_pred[1]-col_pred[0]))
    
    if (len(middles) < 10) or (abs(theta) > 5.0):
        return default_axis(I_raw, geom)
    else:
        return (x_ax, y_ax), theta

