import numpy as np

ecg = open("./pecg/ecg/wavdet_exe/Dog_example_ecg.txt", "r")
signal1 = ecg.read()
signal_dog = signal1.split('\n')
signal = np.asarray([float(x) for x in signal_dog])
freq = 500