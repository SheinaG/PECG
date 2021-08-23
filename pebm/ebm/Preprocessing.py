
import numpy as np
import mne
from scipy.signal import butter, sosfiltfilt
from scipy.spatial import cKDTree
from src.pebm.FiducialPoints import FiducialPoints
from src._ErrorHandler import _check_shape_, WrongParameter


class Preprocessing:


    def __init__(self, signal, fs):
        """
        The Preprocessing class provides some routines for pre-filtering
        the ECG signal as well as estimating the signal quality.

        :param signal: the ECG signal as a ndarray.
        :param fs: The sampling frequency of the signal.
        """
        if fs <= 0:
            raise WrongParameter("Sampling frequency should be strictly positive")
        _check_shape_(signal)

        self.signal = signal
        self.fs = fs
        self.n_freq = None #can be 60 or 50 HZ



    def notch(self, n_freq):

        """
        The notch function applies a notch filter in order to remove the power line artifacts.

        :param n_freq: The expected center frequency of the power line interference.
        Typically 50Hz (e.g. Europe) or 60Hz (e.g. US)

        :return:  the filtered ECG signal
        """
        if n_freq <= 0:
            raise WrongParameter("center frequency of the power line should be strictly positive")
        signal = self.signal
        fs = self.fs
        self.n_freq = n_freq
        # notch_freq have to be 50 or 60 HZ (make that condition)
        fsig = mne.filter.notch_filter(signal.astype(np.float), fs, freqs=n_freq)

        #plot:

        self.signal =fsig
        return fsig


    def bpfilt(self):
        """
        The bpfilt function applies a bandpass filter between [0.67, 100] Hz,
        this function uses a zero-phase Butterworth filter with 75 coefficients.

        :return: the filtered ECG signal
        """
        signal = self.signal
        fs = self.fs
        filter_order = 75 #??
        low_cut = 0.67
        high_cut = 100

        nyquist_freq = 0.5 * fs
        low = low_cut / nyquist_freq
        high = high_cut / nyquist_freq
        if fs <= high_cut*2:
            sos = butter(filter_order, low, btype="high", output='sos', analog=False)
        else:
            sos = butter(filter_order, [low, high], btype="band", output='sos', analog=False)
        fsig = sosfiltfilt(sos, signal)
        self.signal = fsig
        return fsig



    def bsqi(self, peaks = None):

        """
        This function is based on the following paper:
            Li, Qiao, Roger G. Mark, and Gari D. Clifford.
            "Robust heart rate estimation from multiple asynchronous noisy sources
            using signal quality indices and a Kalman filter."
            Physiological measurement 29.1 (2007): 15.

        The implementation itself is based on:
            Behar, J., Oster, J., Li, Q., & Clifford, G. D. (2013).
            ECG signal quality during arrhythmia and its application to false alarm reduction.
            IEEE transactions on biomedical engineering, 60(6), 1660-1666.

        :param peaks:  Annotation of the reference peak detector (Indices of the peaks). If peaks are not given,
         the peaks are calculated with epltd detector, the test peaks are calculated with xqrs detector.
        :returns F1:    The 'bsqi' score, between 0 and 1.
        """

        fs = self.fs
        agw = 0.05 #in seconds
        if peaks is None:
            refqrs = FiducialPoints.epltd()
        else:
            refqrs = peaks
        testqrs = FiducialPoints.xqrs()
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
        return F1