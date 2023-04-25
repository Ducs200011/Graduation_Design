'''
用来进行数据处理，包括matpower的和比利时电网数据
'''
import numpy as np
from typing import List
'''处理matpower数据'''
def datacheating4mat(version: int,  #数据版本
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
    Pgmax = [gen[i, 8] for i in range(ngen)]    #发电机输出最大功率
    Pgmin = [gen[i, 9] for i in range(ngen)]    #发电机输出最小功率
    Qgmax = [gen[i, 3] for i in range(ngen)]    #发电机输出无功最大值
    Qgmin = [gen[i, 4] for i in range(ngen)]    #发电机输出无功最小值
    Pd = [bus[i, 2] for i in range(nbus)]       #负载数据
    Pg = [gen[i, 1] for i in range(ngen)]       #发电数据
    adequacy = (np.sum(Pgmax) - np.max(Pgmax) - np.sum(Pd)) / (np.sum(Pgmax) - np.max(Pgmax))   #充裕性指标
    flex = np.min([Pgmax[i] - Pg[i] for i in range(ngen)])   #灵活性指标
    cleaneng_use = 0
    cleaneng_total = 0
    for i in range(ngen):
        if gencost[i, 0] == 1:
            cleaneng_use = Pg[i] + cleaneng_use
            cleaneng_total = Pgmax[i] + cleaneng_total
    cleanrate = cleaneng_use / cleaneng_total     #清洁能源利用率
    cleanness = cleaneng_use / np.sum(Pg)         #清洁性指标
    cost_all = 0
    for i in range(ngen):
        cost_all = gen[i, 7] * (gencost[i, 1] + gencost[i, 3]) + (1 - gen[i, 7]) * (gencost[i, 2]) + cost_all
    eco = 1 / cost_all      #经济性指标
    sample_data = [adequacy, flex, cleanrate, cleanness, eco]
    return sample_data

'''处理比利时电网数据'''
def datacheating4Elia(fuel_data,
                      gas_data,
                      water_data,
                      nuclear_data,
                      wind_data,
                      other_data,
                      installed_power_data,
                      load_power_data,
                      dtime):
    new_energy_data = water_data + wind_data
    ordinary_energy_data = fuel_data + gas_data + nuclear_data + other_data
    gen_energy_data = new_energy_data + ordinary_energy_data
    gen_load_cov = np.cov(gen_energy_data[dtime], load_power_data[dtime]) / (np.std(gen_energy_data[dtime]) * np.std(load_power_data[dtime]))
    adequacy = gen_load_cov[0, 1]   #充裕性指标
    i_p4flex = installed_power_data[dtime, 0] + installed_power_data[dtime, 3] + installed_power_data[dtime, 4] + installed_power_data[dtime, 5]        #可调节能源装机
    e4flex = np.max(i_p4flex - fuel_data[dtime] - wind_data[dtime] - wind_data[dtime] - other_data[dtime])
    flex = np.max(load_power_data[dtime] - gen_energy_data[dtime]) / e4flex     #灵活性指标
    cleaneng_use = new_energy_data[dtime]
    cleaneng_total = installed_power_data[dtime, 3] + installed_power_data[dtime, 4]
    cleanrate = np.mean(cleaneng_use / cleaneng_total)   #清洁能源利用率
    cleanness = np.mean(cleaneng_use / gen_energy_data)     #清洁性指标
    eco = np.mean((5 * (fuel_data[dtime] + gas_data[dtime]) + 8 * nuclear_data[dtime] + 10 * water_data[dtime] + 6 * wind_data[dtime] + 12 * other_data[dtime]) / load_power_data[dtime])   #经济性指标
    sample_data = [adequacy, flex, cleanrate, cleanness, eco]
    print(sample_data)
    return sample_data
