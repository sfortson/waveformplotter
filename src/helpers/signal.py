from scipy import signal


def decimate(x, q):
    return signal.decimate(x, q, None, "iir", -1)
