'''
比利时电网数据生成使用
注：21年的数据不全，21年的总负荷来自22年
'''
import numpy as np
import xlrd
from datacheating import datacheating4Elia
from datacheating import datarepair
from datacheating import add02data
import json

year = ['2014', '2015', '2016', '2017', '2018', '2019', '2020', '2022', '2023']
month = ['January', 'February', 'March', 'April',
         'May', 'June', 'July', 'August',
         'September', 'October', 'November', 'December']
monthroot_gen = '/Generation_Forecast_Historical_Cipu_'
installed_power_root = '/Installed_Power_Historical_'
total_load_root = '/Total_load_'
nyear = len(year)   #记录输入数据年数

#建立公共路径
public_root = [None] * nyear
for i in range(nyear):
    public_root[i] = 'Eliadata/' + year[i] + '_Elia'


data_num = (nyear - 1) * 4 + 1        #数据数
savedfile = [None] * data_num   #保存文件
casename = [None] * data_num    #每个数据名称


for ny in range(nyear):     #年份
    #读取装机容量(整年)
    installed_power_name = public_root[ny] + installed_power_root + year[ny] + '.XLS'
    installed_power_book = xlrd.open_workbook(installed_power_name)
    sheet_installed_power = installed_power_book.sheet_by_index(0)
    rows = sheet_installed_power.nrows
    installed_power_xls = tuple(sheet_installed_power.row_values(i)[2:] for i in range(2, rows))
    installed_power_data = np.array(installed_power_xls)

    #读取负载(整年)
    load_power_name = public_root[ny] + total_load_root + year[ny] + '.xls'
    load_power_book = xlrd.open_workbook(load_power_name)
    sheet_load_power = load_power_book.sheet_by_index(0)
    rows = sheet_load_power.nrows   #92
    load_power_xls = tuple(sheet_load_power.row_values(i)[2:] for i in range(2, rows))
    load_power_data_ = np.array(load_power_xls)
    load_power_data_ = datarepair(load_power_data_)  # 由于有些数据缺乏，因此选择缺乏项的前一项填上
    load_power_data = np.zeros((rows - 2) * 96).reshape((rows - 2), 96)
    for i in range(96):  # 由于数据有一列为空，采取如下措施规避
        if i >= 8:
            load_power_data[:, i] = load_power_data_[:, i + 1]
        else:
            load_power_data[:, i] = load_power_data_[:, i]
    #读取每季度发电数据
    qua_day = np.zeros(4)   #每季度天数
    for nq in range(4):     #季度
        gen_file_name = public_root[ny] + monthroot_gen + month[nq * 3] + '_' + year[ny] + '.XLS'
        # 读取每季度第一个月的发电数据
        gen_data_book = xlrd.open_workbook(gen_file_name)
        # 读取煤炭发电数据
        sheet_coal = gen_data_book.sheet_by_index(0)
        rows = sheet_coal.nrows
        coal_xls = tuple(sheet_coal.row_values(i)[7:103] for i in range(3, rows))
        coal_data = np.array(coal_xls)
        # 读取液态燃料发电数据
        sheet_fuel = gen_data_book.sheet_by_index(1)
        rows = sheet_fuel.nrows
        fuel_xls = tuple(sheet_fuel.row_values(i)[7:103] for i in range(3, rows))
        fuel_data = np.array(fuel_xls)
        # 读取气体发电数据
        sheet_gas = gen_data_book.sheet_by_index(2)
        rows = sheet_gas.nrows
        gas_xls = tuple(sheet_gas.row_values(i)[7:103] for i in range(3, rows))
        gas_data = np.array(gas_xls)
        # 读取水力发电数据
        sheet_water = gen_data_book.sheet_by_index(3)
        rows = sheet_water.nrows
        water_xls = tuple(sheet_water.row_values(i)[7:103] for i in range(3, rows))
        water_data = np.array(water_xls)
        # 读取核电数据
        sheet_nuclear = gen_data_book.sheet_by_index(4)
        rows = sheet_nuclear.nrows
        nuclear_xls = tuple(sheet_nuclear.row_values(i)[7:103] for i in range(3, rows))
        nuclear_data = np.array(nuclear_xls)
        # 读取风电数据
        sheet_wind = gen_data_book.sheet_by_index(5)
        rows = sheet_wind.nrows
        wind_xls = tuple(sheet_wind.row_values(i)[7:103] for i in range(3, rows))
        wind_data = np.array(wind_xls)
        # 读取其他发电数据
        sheet_other = gen_data_book.sheet_by_index(6)
        rows = sheet_other.nrows
        other_xls = tuple(sheet_other.row_values(i)[7:103] for i in range(3, rows))
        other_data = np.array(other_xls)
        for nm in range(nq * 3 + 1, nq * 3 + 3):    #每个季度的月份
            gen_file_name = public_root[ny] + monthroot_gen + month[nm] + '_' + year[ny] + '.XLS'
            # 读取一个季度的发电数据
            gen_data_book = xlrd.open_workbook(gen_file_name)
            # 读取煤炭发电数据
            sheet_coal = gen_data_book.sheet_by_index(0)
            rows = sheet_coal.nrows
            coal_xls = tuple(sheet_coal.row_values(i)[7:103] for i in range(3, rows))
            coal_data_ = np.array(coal_xls)
            coal_data = np.concatenate((coal_data, coal_data_), axis=0)
            # 读取液态燃料发电数据
            sheet_fuel = gen_data_book.sheet_by_index(1)
            rows = sheet_fuel.nrows
            fuel_xls = tuple(sheet_fuel.row_values(i)[7:103] for i in range(3, rows))
            fuel_data_ = np.array(fuel_xls)
            fuel_data = np.concatenate((fuel_data, fuel_data_), axis=0)
            # 读取气体发电数据
            sheet_gas = gen_data_book.sheet_by_index(2)
            rows = sheet_gas.nrows
            gas_xls = tuple(sheet_gas.row_values(i)[7:103] for i in range(3, rows))
            gas_data_ = np.array(gas_xls)
            gas_data = np.concatenate((gas_data, gas_data_), axis=0)
            # 读取水力发电数据
            sheet_water = gen_data_book.sheet_by_index(3)
            rows = sheet_water.nrows
            water_xls = tuple(sheet_water.row_values(i)[7:103] for i in range(3, rows))
            water_data_ = np.array(water_xls)
            water_data = np.concatenate((water_data, water_data_), axis=0)
            # 读取核电数据
            sheet_nuclear = gen_data_book.sheet_by_index(4)
            rows = sheet_nuclear.nrows
            nuclear_xls = tuple(sheet_nuclear.row_values(i)[7:103] for i in range(3, rows))
            nuclear_data_ = np.array(nuclear_xls)
            nuclear_data = np.concatenate((nuclear_data, nuclear_data_), axis=0)
            # 读取风电数据
            sheet_wind = gen_data_book.sheet_by_index(5)
            rows = sheet_wind.nrows
            wind_xls = tuple(sheet_wind.row_values(i)[7:103] for i in range(3, rows))
            wind_data_ = np.array(wind_xls)
            wind_data = np.concatenate((wind_data, wind_data_), axis=0)
            # 读取其他发电数据
            sheet_other = gen_data_book.sheet_by_index(6)
            rows = sheet_other.nrows
            other_xls = tuple(sheet_other.row_values(i)[7:103] for i in range(3, rows))
            other_data_ = np.array(other_xls)
            other_data = np.concatenate((other_data, other_data_), axis=0)

            #每季度的数据修复
            coal_data = add02data(coal_data)
            fuel_data = add02data(fuel_data)
            gas_data = add02data(gas_data)
            water_data = add02data(water_data)
            nuclear_data = add02data(nuclear_data)
            wind_data = add02data(wind_data)
            other_data = add02data(other_data)
            installed_power_data = add02data(installed_power_data)
            load_power_data = add02data(load_power_data)

        qua_day[nq] = len(fuel_data)    #当年每季度的天数
        #在整年中选择当季度的负载与装机容量的数据读取范围
        starttag = np.sum(qua_day) - qua_day[nq]    #开始标记
        endtag = np.sum(qua_day)    #结束标记,结束标记所在的数不会被读入
        installed_power_data_in = np.zeros(int(qua_day[nq]) * 7).reshape(int(qua_day[nq]), 7)
        load_power_data_in = np.zeros(int(qua_day[nq]) * 96).reshape(int(qua_day[nq]), 96)
        print('year:' + year[ny] + 'qua:' + str(nq+1))
        for i in range(int(qua_day[nq])):
            installed_power_data_in[i] = installed_power_data[i + int(starttag)]
            load_power_data_in[i] = load_power_data[i + int(starttag)]
        #这里是季度的逻辑层
        #根据季度读入数据并且生成结果
        #生成数据
        casename[ny * 4 + nq] = 'Y' + year[ny] + ',Q' + str(nq + 1)
        testout = datacheating4Elia(
            coal_data,
            fuel_data,
            gas_data,
            nuclear_data,
            water_data,
            wind_data,
            other_data,
            installed_power_data_in,
            load_power_data_in)
        savedfile[ny * 4 + nq] = testout
        print('data has been created!')
        if year[ny] == '2023':
            break

with open('data_EWM_Elia.json', 'w') as f:
    json.dump({'data_EWM': savedfile, 'casename': casename}, f)
    print('Elia data has been saved!')
    f.close()
