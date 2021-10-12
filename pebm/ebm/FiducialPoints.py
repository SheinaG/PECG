
import numpy as np
import tempfile
import os
import wfdb
from wfdb import processing
from pebm.ebm.c_files.EpltdAll import epltd_all
from pebm.ebm.wavedet_exe.Wavdet import wavdet
from pebm._ErrorHandler import _check_shape_, WrongParameter

class FiducialPoints:

    def __init__(self, signal, fs, peaks= None):
        """
        The purpose of the FiducialPoints class is to calculate the fiducial pointes of the ECG signal.
        :param signal: The ECG signal as a ndarray.
        :param fs: The sampling frequency" of the signal.
        :param peaks: The indexes of the R- points of the ECG signal – optional input
        """
        if fs <= 0:
            raise WrongParameter("Sampling frequency should be strictly positive")
        _check_shape_(signal)

        self.signal = signal
        self.fs = fs
        if peaks is None:
            peaks = self.epltd()
        self.peaks = peaks

    def wavedet(self, matlab_pat = None):
        """
        The wavedat function uses the matlab algorithm wavedet, compiled for python.
        The algorithm is described in the following paper:
        Martinze at el (2004),
        A wavelet-based ECG delineator: evaluation on standard databases.
        IEEE Transactions on Biomedical Engineering, 51(4), 570-581.

        :param matlab_pat: Optional input- requiered when runing on a linux machine.
        
        :returns: Dictionary that includes indexes for each fiducial point
        """

        signal = self.signal
        fs = self.fs
        peaks = self.peaks
        fiducials_mat =wavdet(signal, fs, peaks, matlab_pat)
        keys = ["Pon", "P", "Poff", "QRSon", "Q", "qrs", "S", "QRSoff", "Ton", "T", "Toff", "Ttipo", "Ttipoon",
                "Ttipooff"]
        position = fiducials_mat['output'][0, 0]
        all_keys = fiducials_mat['output'].dtype.names
        position_values = []
        position_keys = []
        for i, key in enumerate(all_keys):
            ret_val = position[i].squeeze()
            if (keys.__contains__(key)):
                ret_val[np.isnan(ret_val)] = -1
                ret_val = np.asarray(ret_val, dtype=np.int64)
                position_values.append(ret_val.astype(int))
                position_keys.append(key)
        # -----------------------------------

        fiducials = dict(zip(position_keys, position_values))

        return fiducials

    def epltd(self):
        """
        This function calculates the indexes of the R-peaks with epltd peak detector algorithm.
        This algorithm were introduced by Pan, Jiapu; Tompkins, Willis J. (March 1985).
        "A Real-Time QRS Detection Algorithm". IEEE Transactions on Biomedical Engineering.
        BME-32 (3): 230–236

        :return: indexes of the R-peaks in the ECG signal.
        """
        cwd = os.getcwd()
        peaks =epltd_all(self.signal, self.fs)
        os.chdir(cwd)
        return peaks

    def xqrs(self):
        cwd = os.getcwd()

        with tempfile.TemporaryDirectory() as tmpdirname:
            os.chdir(tmpdirname)
            wfdb.wrsamp(record_name= 'temp', fs=np.asscalar(self.fs), units=['mV'], sig_name=['V5'], p_signal=self.signal.reshape(-1, 1), fmt = ['16'] )
            record = wfdb.rdrecord(tmpdirname+'/temp')
            fs = self.fs
            ecg = record.p_signal[:, 0]
            xqrs = processing.XQRS(ecg, fs)

            xqrs.detect()
            peaks = xqrs.qrs_inds
        os.chdir(cwd)
        return peaks


