'''
判断AHP法是否能够使用，并且输出AHP的权重矩阵
'''
import numpy as np
def isahpok(inputahp,):
    n = len(inputahp)
    RIlist = np.array([0, 0, 0.58, 0.90, 1.12, 1.24, 1.32, 1.41, 1.45])
    tzz, tzary = np.linalg.eig(inputahp)
    index = np.argmax(tzz)  #标记最大特征值位置
    tzz_max = np.real(tzz[index])
    tzary_max = np.real(tzary[:, index])    #AHP的w
    #归一化处理
    output = np.zeros(n)
    for i in range(n):
        output[i] = tzary_max[i] / np.sqrt(sum(np.power(tzary_max[ii], 2) for ii in range(n)))
    CI = (tzz_max - n) / (n - 1)
    RI = RIlist[n - 1]
    CR = CI / RI
    if CR < 0.1:
        return 1, output
    else:
        return 0, output
