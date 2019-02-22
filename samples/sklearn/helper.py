# Copyright (C) 2018 GuQiangJs.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

import QUANTAXIS as QA
import pandas as pd
import pyecharts
from sklearn.linear_model import Ridge
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler


def create_validate_df_close(df: pd.DataFrame,
                             days: int,
                             column: str = 'close') -> pd.DataFrame:
    """制作验证用数据。

    根据 df[column].shift(-days)` 查找指定天数后的指定列的数据作为验证数据。

    Args:
        df: 数据源
        days: 天数
        column: 使用的列
    """
    if column not in df.columns:
        raise ValueError('数据中不包含 {} 列。'.format(column))
    return pd.DataFrame(df[column].shift(-1 * days).values,
                        columns=[days],
                        index=df.index).dropna()


def _get_calc_data(stock_code, s, e, fq='qfq',
                   drop_columns=['code', 'preclose', 'adj'],
                   scaler=['amount', 'volume'],
                   scaler_func=MinMaxScaler):
    """获取计算用数据源

    Args:
        fq: 是否采用复权数据。默认使用前复权。如果不需要复权则传''即可。
        stock_code:
        s:
        e:
        drop_columns: 丢弃的列
        scaler: 需要做归一化的数据列。
        scaler_func: 做归一化时默认使用的方法。
    """
    raw_data = QA.QA_fetch_stock_day_adv(stock_code, s, e)
    calc_data = raw_data.data.reset_index().set_index(
        'date').copy()
    if fq == 'qfq':
        qfq_data = raw_data.to_qfq().data.reset_index().set_index(
            'date')  # DataFrame格式
        calc_data = qfq_data.copy()
    elif fq == 'hfq':
        qfq_data = raw_data.to_qfq().data.reset_index().set_index(
            'date')  # DataFrame格式
        calc_data = qfq_data.copy()
    if drop_columns:
        calc_data = calc_data.drop(columns=drop_columns)  # 丢弃多余的列
    if scaler:
        calc_data[scaler] = scaler_func().fit_transform(
            calc_data[scaler])
    return calc_data


def do_fit(stockcode: str, s: str, e: str, days: int, func=Ridge(), data=None,
           test_size: float = 0.2, column: str = 'close', random_state=1):
    """

    Args:
        stockcode:
        s:
        e:
        days: 天数
        func: 实现了`fit`方法的sklearn函数
        data: 数据集。当数据集不存在时调用`_get_calc_data`获取数据集。
        test_size: 验证集占比
        column: 制作验证集时使用的列。列需要存在于数据集data中。

    Returns:(func,func.score得分,数据源,结果集)

    """
    if data is None:
        data = _get_calc_data(stockcode, s, e)

    y = create_validate_df_close(data, days, column=column)

    X = data[data.index.isin(y.index)]
    # 拆分数据源
    X_train, X_test, y_train, y_test = train_test_split(X, y,
                                                        test_size=test_size,
                                                        random_state=random_state)

    func.fit(X_train, y_train)
    score = func.score(X_test, y_test)

    return func, score, X, y


def get_fit_report(X, y, func, days, column: str = 'close') -> pd.DataFrame:
    """对测试数据集获取验证结果

    Args:
        X: 测试数据集
        func: 实现了`predict`方法的sklearn函数
        days: 天数

    Returns:

    """
    Z = X[[column]].rename(columns={column: '当日收盘价'}).join(
        y[[days]].rename(columns={days: '{}日后收盘价'.format(days)}))
    return Z.join(
        pd.DataFrame(func.predict(X), index=X.index).rename(columns={0: '预测值'}))


def plot_report(days, func, X,y, column: str = 'close', title='', subtitle=''):
    r = get_fit_report(X,y, func, days, column)
    line = pyecharts.Line('{} Days'.format(days) if not title else title,
                          subtitle=subtitle)
    for col in r.columns:
        line.add(col, r.index.date, r[col], datazoom_extra_type='both',
             is_datazoom_extra_show=True,
             datazoom_extra_orient='horizontal',
            yaxis_min='dataMin',
            yaxis_max='dataMax')
    # line.add('实际值', data.index.date, data[column], datazoom_extra_type='both',
    #          is_datazoom_extra_show=True,
    #          datazoom_extra_orient='horizontal')
    # line.add('预测值', r.index.date, r[0], datazoom_extra_type='both',
    #          is_datazoom_extra_show=True,
    #          datazoom_extra_orient='horizontal')
    return line
