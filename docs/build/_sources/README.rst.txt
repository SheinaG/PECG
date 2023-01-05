PhysioZoo ECG documentation
===========================

Digital electrocardiography biomarkers to assess cardiac conduction.

Based on the paper 
S. Gendelman et al., "PhysioZoo ECG: Digital electrocardiography biomarkers to assess cardiac conduction," 2021 Computing in Cardiology (CinC), 2021, pp. 1-4, doi: 10.23919/CinC53138.2021.9662857.

Introduction
----------------------

The electrocardiogram (ECG) is a standard tool used in medical practice for identifying cardiac pathologies. Because the necessary expertise to interpret this tracing is not readily available in all medical institutions or at all in some large areas of developing countries, there is a need to create a data-driven approach that can automatically capture the information contained in this physiological time series. The primary objective of this package is to identify and implement clinically important digital ECG biomarkers for the purpose of creating a reference toolbox and software for ECG morphological analysis.

Description
----------------------

Few steps are required to extract the morphological ECG biomarkers, thos steps are impelemented in the PEBM toolbox:

1. ECG Signal Preprocessing - Before computing the ECG morphological biomarkers, prefiltering of the raw ECG time series is performed to remove the baseline wander as well as remove high frequency noise. Specifically, the toolbox include a zero phase second-order infinite impulse response bandpass filter with the passband of 0.67Hz - 100Hz to remove baseline wander and high frequency noise. Also, the toolbox include an optional Notch filter that can be set to 50 or 60Hz to remove the power-line interference.

2. ECG Fiducial Points Detection - The toolbox include the epltd R-peaks algorithem, and the the well-known wavedet algorithm for ECG fiducial points  detection. 

3. Engineering of ECG Biomarkers - Using the fiducial points ECG biomarkers are engineered for individual ECG cycles. When a biomarker cannot be engineered because some fiducial points could not be detected by wavedet then the feature was marked as a NaN. For an ECG channel a total of 14 features are extracted from intervals duration and 8 from waves characteristics to describe the ECG morphology.

.. image:: ../ecg_wth_bio.png
  :width: 600


4. Summary Statistics - For a specified time window the five summary statistics (median, min, max, Ql and Q3) are computed for all ECG biomarkers.

Installation
-----------------------

Available on pip, with the command: 

pip install pecg

Requirements
-----------------------

Python >= 3.6

numpy == 1.20.2

mne == 0.23.0

scipy == 1.7.0

wfdb == 3.4.0

All the requirements are installed when the toolbox is installed, no need for additional commands.

System Requirements
------------------------

For linux- to run the wavdet fiucial-points detector 'matlab runtime (MCR) 2021a'_ is requierd. 

.. _matlab runtime (MCR) 2021a: https://www.mathworks.com/products/compiler/matlab-runtime.html

For windows- to run the wavdet fiucial-points detector 'matlab runtime (MCR) 2020a'_ is requierd.

.. _matlab runtime (MCR) 2020a: https://www.mathworks.com/products/compiler/matlab-runtime.html

If you wish to use the epltd peak detector 'additional wfdb toolbox'_ is requierd. 

.. _additional wfdb toolbox: https://archive.physionet.org/physiotools/wfdb-linux-quick-start.shtml.

If you don't want or can't install this - It's Ok! you can use another peak detectors from the package.

Documentation
------------------------

https://pecg.readthedocs.io/en/latest/
