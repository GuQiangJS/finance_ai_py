#日常引用的头文件，其他ipynb文件可以引用这个

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import QUANTAXIS as QA
import datetime

#设定绘图的默认大小
import matplotlib
matplotlib.rcParams["figure.figsize"]=[16,8]

#加载 seaborn，并且设置默认使用 seaborn
import seaborn as sns
sns.set()

matplotlib.rcParams['font.family'] = 'sans-serif'
matplotlib.rcParams['font.sans-serif'] = ['SimHei']
matplotlib.rcParams['axes.unicode_minus']=False #用来正常显示负号

import os