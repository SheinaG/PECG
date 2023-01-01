import tempfile
import platform
import os, sys, stat
import numpy as np
import scipy.io as spio
import pathlib


def wavdet(signal, fs, peaks, matlab_pat):
    my_path = str(pathlib.Path(__file__).parent.resolve())
    tmpdirname = tempfile.TemporaryDirectory()
    os.chdir(tmpdirname.name)

    np.savetxt("peaks.txt", peaks)
    np.savetxt("signal.txt", signal)
    if platform.system() == "Linux":
        wavedet_dir = my_path + "/run_run_wavedet.sh"
        for root, dirs, files in os.walk(my_path):
            for d in dirs:
                os.chmod(os.path.join(root, d), 0o777)
            for f in files:
                os.chmod(os.path.join(root, f), 0o777)

        command = " ".join(
            [wavedet_dir, matlab_pat, '"signal.txt" "peaks.txt"', str(fs)]
        )
        os.system(command)
        fiducials_mat = spio.loadmat(tmpdirname.name + "/output.mat")
    if platform.system() == "Windows":
        wavedet_dir = my_path + "//run_wavdet_W.exe"
        command = " ".join([wavedet_dir, '"signal.txt" "peaks.txt" ', str(fs)])
        os.system(command)
        fiducials_mat = spio.loadmat(tmpdirname.name + "//output.mat")

    return fiducials_mat, tmpdirname
