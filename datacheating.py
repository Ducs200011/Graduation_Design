'''
用来进行数据处理，包括matpower的和比利时电网数据
计算各指标值，对各指标进行量化
'''
import numpy as np
from typing import List
import pyomo.environ as pyo

'''修复缺少的数据'''
def datarepair(datainput):
    m, n = datainput.shape
    dataoutput = np.zeros(m * n).reshape(m, n)
    for i in range(m):  # 输入格式有时候是字符串不是浮点数，因此需要进行一次数据类型修改
        for j in range(n):
            if datainput[i, j]:
                dataoutput[i, j] = float(datainput[i, j])
    for i in range(m):  # 由于有些数据缺乏，因此选择缺乏项的前一项填上
        for j in range(n):
            if not datainput[i, j]:
                dataoutput[i, j] = (float(dataoutput[i, j - 1]) + float(dataoutput[i - 1, j])) / 2
    return dataoutput

'''发展到后期有些能源不存在消耗，因此需要补零'''
def add02data(datainput):
    m, n = datainput.shape
    dataoutput = np.zeros(m * n).reshape(m, n)
    for i in range(m):  # 由于有些数据缺乏，因此选择缺乏项的前一项填上
        for j in range(n):
            if not datainput[i, j]:
                dataoutput[i, j] = 0
            else:
                dataoutput[i, j] = float(datainput[i, j])
    return np.array(dataoutput)

'''求平均，去掉最大最小的两组'''
def mymean(dataiput):
    nday = len(dataiput)
    dataoutput = (np.sum(dataiput) - np.max(dataiput) - np.min(dataiput)) / (nday - 2)
    return dataoutput



'''
处理matpower数据
matpower数据指标:
1.充裕性指标
2.灵活性指标
3.清洁能源利用率
4.清洁性指标
5.经济性指标
'''
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

'''
处理比利时电网数据
Elia数据指标:
1.充裕性指标（容载比）
2.灵活性指标（备用占比）
3.清洁能源装机占比
4.清洁能源互补性
5.节碳排放率
6.清洁能源消纳率
7.经济性（单位购电成本）
'''
def datacheating4Elia(coal_data,    #280
                      fuel_data,    #250
                      gas_data,     #230
                      nuclear_data, #80
                      water_data,   #60
                      wind_data,    #5
                      other_data,   #70
                      installed_power_data,
                      load_power_data,):
    nday = len(coal_data)   #本季度天数
    new_energy_data = water_data + wind_data    #清洁能源总和
    ordinary_energy_data = coal_data + fuel_data + gas_data + nuclear_data + other_data     #传统能源总和
    gen_energy_data = new_energy_data + ordinary_energy_data    #总装机
    ip_all = np.sum(installed_power_data, axis=1)   #每日装机总和
    ip_new = installed_power_data[:, 4] + installed_power_data[:, 5] #清洁能源装机
    ip_ordinary = ip_all - ip_new
    load_max = np.max(load_power_data, axis=1)      #每日最大负载
    load_day = np.mean(load_power_data, axis=1)     #每日负载平均
    coal_day = np.mean(coal_data, axis=1)   #每日煤炭输出平均
    fuel_day = np.mean(fuel_data, axis=1)   #每日液态燃料输出平均
    gas_day = np.mean(gas_data, axis=1)     ##每日天然气输出平均
    nuclear_day = np.mean(nuclear_data, axis=1)    #每日核电输出平均
    water_day = np.mean(water_data, axis=1)     #每日水电输出平均
    wind_day = np.mean(wind_data, axis=1)       #每日风电输出平均
    other_day = np.mean(other_data, axis=1)     #每日其他发电输出平均
    gen_energy_day = coal_day + fuel_day + gas_day + nuclear_day + water_day + wind_day + other_day
    pshed_day = load_day - gen_energy_day       #缺负荷
    for i in range(len(pshed_day)):
        if pshed_day[i] > 0 and pshed_day[i] < load_day[i] * 0.05:
            pshed_day[i] = 0
        elif pshed_day[i] < 0 and pshed_day[i] > -load_day[i] * 0.20:
            pshed_day[i] = 0
        if pshed_day[i] < 0:
            pshed_day[i] = pshed_day[i] * 0.7
    #计算充裕性指标
    ade_all = (ip_all - load_max) / load_max
    adequacy = mymean(ade_all)
    #计算灵活性指标
    left_flex = (installed_power_data[:, 1] + installed_power_data[:, 4] +\
                installed_power_data[:, 5] + installed_power_data[:, 6]) +\
                (np.max(fuel_data) + np.max(water_data) + np.max(wind_data) + np.max(other_data))   #每日可调能源剩余
    flex_all = left_flex / load_max
    flex = mymean(flex_all)
    #计算清洁能源装机占比
    cleanrate_all = ip_new / ip_all
    cleanrate = mymean(cleanrate_all)
    #计算清洁能源互补性,利用相关系数计算
    clean_comp_all = np.zeros(nday)
    for i in range(nday):
        cleancov = np.corrcoef(water_data[i] + wind_data[i], gas_data[i])
        clean_comp_all[i] = 1 - cleancov[0, 1]
    clean_comp = mymean(clean_comp_all)
    #节碳排放率
    c_e_true = 280 * coal_day + 250 * fuel_day + 230 * gas_day +\
               80 * nuclear_day + 60 * water_day + 20 * wind_day + 70 * other_day + 160 * pshed_day
    c_e_min = getcemin(gen_energy_day, installed_power_data) + 160 * pshed_day
    car_de_all = c_e_true / c_e_min
    car_de = mymean(car_de_all)
    #清洁能源消纳率
    cleaneng_use = np.max(water_data, axis=1) + np.max(wind_data, axis=1)
    cleaneng_total = installed_power_data[:, 4] + installed_power_data[:, 5]
    cleanness_all = cleaneng_use / (0.9 * cleaneng_total + 0.8 * pshed_day)
    cleanness = mymean(cleanness_all)
    #经济性
    eco_use = 12 * coal_day + 8 * fuel_day + 8.5 * gas_day +\
              9 * nuclear_day + 9 * water_day + 6 * wind_day + 11 * other_day + 10 * pshed_day
    eco_best = 9 * load_day
    eco_all = eco_best / eco_use
    eco = mymean(eco_all)

    #输出结果
    sample_data = [adequacy, flex, cleanrate, car_de, cleanness, eco]
    print('量化结果:')
    print(sample_data)
    return sample_data


