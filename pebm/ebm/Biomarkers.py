import numpy as np
from pebm.ebm.FiducialPoints import FiducialPoints
from pebm.ebm.IntervalsDuration import extract_intervals_duration
from pebm.ebm.WavesCharacteristics import extract_waves_characteristics
from pebm.ebm.Statistics import statistics
from pebm._ErrorHandler import _check_shape_, WrongParameter


class Biomarkers:
    def __init__(self, signal: np.array, fs, fiducials=None, matlab_path: str = None):
        """

        :param signal: The ECG signal as a ndarray.
        :param fs: The sampling frequency of the signal.
        :param fiducials: Dictionary that includes indexes for each fiducial point
        :param matlab_path: The indexes of the R- points of the ECG signal – optional input
        """
        if fs <= 0:
            raise WrongParameter("Sampling frequency should be strictly positive")
        _check_shape_(signal, fs)

        self.signal = signal
        self.fs = fs
        self.fiducials = fiducials
        self.intervals_b = {}
        self.waves_b = {}
        self.intervals_statistics = {}
        self.waves_statistics = {}

        if fiducials is None:
            fp = FiducialPoints(signal, fs)
            fiducials = fp.wavedet(matlab_path)
        self.fiducials = fiducials

    def intervals(self):
        """

        :returns:
            *intervals_b: Dictionary that includes all the row data, for the intervals and segments biomarkers.
            *intervals_statistics: Dictionary that includes the mean, median, min, max, iqr and std,
         for every ‘interval’ biomarker.

        Interval duration and segments:

        P-waveint:	Time interval between P-on and P-off.

        PRint:	Time interval between the P-on to the QRS-on.

        PRseg:	Time interval between the P-off to the QRS-on.

        PRint2:	Time interval between P-peak and R-peak as defined by Mao et al.

        QRSint:	Time interval between the QRS-on to the QRS-off.

        QTint:	Time interval between the QRS-on to the T-off.

        QTcBint:	Corrected QT interval (QTc) using Bazett’s formula.

        QTcFriint:	QTc using the Fridericia formula.

        QTcFraint:	QTc using the Framingham formula.

        QTcHint:	QTc using the Hodges formula.

        T-waveint:	Time interval between T-on and T-off.

        TPseg:	Time interval between T-off and P-on.

        RRint:	Time interval between sequential R-peaks.

        Rdep: Time interval betweem Q-on and R-peak.
        """
        fs = self.fs
        fiducials = self.fiducials
        signal = self.signal

        if len(np.shape(signal)) == 2:
            [ecg_len, ecg_num] = np.shape(signal)
            intervals_b = {}
            intervals_statistics = {}
            for i in np.arange(ecg_num):
                if np.sum(fiducials[i]['qrs']) == 0:
                    intervals_b[i] = np.nan
                    intervals_statistics[i] = np.nan
                else:
                    intervals_b[i] = extract_intervals_duration(fs, fiducials[i])
                    intervals_statistics[i] = statistics(intervals_b[i])
        elif len(np.shape(signal)) == 1:
            if np.sum(fiducials[0]['qrs']) == 0:
                intervals_b = np.nan
                intervals_statistics = np.nan
            else:
                intervals_b = extract_intervals_duration(fs, fiducials[0])
                intervals_statistics = statistics(intervals_b)

        self.intervals_b = intervals_b
        self.intervals_statistics = intervals_statistics
        return self.intervals_b, self.intervals_statistics

    def waves(self):
        """
        :returns:
            *waves_b: Dictionary that includes all the row data, for every ‘wave’ biomarker.
            *waves_statistics: Dictionary that includes the mean, median, min, max, iqr and std, for every ‘wave’ biomarker.

        P-wave:	Amplitude difference between P-peak and P-off.

        T-wave:	Amplitude difference between T-peak on and T-off.

        R-wave:	R-peak amplitude.

        P-waveArea:	P-wave interval area defined as integral from the P-on to the P-off.

        T-waveArea:	T-wave interval area  defined as integral from the T-on to the T-off.

        QRSArea: QRS interval area defined as integral from the QRS-on to the QRS-off.

        STseg:	Amplitude difference between QRS-off and T-on.

        J-point: Amplitude in 40ms after QRS-off as defined by Hollander et al.
        """
        signal = self.signal
        fs = self.fs
        fiducials = self.fiducials

        if len(np.shape(signal)) == 2:
            [ecg_len, ecg_num] = np.shape(signal)
            waves_b = {}
            waves_statistics = {}
            for i in np.arange(ecg_num):
                if np.sum(fiducials[i]['qrs']) == 0:
                    waves_b[i] = np.nan
                    waves_statistics[i] = np.nan
                else:
                    waves_b[i] = extract_waves_characteristics(signal[:,i], fs, fiducials[i])
                    waves_statistics[i] = statistics(waves_b[i])
        elif len(np.shape(signal)) == 1:
            if np.sum(fiducials[0]['qrs']) == 0:
                waves_b = np.nan
                waves_statistics = np.nan
            else:
                waves_b = extract_waves_characteristics(signal,fs, fiducials[0])
                waves_statistics = statistics(waves_b)

        self.waves_b = waves_b
        self.waves_statistics = waves_statistics
        return self.waves_b, self.waves_statistics

    def isECG(self):

        signal = self.signal
        fs = self.fs
        fiducials = self.fiducials
        score = 0
        #naive_score:
        if len(np.shape(signal)) == 2:
            [ecg_len, ecg_num] = np.shape(signal)
            score = {}
            for i in np.arange(ecg_num):
                score[i] = self.calculate_isECG(fiducials[i])
        elif len(np.shape(signal)) == 1:
            score = self.calculate_isECG(fiducials[0])
        return score

    def calculate_isECG(self, fiducials):

        score = 0

        R_num = len(~np.isnan(fiducials['qrs']))
        Pon_num = len(~np.isnan(fiducials['Pon']))
        P_num = len(~np.isnan(fiducials['P']))
        Poff_num = len(~np.isnan(fiducials['Poff']))
        Q_num = len(~np.isnan(fiducials['QRSoff']))
        S_num = len(~np.isnan(fiducials['QRSon']))
        Ton_num = len(~np.isnan(fiducials['Ton']))
        T_num = len(~np.isnan(fiducials['T']))
        Toff_num = len(~np.isnan(fiducials['Toff']))

        score = ~np.isnan(fiducials['P']) & ~np.isnan(fiducials['T']) & ~np.isnan(fiducials['QRSon']) & ~np.isnan(fiducials['QRSoff'])

        return score