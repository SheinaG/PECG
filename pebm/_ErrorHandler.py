import numpy as np


def _check_shape_(signal, fs):
    assert len(signal) > fs*5, "Signal must be at list five seconds"
    signal = np.array(signal)
    assert len(signal.shape) == 1, "Signal must be 1-d dimension array"


def _check_fragment_PRSA_(d):
    assert d > 0, "The parameter d should be strictly positive"


class WrongParameter(Exception):
    pass