# X-Ray Image Batch Processing

import os
import numpy as np
from skimage import io

import primary_calcs as primary
import contrast_enhancement as contrast
import scale_bar as scale


#####################################################################################################
## SUPPORT FUNCTIONS ##
#####################################################################################################


def _empty_histogram(bounds):
    bin_step = (bounds[1] - bounds[0]) / 1000
    bin_edges = np.arange(bounds[0], bounds[1] + bin_step, bin_step)
    hist_empty = np.zeros(len(bin_edges)-1)
    return (bin_edges, hist_empty)


def _process_image(I_raw, geom, cfg):
    murhot0 = primary.calculate_murhot0(I_raw, geom, cfg)
    I_proc = contrast.stretch(murhot0, cfg)
    return I_proc


def _save_image(I_out, filename, out_folder):
    name = filename + "_processed.tif"
    out_path = os.path.join(out_folder, name)
    io.imsave(out_path, I_out.astype('uint16'))

    
#####################################################################################################
## MAIN FUNCTIONS ##
#####################################################################################################


def histogram_14b(in_folder):
    I_14b_bounds = (0.0, 16383.0)
    bin_edges, hist_out = _empty_histogram(I_14b_bounds)
    for root, dirs, files in os.walk(in_folder):
        for filename in files:
            filename_pts = filename.split('.')
            if filename_pts[1] == 'tif':
                filepath = os.path.join(root, filename)
                img = io.imread(filepath)
                I_raw = img.astype('float64')
                hist,_ = np.histogram(I_raw, bins=bin_edges)
                hist_out += hist
    return (bin_edges, hist_out)


def batch_14to16bit(in_folder, out_folder, geom, cfg):
    I_16b_bounds = (0.0, 65535.0)
    bin_edges, hist_out = _empty_histogram(I_16b_bounds)
    I_scale = scale.create_scale_bar(geom)
    for root, dirs, files in os.walk(in_folder):
        for filename in files:
            filename_pts = filename.split('.')
            if filename_pts[1] == 'tif':
                filepath = os.path.join(root, filename)
                img = io.imread(filepath)
                I_raw = img.astype('float64')
                I_proc = _process_image(I_raw, geom, cfg)
                hist,_ = np.histogram(I_proc, bins=bin_edges)
                hist_out += hist
                I_out = scale.add_scale_bar(I_proc, I_scale)
                _save_image(I_out, filename_pts[0], out_folder)
    return (bin_edges, hist_out)


