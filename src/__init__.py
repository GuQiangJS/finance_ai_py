# Copyright (C) 2018 GuQiangJs.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

__all__ = ['unit']

import warnings
from sys import platform

import matplotlib.pyplot as plt
import seaborn as sns

# 禁止在python运行时显示警告信息
warnings.filterwarnings('ignore')

# 绘图支持中文字体
sns.set_style('whitegrid')
if platform == 'darwin':
    sns.set_style({'font.sans-serif': 'SimHei'})
elif platform == 'win32':
    sns.set_style({'font.sans-serif': 'SimHei'})

plt.rcParams['axes.unicode_minus'] = False
