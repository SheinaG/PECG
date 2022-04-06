import numpy as np
import tempfile
import os

sampling_freq = 3
signal = np.random.random(100)
qrs = [np.random.randint(100) for x in range(10)]

# Create temp files
signal_temp_file = tempfile.NamedTemporaryFile(mode="w", delete=False)
qrs_temp_file = tempfile.NamedTemporaryFile(mode="w", delete=False)

# Save the numpy arrays to file
np.savetxt(signal_temp_file.name, signal)
np.savetxt(qrs_temp_file.name, qrs)

# Recover signals
recovered_signal = np.loadtxt(signal_temp_file.name)
print("Length of recovered signal from temp", len(recovered_signal))

recovered_qrs = np.loadtxt(qrs_temp_file.name)
print("Length of recovered qrs from temp", len(recovered_qrs))

# Close the temp files
signal_temp_file.close()
qrs_temp_file.close()

# Delete the temp files
os.remove(signal_temp_file.name)
os.remove(qrs_temp_file.name)