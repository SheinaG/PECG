import math
import numpy as np
import os
import scipy.signal as sc_signal
import tempfile
import wfdb
from wfdb import processing
import multiprocessing

from pecg._ErrorHandler import _check_shape_, WrongParameter
from pecg.ecg.c_files.EpltdAll import epltd_all
from pecg.ecg.wavedet_exe.Wavdet import wavdet


class FiducialPoints:

    def __init__(self, signal: np.array, fs: int):
        """
        The purpose of the FiducialPoints class is to calculate the fiducial points.

        :param signal: the ECG signal as a ndarray, with shape (L, N) when L is the number of channels or leads and N is the number of samples.
        :param fs: The sampling frequency of the signal.[Hz]

        .. code-block:: python

            from pecg.ecg import FiducialPoints as Fp
            fp = Fp.FiducialPoints(f_ecg_rec, fs)

        """
        if fs <= 0:
            raise WrongParameter("Sampling frequency should be strictly positive")
        _check_shape_(signal, fs)

        self.signal = signal
        self.fs = fs
        self.peaks = []


    def wavedet(self, matlab_pat: str, peaks: np.array = np.array([])):
        """
        The wavedat function uses the matlab algorithm wavedet, compiled for python.
        The algorithm is described in the following paper: [1]_. The function is calculating
        the fiducial points of the ECG recording using wavelet transform.

        .. [1] Martinze at el (2004),
            A wavelet-based ECG delineator: evaluation on standard databases.
            IEEE Transactions on Biomedical Engineering, 51(4), 570-581.

        :param matlab_pat: path to matlab runtime 2021a directory
        :param peaks: Optional input- Annotation of the reference peak detector (Indices of the peaks), as an ndarray of shape (L,N), when L is the number of channels or leads and N is the number of peaks. If peaks are not given, the peaks are calculated with the jqrs detector.
        :return: fiducials: Nested dictionary of leads - For every lead there is a dictionary that includes indexes for for each one of nine fiducials points.


        .. code-block:: python

            matlab_pat = '/usr/local/MATLAB/R2021a'
            peaks = fp.jqrs()
            fiducials = fp.wavedet(matlab_pat, peaks)


        """

        signal = self.signal
        fs = self.fs

        try:
            cwd = os.getcwd()
            fl = 1
        except:
            print('Not exists current path')
            fl = 0

        if len(np.shape(signal)) == 2:
            [ecg_len, ecg_num] = np.shape(signal)
        elif len(np.shape(signal)) == 1:
            ecg_num = 1
        if peaks.size == 0:
            peaks = self.epltd

        self.peaks = peaks

        fiducials_mat, tempdirname = wavdet(signal, fs, peaks, matlab_pat)
        keys = ["Pon", "P", "Poff", "QRSon", "qrs", "QRSoff", "Ton", "T", "Toff"]
        position = fiducials_mat['output']
        all_keys = fiducials_mat['output'].dtype.names
        fiducials = {}

        num_ecg = np.size(position)
        for j in np.arange(num_ecg):
            position_values = []
            position_keys = []
            for i, key in enumerate(all_keys):
                ret_val = position[0, j][i].squeeze()
                if (keys.__contains__(key)):
                    if len(ret_val[np.isnan(ret_val)]):
                        ret_val[np.isnan(ret_val)] = np.nan
                    ret_val = np.asarray(ret_val)
                    position_values.append(ret_val)
                    position_keys.append(key)
            # -----------------------------------

            fiducials[j] = dict(zip(position_keys, position_values))
        if fl:
            os.chdir(cwd)
        tempdirname.cleanup()
        return fiducials

    def epltd(self):
        """
        This function calculates the indexes of the R-peaks with epltd peak detector algorithm.
        This algorithm were introduced by [2]_.

        .. [2] Pan, Jiapu, and Willis J. Tompkins. "A real-time QRS detection algorithm."
            IEEE Trans. Biomed. Eng 32.3 (1985): 230-236.

        :return: indexes of the R-peaks in the ECG signal, as an ndarray of shape (L,N), when L is the number of channels or leads and N is the number of peaks.


        .. code-block:: python

            peaks = fp.epltd()

        """
        try:
            cwd = os.getcwd()
            fl = 1
        except:
            fl = 0

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

        if fl:
            os.chdir(cwd)

        return peaks

    def xqrs(self):
        """
        This function wraps the XQRS function of the WFDB package.

        :return: indexes of the R-peaks in the ECG signal, as an ndarray of shape (L,N), when L is the number of channels or leads and N is the number of peaks.


        .. code-block:: python

            peaks = fp.xqrs()

        """
        signal = self.signal
        fs = self.fs

        if len(np.shape(signal)) == 2:
            [ecg_len, ecg_num] = np.shape(signal)
            size_peaks = np.zeros([1, ecg_num]).squeeze()
            peaks_dict = {}
            for i in np.arange(0, ecg_num):
                signali = signal[:, i]
                peaks_dict[str(i)] = self.__calculate_xqrs(signali, fs)
                size_peaks[i] = len(peaks_dict[str(i)])
            max_sp = int(np.max(size_peaks))
            peaks = np.zeros([max_sp, ecg_num])
            for i in np.arange(0, ecg_num):
                peaks[:int(size_peaks[i]), i] = peaks_dict[str(i)]
        elif len(np.shape(signal)) == 1:
            ecg_num = 1
            peaks = self.__calculate_xqrs(signal, fs)
        self.peaks = peaks
        return peaks

    def jqrs(self, thr: float = 0.8, rp: float = .25):
        """
        The function is an Implementation of an energy based qrs detector [3]_. The algorithm is an
        adaptation of the popular Pan & Tompkins algorithm [2]_. The function assumes
        the input ecg is already pre-filtered i.e. bandpass filtered and that the
        power-line interference was removed. Of note, NaN should be represented by the
        value -32768 in the ecg (WFDB standard).

        .. [3] Behar, Joachim, Alistair Johnson, Gari D. Clifford, and Julien Oster.
            "A comparison of single channel fetal ECG extraction methods." Annals of
            biomedical engineering 42, no. 6 (2014): 1340-1353.

        :param thr: threshold, default value is 0.8.
        :param rp: refractory period (sec), default value is 0.25.

        :return: indexes of the R-peaks in the ECG signal, as an ndarray of shape (L,N), when L is the number of channels or leads and N is the number of peaks.


        .. code-block:: python

            peaks = fp.jqrs()

        """
        signal = self.signal
        fs = self.fs
        if len(np.shape(signal)) == 2:
            [ecg_len, ecg_num] = np.shape(signal)
            size_peaks = np.zeros([1, ecg_num]).squeeze()
            peaks_dict = {}
            for i in np.arange(0, ecg_num):
                signali = signal[:, i]
                peaks_dict[str(i)] = self.__calculate_jqrs(signali, fs, thr, rp)
                size_peaks[i] = len(peaks_dict[str(i)])
            max_sp = int(np.max(size_peaks))
            peaks = np.zeros([max_sp, ecg_num])
            for i in np.arange(0, ecg_num):
                peaks[:int(size_peaks[i]), i] = peaks_dict[str(i)]
        elif len(np.shape(signal)) == 1:
            ecg_num = 1
            peaks = self.__calculate_jqrs(signal, fs, thr, rp)
        self.peaks = peaks
        return peaks

    @staticmethod
    def __calculate_xqrs(signal, fs):
        try:
            cwd = os.getcwd()
            fl = 1
        except:
            print('Not exists current path')
            fl = 0
        tmpdirname = tempfile.TemporaryDirectory()
        os.chdir(tmpdirname.name)
        wfdb.wrsamp(record_name='temp', fs=fs, units=['mV'], sig_name=['V5'],
                    p_signal=signal.reshape(-1, 1), fmt=['16'])
        record = wfdb.rdrecord(tmpdirname.name + '/temp')
        ecg = record.p_signal[:, 0]
        xqrs = processing.xqrs_detect(ecg, fs=fs)

        if fl:
            os.chdir(cwd)
        tmpdirname.cleanup()
        return xqrs


    @staticmethod
    def __calculate_jqrs(signal, fs, thr, rp):
        try:
            cwd = os.getcwd()
            fl = 1
        except:
            print('Not exists current path')
            fl = 0
        tmpdirname =  tempfile.TemporaryDirectory()
        os.chdir(str(tmpdirname.name))
        wfdb.wrsamp(record_name='temp', fs=fs, units=['mV'], sig_name=['V5'],
                    p_signal=signal.reshape(-1, 1), fmt=['16'])
        record = wfdb.rdrecord(tmpdirname.name + '/temp')
        ecg = record.p_signal[:, 0]
        INT_NB_COEFF = int(np.round(7 * fs / 256))  # length is 30 for fs=256Hz
        dffecg = np.diff(ecg)  # differenciate (one datapoint shorter)
        sqrecg = np.square(dffecg)  # square ecg
        intecg = sc_signal.lfilter(np.ones(INT_NB_COEFF, dtype=int),
                                   1, sqrecg)  # integrate
        mdfint = intecg
        delay = math.ceil(INT_NB_COEFF / 2)
        mdfint = np.roll(mdfint, -delay)  # remove filter delay for scanning back through ecg
        # thresholding
        mdfint_temp = mdfint
        mdfint_temp_ = np.delete(mdfint_temp, np.where(ecg == -32768))  # exclude the NaN (encoded in WFDB format)
        xs = np.sort(mdfint_temp)
        ind_xs = int(np.round(98 / 100 * len(xs)))
        en_thres = xs[ind_xs]
        poss_reg = mdfint > thr * en_thres
        tm = np.arange(start=1 / fs, stop=(len(ecg) + 1) / fs, step=1 / fs).reshape(1, -1)
        # search back
        SEARCH_BACK = 1
        if SEARCH_BACK:
            indAboveThreshold = np.where(poss_reg)[0]  # indices of samples above threshold
            RRv = np.diff(tm[0, indAboveThreshold])  # compute RRv
            medRRv = np.median(RRv[RRv > 0.01])
            indMissedBeat = np.where(RRv > 1.5 * medRRv)[0]  # missed a peak?
            # find interval onto which a beat might have been missed
            indStart = indAboveThreshold[indMissedBeat]
            indEnd = indAboveThreshold[indMissedBeat + 1]
            for i in range(0, len(indStart)):
                # look for a peak on this interval by lowering the energy threshold
                poss_reg[indStart[i]: indEnd[i]] = mdfint[indStart[i]: indEnd[i]] > (0.25 * thr * en_thres)
        # find indices into boudaries of each segment
        left = np.where(np.diff(np.pad(1 * poss_reg, (1, 0), 'constant')) == 1)[0]  # remember to zero pad at start
        right = np.where(np.diff(np.pad(1 * poss_reg, (0, 1), 'constant')) == -1)[0]  # remember to zero pad at end
        nb_s = len(left < 30 * fs)
        loc = np.zeros([1, nb_s], dtype=int)
        for j in range(0, nb_s):
            loc[0, j] = np.argmax(np.abs(ecg[left[j]:right[j] + 1]))
            loc[0, j] = int(loc[0, j] + left[j])
        sign = np.median(ecg[loc])
        # loop through all possibilities
        compt = 0
        NB_PEAKS = len(left)
        maxval = np.zeros([NB_PEAKS])
        maxloc = np.zeros([NB_PEAKS], dtype=int)
        for j in range(0, NB_PEAKS):
            if sign > 0:
                # if sign is positive then look for positive peaks
                maxval[compt] = np.max(ecg[left[j]:right[j] + 1])
                maxloc[compt] = np.argmax(ecg[left[j]:right[j] + 1])
            else:
                # if sign is negative then look for negative peaks
                maxval[compt] = np.min(ecg[left[j]:right[j] + 1])
                maxloc[compt] = np.argmin(ecg[left[j]:right[j] + 1])
            maxloc[compt] = maxloc[compt] + left[j]
            # refractory period - has proved to improve results
            if compt > 0:
                if (maxloc[compt] - maxloc[compt - 1] < fs * rp) & (np.abs(maxval[compt]) < np.abs(maxval[compt - 1])):
                    maxval = np.delete(maxval, compt)
                    maxloc = np.delete(maxloc, compt)
                elif (maxloc[compt] - maxloc[compt - 1] < fs * rp) & (
                        np.abs(maxval[compt]) >= np.abs(maxval[compt - 1])):
                    maxval = np.delete(maxval, compt - 1)
                    maxloc = np.delete(maxloc, compt - 1)
                else:
                    compt = compt + 1
            else:
                # if first peak then increment
                compt = compt + 1
        qrs_pos = maxloc  # datapoints QRS positions

        if fl:
            os.chdir(cwd)
        tmpdirname.cleanup()
        return qrs_pos