# 本文件用于AWG器件版图设计
import numpy as np
import math
from numpy import cos, sin, tan, pi, sqrt, deg2rad, rad2deg
import matplotlib.pyplot as plt

# # 测试数据
# Narray = 24  # 阵列波导数
# m = 45  # 衍射级次
# lambda_c = 1.55  # 工作中心波长
# neff = 2.4337  # 阵列波导有效折射率
# Ra = 12.592  # FPR长度
# delta_L = m*lambda_c/neff  # 阵列波导总长度差
# da = 0.6  # 阵列波导中心间距
# theta_offset = deg2rad(90)  # 星形耦合器倾斜角度
# waveguide_width = 0.5  # 波导宽度

Narray = 30  # 阵列波导数
m = 3  # 衍射级次
lambda_c = 1.5  # 工作中心波长
neff = 1.62  # 阵列波导有效折射率
Ra = 800  # FPR长度
delta_L = m*lambda_c/neff  # 阵列波导总长度差
da = 6  # 阵列波导中心间距
theta_offset = deg2rad(55)  # 星形耦合器倾斜角度
waveguide_width = 1.2  # 波导宽度

# 初始化声明
L = np.zeros(Narray)  # 直波导长度
theta = np.zeros(Narray)  # 阵列波导起始角度
R = np.zeros(Narray)  # 阵列波导弯曲部分半径
# 计算阵列波导倾斜角度
L[0] = 100  # 直波导初始长度
R[0] = 950  # 初始弯曲波导半径

# # 测试数据
# R[0] = 50

for i in range(1, Narray+1):
    theta[i-1] = da * (i - (Narray + 1)/2) / Ra + theta_offset
D = 2 * ( (Ra + L[0]) * cos(theta[0]) + R[0] * sin(theta[0]) )  # 输入/输出自由传输区顶点间距
L_0 = 2 * (L[0] + R[0] * theta[0])  # 阵列波导第一根总长度

for i in range(1, Narray):
    R[i] = (L_0/2 - cos(theta[i]) * ((L_0 + i*delta_L)/2 + Ra)) / (sin(theta[i]) - theta[i]*cos(theta[i]))
    L[i] = (L_0 + i*delta_L) / 2 - R[i] * theta[i]

channel = np.arange(1, Narray + 1)

# 绘制L1 - i关系图
plt.subplot(1, 3, 1)   # 第 1 个子图
plt.plot(channel, L, "o", markerfacecolor="none")
plt.xlabel("Channel#")
plt.ylabel("L")
plt.title("L vs. Channel")
plt.xlim(1, Narray)

# 绘制R - i关系图
plt.subplot(1, 3, 2)
plt.plot(channel, R, "o", markerfacecolor="none")
plt.xlabel("Channel#")
plt.ylabel("R")
plt.title("R vs. Channel")
plt.xlim(1, Narray)

plt.subplot(1, 3, 3)
plt.plot(channel, rad2deg(theta), "o", markerfacecolor="none")
plt.xlabel("Channel#")
plt.ylabel("theta")
plt.title("theta vs. Channel")
plt.xlim(1, Narray)

plt.show()
