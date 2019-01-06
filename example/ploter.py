# Copyright 2019 The GuQiangJS. All Rights Reserved.
# ==============================================================================

import pandas as pd
import matplotlib.pyplot as plt
import QUANTAXIS as QA

#设定绘图的默认大小
import matplotlib
matplotlib.rcParams["figure.figsize"]=[16,8]

#加载 seaborn，并且设置默认使用 seaborn
import seaborn as sns
sns.set()

matplotlib.rcParams['font.family'] = 'sans-serif'
matplotlib.rcParams['font.sans-serif'] = ['SimHei']
matplotlib.rcParams['axes.unicode_minus']=False #用来正常显示负号

from talib import MA_Type
def bbands_plot(series,t=20,matype=MA_Type.WMA):
    """绘制布林带
    默认为20日均线，加权计算
    """
    up,mean,low=QA.QAIndicator.talib_series.BBANDS(series,t,matype=matype)
    df=pd.DataFrame({'上线':up,'中线':mean,'下线':low})
    df.plot(title=' 布林带\nwindow={0}\nMA_Type={1}'.format(t,matype))
    plt.show()