from pebm import Preprocessing as Pre
from pebm.ebm import FiducialPoints as Fp
from pebm.ebm import Biomarkers as Obm
import scipy.io as spio
from scipy.fft import fft, ifft, fftshift
import numpy as np


ecg_mat = spio.loadmat('/home/sheina/pebm/example/TNMG_example0.mat')
# fid_mat = spio.loadmat('/home/sheina/pebm/example/output.mat')
freq = 400

signal = ecg_mat['signal']
[ecg_len, ecg_num] = np.shape(signal)

pre = Pre.Preprocessing(signal,freq)
f_notch = 60
fsig =pre.notch(f_notch)
fsig= pre.bpfilt()

matlab_pat='/usr/local/MATLAB/R2021a'
fp = Fp.FiducialPoints(signal, np.uint8(freq))
peaks = fp.epltd
peaks = fp.xqrs()
fiducials = fp.wavedet(matlab_pat)

#qrs = fp.xqrs()


# fiducials = {}
# keys = ["Pon", "P", "Poff", "QRSon", "Q", "qrs", "S", "QRSoff", "Ton", "T", "Toff", "Ttipo", "Ttipoon",
#         "Ttipooff"]
# for i in np.arange(0,ecg_num):
#     position = fid_mat['output'][0, i]
#     all_keys = fid_mat['output'][0][i].dtype.names
#     position_values = []
#     position_keys = []
#     for j, key in enumerate(all_keys):
#         ret_val = position[j].squeeze()
#         if (keys.__contains__(key)):
#             ret_val[np.isnan(ret_val)] = -1
#             ret_val = np.asarray(ret_val, dtype=np.int64)
#             position_values.append(ret_val.astype(int))
#             position_keys.append(key)
# # -----------------------------------
#
#     fiducials[i] = dict(zip(position_keys, position_values))

obm = Obm.Biomarkers(signal, freq, fiducials=fiducials)
ints, stat_i = obm.intervals()
waves, stat_w = obm.waves()

a =5