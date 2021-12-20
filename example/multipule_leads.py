from pebm import Preprocessing as Pre
from pebm.ebm import FiducialPoints as Fp
from pebm.ebm import Biomarkers as Obm
import matplotlib.pyplot as plt
import scipy.io as spio
from scipy.fft import fft, ifft, fftshift
import numpy as np

#ecg_mat = spio.loadmat('/home/sheina/pebm/example/TNMG_example0.mat')
ecg_mat = spio.loadmat('C:\Sheina\pebm\example\\run10.mat')
freq = 400;
signal = ecg_mat['raw_ecg']
peaks = ecg_mat['peaks']
# [ecg_len, ecg_num] = np.shape(signal)
#
#
# pre = Pre.Preprocessing(signal,freq)
# f_notch = 60
# fsig =pre.notch(f_notch)
# fsig= pre.bpfilt()

# matlab_pat='/usr/local/MATLAB/MATLAB_Runtime'
# fp = Fp.FiducialPoints(signal, np.uint8(freq))
# fiducials = fp.wavedet(matlab_pat)
# peaks = fp.epltd()
# #qrs = fp.xqrs()
# a = 5

# size_peaks = np.zeros([1, ecg_num]).squeeze()
# for i in np.arange(0, ecg_num):
#     sp = len(ecg_mat['peaks_lead_'+str(i)][0])
#     size_peaks[i] = sp
#
# max_sp = int(np.max(size_peaks))
# peaks = np.zeros([max_sp, ecg_num])
#
# for i in np.arange(0, ecg_num):
#     peaks[:int(size_peaks[i]), i] = ecg_mat['peaks_lead_'+str(i)][0]
#
np.savetxt("C:\Sheina\pebm\example\\peaks10.txt", peaks)
np.savetxt("C:\Sheina\pebm\example\\signal10.txt", signal)



