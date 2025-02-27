
import numpy as np
from pyspedas import time_double
from pytplot import get_data, store_data, options
from geopack import geopack, t89

def tt89(pos_var_gsm, iopt=3, suffix='', igrf_only=False):
    """
    tplot wrapper for the functional interface to Sheng Tian's implementation 
    of the Tsyganenko 96 and IGRF model:

    https://github.com/tsssss/geopack

    Input
    ------
        pos_gsm_tvar: str
            tplot variable containing the position data (km) in GSM coordinates

    Parameters
    -----------
        iopt: int
            Specifies the ground disturbance level:
                iopt= 1       2        3        4        5        6      7
                           correspond to:
                kp=  0,0+  1-,1,1+  2-,2,2+  3-,3,3+  4-,4,4+  5-,5,5+  &gt =6-

        suffix: str
            Suffix to append to the tplot output variable

    Returns
    --------
        Name of the tplot variable containing the model data
    """
    pos_data = get_data(pos_var_gsm)

    if pos_data is None:
        print('Variable not found: ' + pos_var_gsm)
        return

    b0gsm = np.zeros((len(pos_data.times), 3))
    dbgsm = np.zeros((len(pos_data.times), 3))

    # convert to Re
    pos_re = pos_data.y/6371.2

    for idx, time in enumerate(pos_data.times):
        tilt = geopack.recalc(time)

        # dipole B in GSM
        b0gsm[idx, 0], b0gsm[idx, 1], b0gsm[idx, 2] = geopack.dip(pos_re[idx, 0], pos_re[idx, 1], pos_re[idx, 2])

        # T89 dB in GSM
        dbgsm[idx, 0], dbgsm[idx, 1], dbgsm[idx, 2] = t89.t89(iopt, tilt, pos_re[idx, 0], pos_re[idx, 1], pos_re[idx, 2])

    if igrf_only:
        bgsm = b0gsm
    else:
        bgsm = b0gsm + dbgsm

    saved = store_data(pos_var_gsm + '_bt89' + suffix, data={'x': pos_data.times, 'y': bgsm})

    if saved:
        return pos_var_gsm + '_bt89' + suffix