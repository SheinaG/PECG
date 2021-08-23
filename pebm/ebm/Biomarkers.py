from src.pebm.FiducialPoints import FiducialPoints
from src.pebm.IntervalsDuration import extract_intervals_duration
from src.pebm.WavesCharacteristics import extract_waves_characteristics
from src.pebm.Statistics import statistics
from src._ErrorHandler import _check_shape_, WrongParameter


class Biomarkers:
    def __init__(self, signal, fs, fiducials=None):
        """

        :param signal: The ECG signal as a ndarray.
        :param fs: The frequency of the signal.
        :param fiducials: Dictionary that includes indexes for each fiducial point
        """
        if fs <= 0:
            raise WrongParameter("Sampling frequency should be strictly positive")
        _check_shape_(signal)

        self.signal = signal
        self.fs = fs
        self.fiducials = fiducials
        self.intervals_b = {}
        self.waves_b = {}
        self.intervals_statistics = {}
        self.waves_statistics = {}

        if fiducials is None:
            fp = FiducialPoints(signal, fs)
            fiducials = fp.wavedet()
        self.fiducials = fiducials

    def intervals(self):
        """

        :returns:
        1. dictionary that includes all the row data, for every ‘interval’ biomarker.
        2. dictionary that includes the mean, median, min, max, iqr and std,
         for every ‘interval’ biomarker.

        Interval duration and segments:

        P-waveint:	Time interval between P on and P off.

        PRint:	Time interval between the P on to the QRS on.

        PRseg:	Time interval between the P off to the QRS on.

        PRint2:	Time interval between P peak and R peak as defined by Mao et al.

        QRSint:	Time interval between the QRS on to the QRS off.

        QTint:	Time interval between the QRS on to the T off.

        QTcBint:	Corrected QT interval (QTc) using Bazett’s formula.

        QTcFriint:	QTc using the Fridericia formula.

        QTcFraint:	QTc using the Framingham formula.

        QTcHint:	QTc using the Hodges formula.

        T-waveint:	Time interval between T on and T off.

        TPseg:	Time interval between T off and P on.

        RRint:	Time interval between sequential R peaks.
        """
        fs = self.fs
        fiducials = self.fiducials
        self.intervals_b = extract_intervals_duration(fs, fiducials)
        self.intervals_statistics = statistics(self.intervals_b)
        return self.intervals_b, self.intervals_statistics

    def waves(self):
        """
        :returns:
        1. Dictionary that includes all the row data, for every ‘wave’ biomarker.
        2. Dictionary that includes the mean, median, min, max, iqr and std, for every ‘wave’ biomarker.

        P-wave:	Amplitude difference between P peak and P off.

        T-wave:	Amplitude difference between T peak on and T off.

        R-wave:	R peak amplitude.

        P-waveArea:	P wave interval area defined as integral from the P on to the P off.

        T-waveArea:	T wave interval area  defined as integral from the T on to the T off.

        QRSArea: QRS interval area defined as integral from the QRS on to the QRS off.

        STseg:	Amplitude difference between QRS off and T on.

        J-point: Amplitude in 40ms after QRS off as defined by Hollander et al.
        """
        signal = self.signal
        fs = self.fs
        fiducials = self.fiducials
        self.waves_b = extract_waves_characteristics(signal, fs, fiducials)
        self.waves_statistics = statistics(self.waves_b)
        return self.waves_b, self.waves_statistics