'''用于计算节碳排放率的子函数'''
def getcemin(gen_energy_day, installed_power_data):
    nday = len(gen_energy_day)
    gen_all = gen_energy_day
    coal_day = np.zeros(nday)
    fuel_day = np.zeros(nday)
    gas_day = np.zeros(nday)
    nuclear_day = np.zeros(nday)
    water_day = np.zeros(nday)
    wind_day = np.zeros(nday)
    other_day = np.zeros(nday)
    for i in range(nday):
        #重设风电
        eng_allo = installed_power_data[i, 5]
        if (gen_all[i] - eng_allo) > 0:
            gen_all[i] = gen_all[i] - eng_allo
            wind_day[i] = eng_allo
        else:
            if gen_all[i] > 0:
                wind_day[i] = gen_all[i]
                gen_all[i] = gen_all[i] - eng_allo
            else:
                wind_day[i] = 0
        #重设水电
        eng_allo = installed_power_data[i, 4]
        if (gen_all[i] - eng_allo) > 0:
            gen_all[i] = gen_all[i] - eng_allo
            water_day[i] = eng_allo
        else:
            if gen_all[i] > 0:
                water_day[i] = gen_all[i]
                gen_all[i] = gen_all[i] - eng_allo
            else:
                water_day[i] = 0
        #重设其他能源
        eng_allo = installed_power_data[i, 6]
        if (gen_all[i] - eng_allo) > 0:
            gen_all[i] = gen_all[i] - eng_allo
            other_day[i] = eng_allo
        else:
            if gen_all[i] > 0:
                other_day[i] = gen_all[i]
                gen_all[i] = gen_all[i] - eng_allo
            else:
                other_day[i] = 0
        #重设核电
        eng_allo = installed_power_data[i, 3]
        if (gen_all[i] - eng_allo) > 0:
            gen_all[i] = gen_all[i] - eng_allo
            nuclear_day[i] = eng_allo
        else:
            if gen_all[i] > 0:
                nuclear_day[i] = gen_all[i]
                gen_all[i] = gen_all[i] - eng_allo
            else:
                nuclear_day[i] = 0
        #重设气体
        eng_allo = installed_power_data[i, 2]
        if (gen_all[i] - eng_allo) > 0:
            gen_all[i] = gen_all[i] - eng_allo
            gas_day[i] = eng_allo
        else:
            if gen_all[i] > 0:
                gas_day[i] = gen_all[i]
                gen_all[i] = gen_all[i] - eng_allo
            else:
                gas_day[i] = 0
        #重设液态燃料
        eng_allo = installed_power_data[i, 1]
        if (gen_all[i] - eng_allo) > 0:
            gen_all[i] = gen_all[i] - eng_allo
            fuel_day[i] = eng_allo
        else:
            if gen_all[i] > 0:
                fuel_day[i] = gen_all[i]
                gen_all[i] = gen_all[i] - eng_allo
            else:
                fuel_day[i] = 0
        #重设煤电
        eng_allo = installed_power_data[i, 0]
        if (gen_all[i] - eng_allo) > 0:
            gen_all[i] = gen_all[i] - eng_allo
            coal_day[i] = eng_allo
        else:
            if gen_all[i] > 0:
                coal_day[i] = gen_all[i]
                gen_all[i] = gen_all[i] - eng_allo
            else:
                coal_day[i] = 0
    dataoutput = 280 * coal_day + 250 * fuel_day + 230 * gas_day +\
               80 * nuclear_day + 60 * water_day + 20 * wind_day + 70 * other_day
    return dataoutput


