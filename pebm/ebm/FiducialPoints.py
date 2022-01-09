
import numpy as np
import tempfile
import os
import wfdb
from wfdb import processing
from pebm.ebm.c_files.EpltdAll import epltd_all
from pebm.ebm.wavedet_exe.Wavdet import wavdet
from pebm._ErrorHandler import _check_shape_, WrongParameter

class FiducialPoints:

    def __init__(self, signal: np.array, fs: int):
        """
        The purpose of the FiducialPoints class is to calculate the fiducial points
        :param signal: The ECG signal as a two-dimensional ndarray, when the first dimension is the len of the ecg, and the second is the number of leads.
        :param fs: The sampling frequency of the signal.
        :param peaks: The indexes of the R- points of the ECG signal – optional input
        """
        if fs <= 0:
            raise WrongParameter("Sampling frequency should be strictly positive")
        _check_shape_(signal, fs)

        self.signal = signal
        self.fs = fs
        self.peaks = []


    def wavedet(self, matlab_pat: str = None, peaks: np.array = np.array([])):
        """
        The wavedat function uses the matlab algorithm wavedet, compiled for python.
        The algorithm is described in the following paper:
        Martinze at el (2004),
        A wavelet-based ECG delineator: evaluation on standard databases.
        IEEE Transactions on Biomedical Engineering, 51(4), 570-581.

        :param peaks: Optional input- Annotation of the reference peak detector (Indices of the peaks). If peaks are not given,
         the peaks are calculated with epltd detector.
        :param matlab_pat: Optional input- required when running on a linux machine.
        
        :returns:
            *fiducials: Dictionary that includes indexes for each fiducial point.
        """

        signal = self.signal
        fs = self.fs

        if len(np.shape(signal)) == 2:
            [ecg_len, ecg_num] = np.shape(signal)
        elif len(np.shape(signal)) == 1:
            ecg_num = 1
        if peaks.size ==0:
            peaks = self.epltd()

        self.peaks = peaks

        fiducials_mat =wavdet(signal, fs, peaks, matlab_pat)
        keys = ["Pon", "P", "Poff", "QRSon", "Q", "qrs", "S", "QRSoff", "Ton", "T", "Toff", "Ttipo", "Ttipoon",
                "Ttipooff"]
        position = fiducials_mat['output']
        all_keys = fiducials_mat['output'].dtype.names
        fiducials = {}

        num_ecg = np.size(position)
        for j in np.arange(num_ecg):
            position_values = []
            position_keys = []
            for i, key in enumerate(all_keys):
                ret_val = position[0,j][i].squeeze()
                if (keys.__contains__(key)):
                    ret_val[np.isnan(ret_val)] = -1
                    ret_val = np.asarray(ret_val, dtype=np.int64)
                    position_values.append(ret_val.astype(int))
                    position_keys.append(key)
            # -----------------------------------

            fiducials[j] = dict(zip(position_keys, position_values))

        return fiducials

    def epltd(self):
        """
        This function calculates the indexes of the R-peaks with epltd peak detector algorithm.
        This algorithm were introduced by Pan, Jiapu; Tompkins, Willis J. (March 1985).
        "A Real-Time QRS Detection Algorithm". IEEE Transactions on Biomedical Engineering.
        BME-32 (3): 230–236

        :return: indexes of the R-peaks in the ECG signal.
        """
        signal = self.signal
        fs = self.fs

        if len(np.shape(signal)) == 2:
            [ecg_len, ecg_num] = np.shape(signal)
            size_peaks = np.zeros([1, ecg_num]).squeeze()
            peaks_dict = {}
            for i in np.arange(0, ecg_num):
                peaks_dict[str(i)] = epltd_all(signal[:, i], fs)
                size_peaks[i] = len(peaks_dict[str(i)])
            max_sp = int(np.max(size_peaks))
            peaks = np.zeros([max_sp, ecg_num])
            for i in np.arange(0, ecg_num):
                peaks[:int(size_peaks[i]), i] = peaks_dict[str(i)]
        elif len(np.shape(signal)) == 1:
            ecg_num = 1
            peaks = epltd_all(signal, fs)



        return peaks

    def xqrs(self):

        signal = self.signal
        fs = self.fs

        if len(np.shape(signal)) == 2:
            [ecg_len, ecg_num] = np.shape(signal)
            size_peaks = np.zeros([1, ecg_num]).squeeze()
            peaks_dict = {}
            for i in np.arange(0, ecg_num):
                signali = signal[:,i]
                peaks_dict[str(i)] = calculate_xqrs(signali, fs)
                size_peaks[i] = len(peaks_dict[str(i)])
            max_sp = int(np.max(size_peaks))
            peaks = np.zeros([max_sp, ecg_num])
            for i in np.arange(0, ecg_num):
                peaks[:int(size_peaks[i]), i] = peaks_dict[str(i)]
        elif len(np.shape(signal)) == 1:
            ecg_num = 1
            peaks = calculate_xqrs(signal, fs)
        self.peaks = peaks
        return peaks

def calculate_xqrs(signal, fs):
    with tempfile.TemporaryDirectory() as tmpdirname:
        os.chdir(tmpdirname)
        wfdb.wrsamp(record_name='temp', fs=np.asscalar(np.uint(fs)), units=['mV'], sig_name=['V5'],
                    p_signal=signal.reshape(-1, 1), fmt=['16'])
        record = wfdb.rdrecord(tmpdirname + '/temp')
        ecg = record.p_signal[:, 0]
        xqrs = processing.xqrs_detect(ecg, fs, verbose = True)
        #xqrs.detect()
    return  xqrs