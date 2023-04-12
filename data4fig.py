import numpy as np
def datafix(AR,): #浮动范围，最小值20-30，最大值90-100
    [m, n] = AR.shape
    liemin = np.min(AR, axis=0)
    liemax = np.max(AR, axis=0)
    liegap = liemax - liemin
    lieminmax = np.max(liemin)
    lieminmin = np.min(liemin)
    liemaxmax = np.max(liemax)
    liemaxmin = np.min(liemax)
    liemingap = lieminmax - lieminmin
    liemaxgap = liemaxmax - liemaxmin
    ARopt = np.zeros(m * n)
    ARopt = ARopt.reshape(m, n)
    for j in range(n):
        for i in range(m):
            jiding = (liemax[j] - liemaxmin) / liemaxgap * 10
            jidi = (liemin[j] - lieminmin) / liemingap * 10
            ARopt[i, j] = (AR[i, j] - liemin[j]) / liegap[j] * 60 + 20 + jiding + jidi
    return ARopt