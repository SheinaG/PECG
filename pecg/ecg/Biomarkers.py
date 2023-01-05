import numpy as np
from pecg.ecg.FiducialPoints import FiducialPoints
from pecg.ecg.IntervalsDuration import extract_intervals_duration
from pecg.ecg.WavesCharacteristics import extract_waves_characteristics
from pecg.ecg.Statistics import statistics
from pecg._ErrorHandler import _check_shape_, WrongParameter


class Biomarkers:
    def __init__(self, signal: np.array, fs: int, fiducials: dict):
        """
        The purpose of the Biomarkers class is to calculate the biomarkers, we divided the morphological biomarkers into two main groups: intervals and waves.
        :param signal: The ECG signal as a ndarray.
        :param fs: The sampling frequency of the signal [Hz].
        :param fiducials: Nested dictionary of leads - For every lead there is a dictionary that includes indexes for for each one of nine fiducials points. this nested dictionary can be calculated using the FiducialPoints module.


        .. code-block:: python

            from pecg.ecg import Biomarkers as Obm
            obm = Obm.Biomarkers(f_ecg_rec, fs, fiducials)
            ints, stat_i = obm.intervals()
            waves, stat_w = obm.waves()

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


    def intervals(self):
        """
        :return:
            * intervals_b: Dictionary that includes all the row data, for the **Interval duration and segments** biomarkers.
            * intervals_statistics: Dictionary that includes the mean, median, min, max, iqr and std, for every **Interval duration and segments** biomarker.


        .. list-table:: **Interval duration and segments**:
            :widths: 25 75
            :header-rows: 1

            * - Biomarker
              - Description
            * - P-waveint
              - Time interval between P-on and P-off.
            * - PRint
              - Time interval between the P-on to the QRS-on.
            * - PRseg
              - Time interval between the P-off to the QRS-on.
            * - PRint2
              - Time interval between P-peak and R-peak as defined by Mao et al.
            * - QRSint
              - Time interval between the QRS-on to the QRS-off.
            * - QTint
              - Time interval between the QRS-on to the T-off.
            * - QTcBint
              - Corrected QT interval (QTc) using Bazett’s formula.
            * - QTcFriint
              - QTc using the Fridericia formula.
            * - QTcFraint
              - QTc using the Framingham formula.
            * - QTcHint
              - QTc using the Hodges formula.
            * - T-waveint
              - Time interval between T-on and T-off.
            * - TPseg
              - Time interval between T-off and P-on.
            * - RRint
              - Time interval between sequential R-peaks.
            * - Rdep
              - Time interval betweem Q-on and R-peak.


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
        :return:
            * waves_b: Dictionary that includes all the row data, for every **Waves characteristic** biomarker.
            * waves_statistics: Dictionary that includes the mean, median, min, max, iqr and std, for every **Waves characteristic** biomarker.


        .. list-table:: **Waves characteristics**:
            :widths: 25 75
            :header-rows: 1

            * - Biomarker
              - Description
            * - P-wave
              - Amplitude difference between P-peak and P-off.
            * - T-wave
              - Amplitude difference between T-peak on and T-off.
            * - R-wave:
              - R-peak amplitude.
            * - P-waveArea
              - P-wave interval area defined as integral from the P-on to the P-off.
            * - T-waveArea
              - T-wave interval area  defined as integral from the T-on to the T-off.
            * - QRSArea
              - QRS interval area defined as integral from the QRS-on to the QRS-off.
            * - STseg
              - Amplitude difference between QRS-off and T-on.
            * - J-point
              - Amplitude in 40ms after QRS-off as defined by Hollander et al.


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
