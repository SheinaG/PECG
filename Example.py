import numpy as np
import sys
sys.path.append("C:\Sheina\PECG")

#ecg = open("C:\Sheina\PECG\pecg\ecg\wavedet_exe\Dog_example_ecg1.txt", "r")
ecg = open("/home/sheina/PECG/pecg/ecg/wavedet_exe/Dog_example_ecg1.txt")
signal1 = ecg.read()
signal_dog = signal1.split('\n')
signal = np.asarray([float(x) for x in signal_dog[:-1]])
freq = 500

from pecg import Preprocessing as Pre
pre = Pre.Preprocessing(signal, fs=500)
pre_notch = pre.notch(50)
pre_filt = pre.bpfilt()
bsqi = pre.bsqi()

from pecg.ecg import FiducialPoints as Fp
fp = Fp.FiducialPoints(signal, fs=500)
#matlab_pat = 'C:\Apps\MATLAB_Runtime_R2022a_Update_5_win64'
matlab_pat = '/usr/local/MATLAB/R2021a'
peaks = fp.jqrs()
fiducials = fp.wavedet(matlab_pat, peaks)

from pecg.ecg import Biomarkers as Obm

obm = Obm.Biomarkers(signal, fs=500, fiducials=fiducials)
ints, stat_i = obm.intervals()
waves, stat_w = obm.waves()

a=5