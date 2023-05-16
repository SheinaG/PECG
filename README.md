
# PhysioZoo ECG documentation

Digital electrocardiography biomarkers to assess cardiac conduction.

Based on the paper 
S. Gendelman et al., "PhysioZoo ECG: Digital electrocardiography biomarkers to assess cardiac conduction," 2021 Computing in Cardiology (CinC), 2021, pp. 1-4, doi: 10.23919/CinC53138.2021.9662857.

## Introduction

The electrocardiogram (ECG) is a standard tool used in medical practice for identifying cardiac pathologies. Because the necessary expertise to interpret this tracing is not readily available in all medical institutions or at all in some large areas of developing countries, there is a need to create a data-driven approach that can automatically capture the information contained in this physiological time series. The primary objective of this package is to identify and implement clinically important digital ECG biomarkers for the purpose of creating a reference toolbox and software for ECG morphological analysis.
    
## Description

Few steps are required to extract the morphological ECG biomarkers, those steps are implemented in the PECG toolbox:

1. ECG Signal Preprocessing - Before computing the ECG morphological biomarkers, prefiltering of the raw ECG time series is performed to remove the baseline wander and the high frequency noise. Specifically, the toolbox includes a zero phase second-order infinite impulse response bandpass filter with the passband of 0.67Hz - 100Hz. Also, the toolbox includes an optional Notch filter that can be set to 50 or 60Hz to remove the power-line interference.

2. ECG Fiducial Points Detection - The toolbox includes the epltd R-peaks algorithm, and the well-known wavedet algorithm for ECG fiducial points  detection. 

3. Engineering of ECG Biomarkers - Using the fiducial points ECG biomarkers are engineered for individual ECG cycles. When a biomarker cannot be engineered because some fiducial points could not be detected by wavedet, then the feature was marked as a NaN. For an ECG channel, a total of 14 features are extracted from intervals duration and 8 from waves characteristics to describe the ECG morphology.

4. Summary Statistics - For a specified time window the six summary statistics (mean, median, min, max, IQR and std) are computed for all ECG biomarkers.

![alt text](https://github.com/SheinaG/pebm_new/blob/master/ecg_wth_bio.png?raw=true)


## Installation

Available on pip, with the command: 
pip install pecg


## Requirements

### Python Requirements:

Python >= 3.6

numpy 

mne 

wfdb 

All the python requirements except wfdb are installed when the toolbox is installed. To install wfbd run: pip install wfdb
### System Requirements:

To run the wavdet fiducial-points detector matlab runtime (MCR) 2021a is required. https://www.mathworks.com/products/compiler/matlab-runtime.html

To run the epltd peak detector additional wfdb toolbox is required. https://archive.physionet.org/physiotools/wfdb-linux-quick-start.shtml

## Installation instructions:

1. Install the "pecg" package using pip by running the command line: "pip install pecg".

2. Install the "wfdb" package using pip by running the command line: "pip install wfdb".

3. Follow the guidelines provided in the link: https://www.mathworks.com/products/compiler/matlab-runtime.html, and choose the version of 2021a(9.10).

## Documentation

https://pecg.readthedocs.io/en/latest/pecg.html