'''计算节碳排放率的子函数废案'''
def getcemin_new(gen_energy_day, installed_power_data):
    nday = len(gen_energy_day)

    model = pyo.ConcreteModel()
    model.D = pyo.Set(initialize=list(range(nday)))

    model.coal = pyo.Var(model.D, domain=pyo.NonNegativeReals)
    model.fuel = pyo.Var(model.D, domain=pyo.NonNegativeReals)
    model.gas = pyo.Var(model.D, domain=pyo.NonNegativeReals)
    model.nuclear = pyo.Var(model.D, domain=pyo.NonNegativeReals)
    model.water = pyo.Var(model.D, domain=pyo.NonNegativeReals)
    model.wind = pyo.Var(model.D, domain=pyo.NonNegativeReals)
    model.other = pyo.Var(model.D, domain=pyo.NonNegativeReals)
    def obj_rule(model, d):
        cost = 280 * model.coal[d] + 250 * model.fuel[d] + 230 * model.gas[d] +\
               80 * model.nuclear[d] + 60 * model.water[d] + 20 * model.wind[d] + 70 * model.other[d]
        return cost

    def cons_coal(model, d):
        return model.coal[d] <= installed_power_data[d, 0]

    def cons_fuel(model, d):
        return model.fuel[d] <= installed_power_data[d, 1]

    def cons_gas(model, d):
        return model.gas[d] <= installed_power_data[d, 2]

    def cons_nuclear(model, d):
        return model.nuclear[d] <= installed_power_data[d, 3]

    def cons_water(model, d):
        return model.water[d] <= installed_power_data[d, 4]

    def cons_wind(model, d):
        return model.wind[d] <= installed_power_data[d, 5]

    def cons_other(model, d):
        return model.other[d] <= installed_power_data[d, 6]

    def all_is(model, d):
        return  model.coal[d] + model.fuel[d] + model.gas[d] + model.nuclear[d] +\
            model.water[d] + model.wind[d] + model.other[d] == gen_energy_day[d]


    #objection function
    model.Obj = pyo.Objective(model.D, rule=obj_rule, sense=pyo.minimize)

    #constrains
    model.cons_coal = pyo.Constraint(model.D, rule=cons_coal)
    model.cons_fuel = pyo.Constraint(model.D, rule=cons_fuel)
    model.cons_gas = pyo.Constraint(model.D, rule=cons_gas)
    model.cons_nuclear = pyo.Constraint(model.D, rule=cons_nuclear)
    model.cons_water = pyo.Constraint(model.D, rule=cons_water)
    model.cons_wind = pyo.Constraint(model.D, rule=cons_wind)
    model.cons_other = pyo.Constraint(model.D, rule=cons_other)
    model.all_is = pyo.Constraint(model.D, rule=all_is)

    dataoutput = 280 * np.array([pyo.value(model.coal[j]) for j in model.D])

    return dataoutput