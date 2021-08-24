import tempfile
import platform
import os
import numpy as np
import scipy.io as spio
import pathlib

def wavdet(signal, fs, peaks, matlab_pat):
    my_path = str(pathlib.Path(__file__).parent.resolve())
    with tempfile.TemporaryDirectory() as tmpdirname:
        os.chdir(tmpdirname)
        ecg_kit = my_path + '/ecg-kit-master'
        np.savetxt("peaks.txt", peaks)
        np.savetxt("signal.txt", signal)
        if platform.system() == 'Linux':
            set_command = ''.join(['export MATLAB_RUNTIME=', matlab_pat])
            wavedet_dir = my_path + '/run_peak_det.sh'
            command = ' '.join([wavedet_dir, ecg_kit, '"signal.txt" "peaks.txt"', str(fs)])
            all_command = ';'.join([set_command, command])
            os.system(all_command)
        if platform.system() == 'Windows':
            wavedet_dir = '/home/sheina/pebm_toolbox/src/pebm_pkg/wavedet_exe/peak_det.exe'
            command = ' '.join([wavedet_dir, '"signal.txt" "peaks.txt" ', str(fs)])
            os.system(command)
        fiducials_mat = spio.loadmat('output.mat')
    return fiducials_mat