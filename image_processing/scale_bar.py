# Scale Bar

import numpy as np


def _px_det(x_core, geom):
    x_det = (x_core / (geom['src_ht'] - geom['core_ht'] - geom['radius'])) * geom['src_ht']
    px_det = int(x_det / geom['px_size'])
    return px_det


def create_scale_bar(geom, border=2):
    I_scale = np.full(shape=(geom['nrows'], geom['ncols']), fill_value=0.5)
    cm_length = _px_det(1.0, geom)
    cm_width = _px_det(0.2, geom)
    ir_start = border
    ir_end = geom['nrows']-1
    jr_start = border
    jr_end = border + cm_width
    I_scale[ir_start:ir_end, 0:jr_end+border] = 0.0
    I_scale[ir_start:ir_end, jr_start:jr_end] = 1.0
    n_cms = round((geom['nrows'] - 2*border)/cm_length)
    for cm in range(0, n_cms+1, 1):
        if (cm%2) == 0:
            ir_cm_start = ir_start + cm*cm_length
            ir_cm_end = ir_start + (cm+1)*cm_length
            if ir_cm_end > geom['nrows']:
                ir_cm_end = geom['nrows']-1
            I_scale[ir_cm_start:ir_cm_end, jr_start:jr_end] = 0.0
            
    ln_length = _px_det(geom['roi'], geom)
    ln_width = _px_det(0.1, geom)
    il_start = int((geom['nrows'] - ln_length) / 2)
    il_end = il_start + ln_length
    jl_start = jr_end + 3*border
    jl_end = jl_start + ln_width
    I_scale[il_start:il_end, jl_start:jl_end] = 0.0
    return I_scale


def add_scale_bar(I_proc, I_scale):
    I_max = np.amax(I_proc)
    I_out = np.where(I_scale == 0.0, 0.0, I_proc)
    I_out = np.where(I_scale == 1.0, I_max, I_out)
    return I_out