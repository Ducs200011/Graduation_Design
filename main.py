import numpy as np
import matplotlib.pyplot as plt
from data4fig import datafix
from isahpok import isahpok
import json
import warnings
from getphi import getphi
import os
import xlwt

img_dpi = 1000      #图像dpi
#指标量化
os.system("python Elia_data_create.py")


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
        p[i, j] = (testx[i, j]) / np.sqrt(sum(np.power(testx[ii, j], 2) for ii in range(m)))
E = np.zeros(n)
Wd = np.zeros(n)
for j in range(n):  #各指标熵值计算
    middata = 0
    for i in range(m):
        middata = middata + p[i, j] * np.log(p[i, j])
    E[j] = -1 / np.log(m) * middata
for j in range(n):  #熵权值计算
    Wd[j] = (1 - E[j]) / sum(1 - E)

#组合权重
Phi = getphi(p, W, Wd)  #利用gurobi的优化算法,最小二乘法

#正负靶心
Z = p * Phi #求解加权规范化决策矩阵
newZ = datafix(Z)  #数据处理
Z_max = np.max(newZ, axis=0)
Z_min = np.min(newZ, axis=0)
D_up = np.zeros(m)
D_down = np.zeros(m)
for i in range(m):
    for j in range(n):
        D_up[i] = np.power((newZ[i, j] - Z_max[j]), 2) + D_up[i]
        D_down[i] = np.power((newZ[i, j] - Z_min[j]), 2) + D_down[i]
D_up = np.sqrt(D_up)
D_down = np.sqrt(D_down)
C = D_down / (D_up + D_down)    #C越小低碳潜力越好，C越大表示离理想方案越近
print("低碳发展状况:")
print(C)


#绘画雷达图
clrlist = 'rygcbm' #最多同时输入6组数据，定义颜色

data_dim = n #数据维数
data_num = m #场景数量
angles = np.linspace(0, 2 * np.pi, data_dim, endpoint=False)  #设立极坐标角度
angles = np.concatenate((angles, [angles[0]]))
labels = ['充裕性', '灵活性', '清洁能源装机占比', '节碳排放率', '清洁能源消纳率', '经济性']   #长度应该为data_dim,设置坐标名称'经济性'
labels = np.concatenate((labels, [labels[0]]))
score = newZ   #设立分数
score = np.hstack((score, score.T[0].reshape(data_num, 1)))
mod4 = np.mod(data_num, 4)
n_fig = int((data_num - mod4) / 4)
sz_fig = np.array([0, 2, 4, 6, 7])


#qua_in = input('是否输出季度雷达图?若需要，键入1')
qua_in = '0'
if qua_in == '1':
    # 如果要输出每季度的雷达图，读入该段程序
    dimname_full = [None] * 40  # 一次最多读入10年数据(40个)
    for i in range(data_num):
        dimname_full[i] = casename[i]  # 'S' + str(i + 1) + ':' + casename[i]
    for nfig in range(n_fig):  # 输入满4季度年份数据
        figname = '雷达图例' + str(nfig + 1)
        fig = plt.figure(figname)  # 打开figure
        fig.suptitle("各示例指标雷达图")
        plt.rcParams['font.sans-serif'] = ['SimHei']  # 防止中文乱码
        ax = plt.subplot(111, polar=True)  # 创建极坐标图
        for i in range(nfig * 4, nfig * 4 + 4):  # 绘画数据
            ax.plot(angles, score[i, :], color=clrlist[np.mod(i, 6)])
        ax.set_thetagrids(angles * 180 / np.pi, labels)
        for j in np.arange(0, 120, 20):  # 绘画网格
            ax.plot(angles, (data_dim + 1) * [j], '-', lw=0.5, color='grey')
        for j in range(data_dim):
            ax.plot([angles[j], angles[j]], [0, 100], '-', lw=0.5, color='black')
        ax.spines['polar'].set_visible(False)  # 隐藏最外围的圆
        ax.grid(False)  # 隐藏圆形网格线
        # ax.set_rlabel_position(0) #坐标显示
        ax.set_rticks([])  # 关闭坐标显示
        dimname = [dimname_full[i] for i in range(nfig * 4, nfig * 4 + 4)]
        plt.legend(dimname, loc='best')
        savefig_name = 'result/雷达图' + str(nfig + 1) + '.png'
        plt.savefig(savefig_name, dpi=img_dpi, bbox_inches='tight')  # 导出图片，尽量高像素
        print('result has been saved!')
    if mod4 != 0:  # 输入不满4季度年份数据
        figname = '雷达图例' + str(n_fig + 1)
        fig = plt.figure(figname)  # 打开figure
        fig.suptitle("各示例指标雷达图")
        plt.rcParams['font.sans-serif'] = ['SimHei']  # 防止中文乱码
        ax = plt.subplot(111, polar=True)  # 创建极坐标图
        for i in range(n_fig * 4, n_fig * 4 + mod4):  # 绘画数据
            ax.plot(angles, score[i, :], color=clrlist[np.mod(i, 6)])
        ax.set_thetagrids(angles * 180 / np.pi, labels)
        for j in np.arange(0, 120, 20):  # 绘画网格
            ax.plot(angles, (data_dim + 1) * [j], '-', lw=0.5, color='grey')
        for j in range(data_dim):
            ax.plot([angles[j], angles[j]], [0, 100], '-', lw=0.5, color='black')
        ax.spines['polar'].set_visible(False)  # 隐藏最外围的圆
        ax.grid(False)  # 隐藏圆形网格线
        # ax.set_rlabel_position(0) #坐标显示
        ax.set_rticks([])  # 关闭坐标显示
        dimname = [dimname_full[i] for i in range(n_fig * 4, n_fig * 4 + mod4)]
        plt.legend(dimname, loc='best')
        savefig_name = 'result/雷达图' + str(n_fig + 1) + '.png'
        plt.savefig(savefig_name, dpi=img_dpi, bbox_inches='tight')  # 导出图片，尽量高像素
        print('result has been saved!')




