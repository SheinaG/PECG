import numpy as np
import wfdb


def load_example(ecg_type: str) -> (np.ndarray, int):
    """
The load_example function loads ECG signal from some of the PhysioNet open source datasets. There are three types of ECG examples: long single lead ECG, 12-lead and a Holter with two channels.

    :param  ecg_type: The type of the signal that you would like download: 'single-lead', '12-lead' and 'Holter'.
    :return:
        * signal: the ECG signal as a ndarray, with shape (L, N) when L is the number of channels or leads and N is the number of samples.
        * fs: The sampling frequency of the signal [Hz].


    .. code-block:: python

        import pecg
        from pecg.Example import load_example
        signal, fs = load_example(ecg_type='12-lead')

    """
    if ecg_type == 'Holter':
        signal, fields = wfdb.rdsamp('100', pn_dir='mitdb')

    if ecg_type == '12-lead':
        signal, fields = wfdb.rdsamp('JS00001', pn_dir='ecg-arrhythmia/WFDBRecords/01/010')

    if ecg_type == 'single-lead':
        signal, fields = wfdb.rdsamp('a01', pn_dir='apnea-ecg')

    #signal = np.transpose(signal)

    return signal, fields['fs']


