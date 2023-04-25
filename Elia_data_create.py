'''比利时电网数据生成使用'''
import numpy as np
import xlrd
from datacheating import datacheating4Elia
import json

#读取发电数据(gen_data)
gen_data_book = xlrd.open_workbook('gen_data.xls')
#读取液态燃料发电数据
sheet_fuel = gen_data_book.sheet_by_index(1)
rows = sheet_fuel.nrows
fuel_xls = tuple(sheet_fuel.row_values(i)[7:] for i in range(3, rows))
fuel_data = np.array(fuel_xls)
#读取气体发电数据
sheet_gas = gen_data_book.sheet_by_index(2)
rows = sheet_gas.nrows
gas_xls = tuple(sheet_gas.row_values(i)[7:] for i in range(3, rows))
gas_data = np.array(gas_xls)
#读取水力发电数据
sheet_water = gen_data_book.sheet_by_index(3)
rows = sheet_water.nrows
water_xls = tuple(sheet_water.row_values(i)[7:] for i in range(3, rows))
water_data = np.array(water_xls)
#读取核电数据
sheet_nuclear = gen_data_book.sheet_by_index(4)
rows = sheet_nuclear.nrows
nuclear_xls = tuple(sheet_nuclear.row_values(i)[7:] for i in range(3, rows))
nuclear_data = np.array(nuclear_xls)
#读取风电数据
sheet_wind = gen_data_book.sheet_by_index(5)
rows = sheet_wind.nrows
wind_xls = tuple(sheet_wind.row_values(i)[7:] for i in range(3, rows))
wind_data = np.array(wind_xls)
#读取其他发电数据
sheet_other = gen_data_book.sheet_by_index(6)
rows = sheet_other.nrows
other_xls = tuple(sheet_other.row_values(i)[7:] for i in range(3, rows))
other_data = np.array(other_xls)


#读取装机容量
installed_power_book = xlrd.open_workbook('installed_power.xls')
sheet_installed_power = installed_power_book.sheet_by_index(0)
installed_power_xls = tuple(sheet_installed_power.row_values(i)[3:] for i in range(2, 33))  #只读取1月份数据
installed_power_data = np.array(installed_power_xls)


#读取负载
load_power_book = xlrd.open_workbook('load.xls')
sheet_load_power = load_power_book.sheet_by_index(0)
load_power_xls = tuple(sheet_load_power.row_values(i)[2:] for i in range(2, 33))    #只读取1月份信息
load_power_data_ = np.array(load_power_xls)
load_power_data = np.zeros(31 * 96).reshape(31, 96)
for i in range(96):     #由于数据有一列为空，只能采取如下措施
    if i >= 8:
        load_power_data[:, i] = load_power_data_[:, i + 1]
    else:
        load_power_data[:, i] = load_power_data_[:, i]

#生成数据
data_num = 5
savedfile = [None] * data_num
casename = [None] * data_num
for i in range(data_num):
    casename[i] = str(i * 7 + 1) + ' Jan'
    dtime = i * 7 + 1       #加的数代表一周的某一天
    testout = datacheating4Elia(fuel_data,
                      gas_data,
                      water_data,
                      nuclear_data,
                      wind_data,
                      other_data,
                      installed_power_data,
                      load_power_data,
                      dtime - 1)
    savedfile[i] = testout
with open('data_EWM_Elia.json', 'w') as f:
    json.dump({'data_EWM': savedfile, 'casename': casename}, f)
    print('Elia data has been saved!')
    f.close()