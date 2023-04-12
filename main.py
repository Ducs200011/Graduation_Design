import numpy as np
import matplotlib.pyplot as plt
from data4fig import datafix
import json
#读入测试数据
with open('testdata.json','r') as f:
    data = json.load(f)
testp = data['testp'] #将p从json读入
p = np.array(testp)
clrlist = 'rygcbm' #最多输入6组数据，定义颜色
[m, n] = p.shape
E = np.zeros(n)
Wd = np.zeros(n)
for j in range(n):
    middata = 0
    for i in range(m):
        middata += p[i, j] * np.log(p[i, j])
    E[j] = -1/np.log(n) * middata
for j in range(n):
    Wd[j] = (1 - E[j]) / (n - sum(E))
W = np.array([0.4213, 0.1808, 0.2106, 0.1873])
Phi = W * 0.7 + Wd * 0.3
Q = p * Phi


newQ = datafix(Q)  #数据处理，使图像更美观
data_dim = 4 #数据维数
data_num = 4 #场景数量
angles = np.linspace(0, 2 * np.pi, data_dim, endpoint=False)  #设立极坐标角度
angles = np.concatenate((angles, [angles[0]]))
labels = ['供电有序性', '充裕性', '经济性', '节能环保性']   #长度应该为data_dim,设置坐标名称
labels = np.concatenate((labels, [labels[0]]))
score = newQ   #设立分数
score = np.hstack((score, score.T[0].reshape(data_num, 1)))
fig = plt.figure()   #打开figure
fig.suptitle("雷达图")
plt.rcParams['font.sans-serif'] = ['SimHei'] #防止中文乱码
ax = plt.subplot(111, polar=True)   #创建极坐标图
for i in range(4):  #绘画数据
    ax.plot(angles, score[i, :], color=clrlist[i])
ax.set_thetagrids(angles*180/np.pi, labels)
for j in np.arange(0, 120, 20): #绘画网格
    ax.plot(angles, (data_dim + 1) * [j], '-.', lw=0.5, color='black')
for j in range(data_dim):
    ax.plot([angles[j], angles[j]], [0, 120], '-', lw=0.5, color='black')
ax.spines['polar'].set_visible(False)   #隐藏最外围的圆
ax.grid(False)  #隐藏圆形网格线
#ax.set_rlabel_position(90) #坐标显示
ax.set_rticks([])   #关闭坐标显示
plt.legend(['S1', 'S2', 'S3', 'S4'], loc='best')
plt.show()