#雷达图绘画偶数年份的平均，进行比较
figname = '雷达图例'
fig = plt.figure(figname)  # 打开figure
fig.suptitle("各示例指标雷达图")
plt.rcParams['font.sans-serif'] = ['SimHei']  # 防止中文乱码
ax = plt.subplot(111, polar=True)  # 创建极坐标图
useforclr = 0
for nfig in sz_fig:
    useforclr += 1
    for i in range(nfig * 4 + 1, nfig * 4 + 4):
        score[nfig] = score[nfig] + score[i]
    score[nfig] = score[nfig] / 4
    ax.plot(angles, score[nfig, :], color=clrlist[np.mod(useforclr, 6)])
ax.set_thetagrids(angles * 180 / np.pi, labels)
for j in np.arange(0, 120, 20):  # 绘画网格
    ax.plot(angles, (data_dim + 1) * [j], '-', lw=0.5, color='grey')
for j in range(data_dim):
    ax.plot([angles[j], angles[j]], [0, 100], '-', lw=0.5, color='black')
ax.spines['polar'].set_visible(False)  # 隐藏最外围的圆
ax.grid(False)  # 隐藏圆形网格线
# ax.set_rlabel_position(0) #坐标显示
ax.set_rticks([])  # 关闭坐标显示
dimname = ['2014', '2016', '2018', '2020', '2022']
plt.legend(dimname, loc='best')
savefig_name = 'result/雷达图.png'
plt.savefig(savefig_name, dpi=img_dpi, bbox_inches='tight')  # 导出图片，尽量高像素
print('result has been saved!')

#绘画折线图
label = labels
for i in range(data_dim):
    figname = '折线图例' + str(i + 1)
    fig = plt.figure(figname)
    figtitle = label[i] + '折线图'
    fig.suptitle(figtitle)
    plt.rcParams['font.sans-serif'] = ['SimHei']  # 防止中文乱码
    x_axis_data = casename
    y_axis_data = newZ[:, i]
    plt.plot(x_axis_data, y_axis_data, '*-', color=clrlist[np.mod(i, 6)], label=label[i])
    plt.xlabel('对应时间')
    plt.xticks(rotation=70, fontsize=8)     #将坐标轴x旋转90°以避免重叠
    plt.ylabel('指标')
    #plt.yticks(visible=False)       #隐藏y轴数值，因为用不到
    plt.legend(loc='best')
    savefig_name = 'result/折线图' + str(i + 1) + '_' + label[i] + '.png'
    plt.savefig(savefig_name, dpi=img_dpi, bbox_inches='tight')
    print('result has been saved!')

figname = '折线图例' + str(data_dim + 1)
fig = plt.figure(figname)
figtitle = '碳电协同综合评价'
fig.suptitle(figtitle)
plt.rcParams['font.sans-serif'] = ['SimHei']  # 防止中文乱码
x_axis_data = casename
y_axis_data = C
plt.plot(x_axis_data, y_axis_data, '*-', color=clrlist[np.mod(data_dim, 6)], label=figtitle)
plt.xlabel('对应时间')
plt.xticks(rotation=70, fontsize=8)     #将坐标轴x旋转90°以避免重叠
plt.ylabel('指标')
#plt.yticks(visible=False)       #隐藏y轴数值，因为用不到
plt.legend(loc='best')
savefig_name = 'result/折线图' + str(data_dim + 1) + '_碳电协同综合评价.png'
plt.savefig(savefig_name, dpi=img_dpi, bbox_inches='tight')
print('result has been saved!')

#将结果以表格输出
result_xls = xlwt.Workbook()
sheet1 = result_xls.add_sheet('加权规范化决策矩阵', cell_overwrite_ok=True)
sheet2 = result_xls.add_sheet('综合决策矩阵', cell_overwrite_ok=True)
[h, l] = newZ.shape
for i in range(h):
    for j in range(l):
        sheet1.write(i, j, newZ[i, j])
    sheet2.write(i, 0, C[i])
result_xls.save('result/result.xls')
#将结果以JSON格式输出
outputZ = newZ.tolist()
outputC = C.tolist()
output_text = {'PartValue': outputZ,
               'TotalValue': outputC}
with open('result/output.json', 'w') as f3:
    json.dump(output_text, f3)
    f3.close()
print('result array has been saved!')

