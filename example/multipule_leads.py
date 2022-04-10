from pebm import Preprocessing as Pre
from pebm.ebm import FiducialPoints as Fp
from pebm.ebm import Biomarkers as Obm
import matplotlib.pyplot as plt
import scipy.io as spio
from scipy.fft import fft, ifft, fftshift
import numpy as np

# ecg_mat = spio.loadmat('/home/sheina/pebm/example/TNMG_example0.mat')
# #
# freq = 400;
# signal = ecg_mat['signal']
# #
# pre = Pre.Preprocessing(signal, freq)
# bsqi = pre.bsqi()
# f_notch = 60
# fsig =pre.notch(f_notch)
# fsig= pre.bpfilt()

signal = np.load('/home/sheina/pebm/example/ten_ecgs.npy')
freq = 400


matlab_pat= '/usr/local/MATLAB/R2021a'

fp = Fp.FiducialPoints(signal, freq)
peaks = fp.epltd
test_peaks = fp.jqrs()

pre = Pre.Preprocessing(signal, freq)
bsqi = pre.bsqi(peaks, test_peaks)

fiducials = fp.wavedet(matlab_pat)

obm = Obm.Biomarkers(signal, freq, fiducials=fiducials,matlab_path=matlab_pat)
ints, stat_i = obm.intervals()
waves, stat_w = obm.waves()

# signal = np.load('/home/sheina/pebm/example/recording_example.npy')
#
# freq = 2000
#
#
# fp = Fp.FiducialPoints(signal, freq)
# peaks1 = fp.epltd()
# peaks2 = fp.xqrs()

a = 5