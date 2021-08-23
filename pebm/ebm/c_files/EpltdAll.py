import tempfile
import os
import wfdb
import pathlib
import numpy as np



def epltd_all(signal, fs):
    five_sec = 5 *fs
    pad =signal[0:five_sec]
    signal_pad = np.concatenate((pad, signal))
    my_path = str(pathlib.Path(__file__).parent.resolve())
    with tempfile.TemporaryDirectory() as tmpdirname:
        os.chdir(tmpdirname)
        wfdb.wrsamp(record_name='temp', fs=np.asscalar(fs), units=['mV'], sig_name=['V5'],
                    p_signal=signal_pad.reshape(-1, 1), fmt=['16'])

        prog_dir = my_path + '/epltd_all'
        ecg_dir = tmpdirname
        command = ';'.join(['EPLTD_PROG_DIR=' + prog_dir,
                            'ECG_DIR=' + ecg_dir,
                            'cd $ECG_DIR',
                            'command=\"$EPLTD_PROG_DIR -r ' + str('temp') + '\"',
                            'eval $command'])
        if os.name == 'nt':
            command = 'wsl ' + command
        os.system(command)
        peaks = wfdb.rdann('temp', 'epltd0').sample - five_sec
    return peaks