import numpy as np
from typing import List
def datacheating(version: int,  #数据版本
                 baseMVA: int,  #基准功率
                 bus: List[List[float]],    #节点信息
                 gen: List[List[float]],    #发电机信息
                 branch: List[List[float]],     #支路信息
                 gencost: List[List[float]],    #发电机耗费
                 ):
    nbus = len(bus)
    ngen = len(gen)
    nbranch = len(branch)
    bus = np.array(bus)
    gen = np.array(gen)
    branch = np.array(branch)
    gencost = np.array(gencost)
