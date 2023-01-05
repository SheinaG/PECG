import mne
import numpy as np
from scipy.signal import butter, sosfiltfilt
from scipy.spatial import cKDTree

from pecg._ErrorHandler import _check_shape_, WrongParameter
from pecg.ecg.FiducialPoints import FiducialPoints


class Preprocessing:

    def __init__(self, signal: np.array, fs: int):
        """
        The Preprocessing class provides some routines for pre-filtering
        the ECG signal as well as estimating the signal quality.
        :param signal: the ECG signal as a ndarray, with shape (L, N) when L is the number of channels or leads and N i the number of samples.
        :param fs: The sampling frequency of the signal [Hz].


        .. code-block:: python

            import pecg
            from pecg import Preprocessing as Pre
            pre = Pre.Preprocessing(signal, fs)

        """
        if fs <= 0:
            raise WrongParameter("Sampling frequency should be strictly positive")
        _check_shape_(signal, fs)

        self.signal = signal
        self.fs = fs
        self.n_freq = None  # can be 60 or 50 HZ

    def notch(self, n_freq: int):

        """
        The notch function applies a notch filter in order to remove the power line artefacts.
        :param n_freq: The expected center frequency of the power line interference. Typically, 50Hz (e.g. Europe) or 60Hz (e.g. US)
        :return: The filtered ECG signal, with shape (L, N) when L is the number of channels or leads and N is the number of samples.


        .. code-block:: python

            filtered_ecg_rec = pre.notch()

        """
        if n_freq <= 0:
            raise WrongParameter("center frequency of the power line should be strictly positive")
        signal = self.signal
        fs = self.fs
        self.n_freq = n_freq
        # notch_freq have to be 50 or 60 HZ (make that condition)
        if len(np.shape(signal)) == 2:
            [ecg_len, ecg_num] = np.shape(signal)
            fsig = np.zeros([ecg_len, ecg_num])
            for i in np.arange(0, ecg_num):
                fsig[:, i] = mne.filter.notch_filter(signal[:, i].astype(np.float), fs, freqs=n_freq, verbose=False)
        elif len(np.shape(signal)) == 1:
            ecg_len = len(signal)
            ecg_num = 1
            fsig = mne.filter.notch_filter(signal.astype(float), fs, freqs=n_freq)

        self.signal = fsig
        return fsig

    def bpfilt(self):
        """
        The bpfilt function applies a bandpass filter between [0.67, 100] Hz,
        this function uses a zero-phase Butterworth filter with 75 coefficients.
        :return: The filtered ECG signal, with shape (L, N) when L is the number of channels or leads and N is the number of samples.


        .. code-block:: python

            filtered_ecg_rec = pre.bpfilt()

        """
        signal = self.signal
        fs = self.fs
        filter_order = 75  # ??
        low_cut = 0.67
        high_cut = 100

        nyquist_freq = 0.5 * fs
        low = low_cut / nyquist_freq
        high = high_cut / nyquist_freq
        if fs <= high_cut * 2:
            sos = butter(filter_order, low, btype="high", output='sos', analog=False)
        else:
            sos = butter(filter_order, [low, high], btype="band", output='sos', analog=False)

        if len(np.shape(signal)) == 2:
            [ecg_len, ecg_num] = np.shape(signal)
            fsig = np.zeros([ecg_len, ecg_num])
            for i in np.arange(0, ecg_num):
                fsig[:, i] = sosfiltfilt(sos, signal[:, i])
        elif len(np.shape(signal)) == 1:
            ecg_len = len(signal)
            ecg_num = 1
            fsig = sosfiltfilt(sos, signal)

        self.signal = fsig
        return fsig

    def bsqi(self, peaks: np.array = np.array([]), test_peaks: np.array = np.array([])):
        """
        bSQI is an automated algorithm to detect poor-quality electrocardiograms.
        This function is based on the following paper:[1]_.
        The implementation itself is based on: [2]_.

        .. [1] Li, Qiao, Roger G. Mark, and Gari D. Clifford.
            "Robust heart rate estimation from multiple asynchronous noisy sources
            using signal quality indices and a Kalman filter."
            Physiological measurement 29.1 (2007): 15.

        .. [2] Behar, J., Oster, J., Li, Q., & Clifford, G. D. (2013).
            ECG signal quality during arrhythmia and its application to false alarm reduction.
            IEEE transactions on biomedical engineering, 60(6), 1660-1666.

        :param peaks:  Optional input- Annotation of the reference peak detector (Indices of the peaks), as an ndarray of shape (L,N), when L is the number of channels or leads and N is the number of peaks. If peaks are not given, the peaks are calculated with jqrs detector.
        :param test_peaks: Optional input - Annotation of the anther reference peak detector (Indices of the peaks), as an ndarray of shape (L,N), when N is the number of peaks. If test peaks are not given, the test peaks are calculated with xqrs detector.
        :return: The 'bsqi' score, a flout between 0 and 1.


        .. code-block:: python

            bsqi_score = pre.bsqi()
            if bsqi_score < 0.8:
                print('It's a bad quality ECG recording!')

        """

        fs = self.fs
        signal = self.signal

        if len(np.shape(signal)) == 2:
            [ecg_len, ecg_num] = np.shape(signal)
            bsqi = np.zeros([1, ecg_num]).squeeze()
            for i in np.arange(0, ecg_num):
                fp = FiducialPoints(signal[:, i], fs)
                if not peaks.any():
                    refqrs = fp.jqrs()
                else:
                    refqrs = peaks

                if not test_peaks.any():
                    testqrs = fp.xqrs()
                else:
                    testqrs = test_peaks

                bsqi[i] = self.__calculate_bsqi(refqrs[refqrs[:, i] > 0, i], testqrs[testqrs[:, i] > 0, i], fs)
        elif len(np.shape(signal)) == 1:
            fp = FiducialPoints(signal, fs)
            if not peaks.any():
                refqrs = fp.jqrs()
            else:
                refqrs = peaks
            if not test_peaks.any():
                testqrs = fp.xqrs()
            else:
                testqrs = test_peaks
            bsqi = self.__calculate_bsqi(refqrs, testqrs, fs)

        return bsqi

    @staticmethod
    def __calculate_bsqi(refqrs, testqrs, fs):
        agw = 0.05
        agw *= fs
        if len(refqrs) > 0 and len(testqrs) > 0:
            NB_REF = len(refqrs)
            NB_TEST = len(testqrs)

            tree = cKDTree(refqrs.reshape(-1, 1))
            Dist, IndMatch = tree.query(testqrs.reshape(-1, 1))
            IndMatchInWindow = IndMatch[Dist < agw]
            NB_MATCH_UNIQUE = len(np.unique(IndMatchInWindow))
            TP = NB_MATCH_UNIQUE
            FN = NB_REF - TP
            FP = NB_TEST - TP
            Se = TP / (TP + FN)
            PPV = TP / (FP + TP)
            if (Se + PPV) > 0:
                F1 = 2 * Se * PPV / (Se + PPV)
                _, ind_plop = np.unique(IndMatchInWindow, return_index=True)
                Dist_thres = np.where(Dist < agw)[0]
                meanDist = np.mean(Dist[Dist_thres[ind_plop]]) / fs
            else:
                return 0

        else:
            F1 = 0
            IndMatch = []
            meanDist = fs
        bsqi = F1
        return bsqi