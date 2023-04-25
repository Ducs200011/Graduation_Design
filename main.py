import numpy as np
import matplotlib.pyplot as plt
from data4fig import datafix
from isahpok import isahpok
import json
import warnings
from getphi import getphi

#读入测试数据,f1为熵权法所用矩阵，f2为层次分析法所用矩阵
with open('data_AHP.json', 'r') as f2, open('data_EWM_Elia.json') as f1:
    data_AHP = json.load(f2)
    data_EWM = json.load(f1)
    ahp_data = data_AHP['AHPjudge']
    testx = data_EWM['data_EWM']
    casename = data_EWM['casename']
    f1.close()
    f2.close()
#testp = data['xorb'] #将p从json读入，p表示归一化矩阵

#AHP法
ahp_data = np.array(ahp_data)
ahp_flg, W = isahpok(ahp_data)
if ahp_flg == 0:
    warnings.warn("AHP法不可用！不满足一致性")
    exit(1)
#W = np.array([0.4213, 0.1808, 0.2106, 0.1873])  #由AHP得到的权值
#W = np.array([0.087, 0.173, 0.206, 0.206, 0.328])
#W = np.array([0.4541, 0.2546, 0.8458, 0.0662, 0.0962])

#熵权法
testx = np.array(testx)
[m, n] = testx.shape
p = np.zeros(m * n).reshape(m, n)
for i in range(m):
    for j in range(n):
        p[i, j] = (1 + testx[i, j]) / sum((1 + testx[ii, j] for ii in range(m)))
E = np.zeros(n)
Wd = np.zeros(n)
for j in range(n):  #各指标熵值计算
    middata = 0
    for i in range(m):
        middata += p[i, j] * np.log(p[i, j])
    E[j] = -1 / np.log(m) * middata
for j in range(n):  #熵权值计算
    Wd[j] = (1 - E[j]) / sum(1 - E)

#组合权重
#Phi = W * 0.7 + Wd * 0.3        #最小二乘法
Phi = getphi(p, W, Wd)

#正负靶心
Z = p * Phi #求解加权规范化决策矩阵
Z_max = np.max(Z, axis=0)
Z_min = np.min(Z, axis=0)
D_up = np.zeros(m)
D_down = np.zeros(m)
for i in range(m):
    for j in range(n):
        D_up[i] += np.power((Z[i, j] - Z_max[j]), 2)
        D_down[i] += np.power((Z[i, j] - Z_min[j]), 2)
D_up = np.sqrt(D_up)
D_down = np.sqrt(D_down)
C = D_down / (D_up + D_down)    #C越小低碳潜力越好，C越大表示离理想方案越近
print("低碳潜力评估(值越小相应低碳潜力越好,值越大方案越理想):")
print(C)

#绘图
clrlist = 'rygcbm' #最多同时输入6组数据，定义颜色
newZ = datafix(Z)  #数据处理，使图像更美观
data_dim = n #数据维数
data_num = m #场景数量
angles = np.linspace(0, 2 * np.pi, data_dim, endpoint=False)  #设立极坐标角度
angles = np.concatenate((angles, [angles[0]]))
labels = ['充裕性', '灵活性', '清洁能源调用率', '清洁性', '经济性']   #长度应该为data_dim,设置坐标名称'经济性'
labels = np.concatenate((labels, [labels[0]]))
score = newZ   #设立分数
score = np.hstack((score, score.T[0].reshape(data_num, 1)))
fig = plt.figure("图例1")   #打开figure
fig.suptitle("各示例指标雷达图")
plt.rcParams['font.sans-serif'] = ['SimHei'] #防止中文乱码
ax = plt.subplot(111, polar=True)   #创建极坐标图
for i in range(data_num):  #绘画数据
    ax.plot(angles, score[i, :], color=clrlist[i])
ax.set_thetagrids(angles*180/np.pi, labels)
for j in np.arange(0, 120, 20): #绘画网格
    ax.plot(angles, (data_dim + 1) * [j], '-', lw=0.5, color='grey')
for j in range(data_dim):
    ax.plot([angles[j], angles[j]], [0, 100], '-', lw=0.5, color='black')
ax.spines['polar'].set_visible(False)   #隐藏最外围的圆
ax.grid(False)  #隐藏圆形网格线
#ax.set_rlabel_position(0) #坐标显示
ax.set_rticks([])   #关闭坐标显示
dimname_full = [None] * 10
for i in range(data_num):
    dimname_full[i] = 'S' + str(i + 1) + ':' + casename[i]
dimname = [dimname_full[i] for i in range(m)]
plt.legend(dimname, loc='best')
plt.savefig('result/result.png', dpi=1000)  #导出图片，尽量高像素
print('result has been saved!')
plt.show()
