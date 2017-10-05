from scipy import signal

def decimate(x, q):
    import time
    start = time.clock()
    return signal.decimate(x, q, None, 'iir', -1)
    elapsed = time.clock() - start
    print "Decimate Time: ", elapsed
