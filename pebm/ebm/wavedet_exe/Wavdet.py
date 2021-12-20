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
        #ecg_kit = my_path + '/ecg-kit-master'
        np.savetxt("peaks.txt", peaks)
        np.savetxt("signal.txt", signal)
        if platform.system() == 'Linux':
            #set_command = ''.join(['export MATLAB_RUNTIME=', matlab_pat])
            wavedet_dir = my_path + '/run_run_wavedet.sh'
            command = ' '.join([wavedet_dir, matlab_pat, '"signal.txt" "peaks.txt"', str(fs)])
            #all_command = ';'.join([set_command, command])
            os.system(command)
        if platform.system() == 'Windows':
            wavedet_dir = my_path + '/run_wavedet.exe'
            command = ' '.join([wavedet_dir, '"signal.txt" "peaks.txt" ', str(fs)])
            os.system(command)
        fiducials_mat = spio.loadmat(tmpdirname +'\\output.mat')

    return fiducials_mat