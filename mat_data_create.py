'''
用来将多组matpower数据生成数据集
'''
import json
from datacheating import datacheating4mat
inputcasename = ['case9', 'case5', 'case14', 'case30', 'case300']       #手动修改，根据matdata文件夹内文件添加所需数据
data_dim = 5    #数据维度，在维度修改后需要修改
data_num = len(inputcasename)
casename = [None] * data_num
savedfile = [None] * data_num
for i in range(data_num):
    casename[i] = 'matdata/' + inputcasename[i] + '.json'
for i in range(data_num):
    with open(casename[i], 'r') as f:
        data = json.load(f)
        test = datacheating4mat(**data)
        savedfile[i] = test
        f.close()
with open('data_EWM_mat.json', 'w') as f:
    json.dump({'data_EWM': savedfile, 'casename': inputcasename}, f)
    print('mat data has been saved!')
    f.close()
