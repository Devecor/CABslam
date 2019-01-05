import numpy as np
def affine_detect():
    params = [(1.0, 0.0)]
    print params[0]
    for t in 2**(0.5*np.arange(1,6)):
        for phi in np.arange(0, 180, 72.0 / t):
            params.append((t, phi))
            print "(%.2f, %2.f)" % (t, phi)
    print params
affine_detect()
