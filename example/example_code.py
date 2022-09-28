
import pebm
from pebm import Preprocessing as Pre
from pebm.ebm import FiducialPoints as Fp
from pebm.ebm import Biomarkers as Obm
import matplotlib.pyplot as plt
import scipy.io as spio
from scipy.fft import fft, ifft, fftshift
import numpy as np

plot = False


# ecg = open("Dog_example_ecg.txt", "r")
# signal1= ecg.read()
# signal_dog = signal1.split('\n')
# signal = np.asarray([float(x) for x in signal_dog])
# freq = 500
raw_ecg = np.load('/MLAIM/AIMLab/Sheina/databases/VTdb/preprocessed_data/uvafdb/0275/ecg_0.npy')
signal = raw_ecg[41*200*30*60:42*200*30*60]
freq = 200
# ecg_mat = spio.loadmat('human_200Hz_gr.mat')
# signal = np.asarray(ecg_mat['ecg']).squeeze()
# peaks1 = np.asarray(ecg_mat['peaks']).squeeze()
# freq = ecg_mat['fs'][0,0]
# #tt =fecgyn_tgen(signal, peaks, freq)
#
# signal= signal[:-1]

# signal = np.load('ECGs_eran.npy')
# freq = 400
# fiducials = np.load('fiducials_eran.npy', allow_pickle=True).item()
# build a dictinary
# try Extract_mor_features
# pre = Pre.Preprocessing(signal, freq)
#
# f_notch = 60
# fsig =pre.notch(f_notch)
# fsig= pre.bpfilt()
#
#
matlab_pat= '/usr/local/MATLAB/R2021a' #for orian
#
fp = Fp.FiducialPoints(signal, freq)
peaks = fp.epltd
fiducials = fp.wavedet(matlab_pat, peaks)

obm = Obm.Biomarkers(signal, freq, fiducials=fiducials)
ints, stat_i = obm.intervals()
waves, stat_w = obm.waves()
score = obm.isECG()

a= 5


#-------------------------------------
#figures:
if plot:
    cut = 2000
    start = freq*30
    t_axis = np.linspace((1/freq),cut*(1/freq), cut)
    signal_c = signal[start:cut+start]
    fsig_c = fsig[start:cut+start]


    #time domain filter:
    fig = plt.figure()
    plt.style.use('bmh')
    x1, = plt.plot(t_axis, signal_c, 'k')
    x2, = plt.plot(t_axis, fsig_c, 'r',linewidth=1)
    plt.xlabel('time[sec]')
    plt.ylabel('mV')
    plt. show()

    f_axis = np.linspace(-(freq/2), freq/2, cut)
    #freq domain filter

    fft_signal_c =np.abs(fftshift(fft(signal_c)))
    fft_fsig_c = np.abs(fftshift(fft(fsig_c)))

    fig = plt.figure()
    plt.style.use('bmh')
    x1, = plt.plot(f_axis,fft_signal_c , 'k')
    x2, = plt.plot(f_axis,fft_fsig_c , 'r' ,linewidth=1)
    plt.xlabel('f[Hz]')
    plt.ylabel('Amp')

    plt. show()

    #freq domain notch filter
    f_l = int((cut/2)+np.round(((f_notch-5)*cut/freq)))
    f_h = int((cut/2)+np.round(((f_notch+5)*cut/freq)))

    fig = plt.figure()
    plt.style.use('bmh')
    x1, = plt.plot(f_axis[f_l:f_h], fft_signal_c[f_l:f_h] , 'k')
    x2, = plt.plot(f_axis[f_l:f_h], fft_fsig_c[f_l:f_h] , 'r', linewidth=1)
    plt.xlabel('f[Hz]')
    plt.ylabel('Amp')
    plt. show()

    #plot R-peaks
    relevant_R = peaks[peaks > start]
    relevant_R = relevant_R[relevant_R < start+cut]
    relevant_R = relevant_R - start

    fig = plt.figure()
    plt.style.use('bmh')
    x1, = plt.plot(t_axis, fsig_c, 'k')
    x2 = plt.scatter(t_axis[relevant_R],fsig_c[relevant_R] , c ='r', marker = "o")
    plt.xlabel('time[sec]')
    plt.ylabel('mV')
    plt. show()






a = 5