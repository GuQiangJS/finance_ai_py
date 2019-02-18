# jupyter 部分帮助方法
import os

import QUANTAXIS as QA
import numpy as np
import pandas as pd
import pyfolio as pf
import sklearn.linear_model
import talib
from QUANTAXIS.QAUtil.QADate import QA_util_datetime_to_strdate as date_to_str
from pandas import DataFrame
from pyecharts import Line
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from talib import MA_Type


def _test_index(code, start='2018-01-01', end='2018-12-31'):
    """测试指数数据是否在本地能读取到
    
    Return:
        如果数据读取正常，则返回True，否则返回False
    """
    return not QA.QA_fetch_index_day_adv(code, start, end).data.empty


def get_benchmark_code():
    """获取示例时的指数（沪深300）代码，返回000300或者399300"""

    zs_code = ['399300', '000300']  # 指数代码。沪深300
    for code in zs_code:
        if _test_index(code):
            return code
    if not isinstance(zs_code, str):
        raise AssertionError


def get_start_end_date(benchmark_code: str = None):
    """根据指数代码获取开始日期和结束日期

    Args:
        benchmark_code: 指数代码。如果为空则会调用get_benchmark_code获取。

    Returns:(datetime.datetime,datetime.datetime)
    """
    if not benchmark_code:
        benchmark_code = get_benchmark_code()
    ds = QA.QA_fetch_index_day_adv(benchmark_code,
                                   QA.QAUtil.QADate_trade.trade_date_sse[0],
                                   QA.QAUtil.QADate.QA_util_today_str()).date
    return ds[0], ds[-1]


def get_year_stats(start, end, benchmark_code=None, lst=None, auto_save=True,
                   filename=None) -> pd.DataFrame:
    """
    读取指定股票的年度分析数据。如果文件不存在或有部分内容不存在，则读取部分内容。

    部分内容以单支股票为单位。加入只是有部分年份不存在，又或者上次生成文件时2018年，但现在时2020年，缺少2019年的数据时，也不会重新生成。

    Args:
        auto_save: 有新数据时是否保存
        filename: 文件名。如果为None，则为datas/stock_stas_year.h5。
        start: 开始时间
        end: 结束时间
        benchmark_code: 指数代码。如果为空则会调用get_benchmark_code获取。
        lst: 股票代码列表。为None时，自动获取所有列表。

    Returns:
    """
    if not filename:
        filename = os.path.join(os.getcwd(), 'datas', 'stock_stats_year.h5')
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    if not benchmark_code:
        benchmark_code = get_benchmark_code()

    if lst is None or len(lst) == 0:
        lst = QA.QA_fetch_stock_list_adv().code.values

    stats_by_year = pd.DataFrame()  # type: DataFrame
    if os.path.exists(filename):
        stats_by_year = pd.read_hdf(
            filename, key='year', mode='r').astype('float64')
    has_new = False
    for stock in lst:
        if stats_by_year.empty:
            stats_by_year = calc_perf_stats_by_year(
                stock, benchmark_code, start, end)
            has_new = True
        elif stock not in stats_by_year.index.unique(0).values:
            d = calc_perf_stats_by_year(stock, benchmark_code, start, end)
            if d.empty:
                continue
            stats_by_year = stats_by_year.append(d)
            has_new = True
    if has_new and auto_save:
        stats_by_year.to_hdf(filename, key='year', mode='w')
        print('{0} updated.'.format(filename))
    return stats_by_year


def calc_daily_return(s: pd.Series) -> pd.Series:
    '''计算日收益'''
    return (s / s.shift(1) - 1)[1:]


def calc_perf_stats_by_year(code: str, benchmark_code: str, start,
                            end) -> pd.DataFrame:
    """计算指定股票年度数据指标。
    计算 benchmark_code 开始年份 ~ 当前年份的前一年

    Args:
        code:
        benchmark_code:
        start:
        end:
    """
    start_str = start if isinstance(start, str) else date_to_str(start)
    end_str = end if isinstance(end, str) else date_to_str(end)
    zs_data = QA.QA_fetch_index_day_adv(benchmark_code, start_str,
                                        end_str)  # 指数日线数据

    result = pd.DataFrame()

    stock_data_bfq = QA.QA_fetch_stock_day_adv(code, start_str,
                                               end_str)  # 不复权的日线数据
    if stock_data_bfq is None or stock_data_bfq.data.empty:
        return result

    stock_data_qfq = stock_data_bfq.to_qfq()  # 前复权日线数据
    for year in range(start.year, end.year):
        s = pd.Series()
        zs_daily_return = calc_daily_return(
            zs_data.data[zs_data.date.year == year]['close'])  # 指数日收益
        stock_daily_return_qfq = calc_daily_return(
            stock_data_qfq[stock_data_qfq.date.year == year]['close'])  # 股票日收益

        if not stock_daily_return_qfq.empty:
            stock_daily_return_qfq_remove_code = stock_daily_return_qfq.reset_index(
            ).drop(columns=['code']).set_index('date')
            zs_daily_return_remove_code = zs_daily_return.reset_index().drop(
                columns=['code']).set_index('date')

            stock_daily_return_qfq_remove_code_year = \
                stock_daily_return_qfq_remove_code[
                    stock_daily_return_qfq_remove_code.index.year == year]  # 当年股票日收益（前复权）
            zs_daily_return_remove_code_year = zs_daily_return_remove_code[
                zs_daily_return_remove_code.index.year == year]
            s = pf.timeseries.perf_stats(
                stock_daily_return_qfq_remove_code_year.close,
                zs_daily_return_remove_code_year.close)
        else:
            s = pf.timeseries.perf_stats(stock_daily_return_qfq,
                                         zs_daily_return)

        if not s.empty:
            s['code'] = code
            s['year'] = year
            if result.empty:
                result = s.to_frame().T.set_index(['code', 'year'])
            else:
                result = result.append(s.to_frame().T.set_index(
                    ['code', 'year']))
    return result.astype(np.float64)


def normalize_data(df):
    """数据归一化"""
    return df / df.iloc[0]


def get_qfq_stock_close(code, start, end):
    """读取指定股票的收盘价日线数据"""
    start_str = start if isinstance(start, str) else date_to_str(start)
    end_str = end if isinstance(end, str) else date_to_str(end)

    return QA.QA_fetch_stock_day_adv(code, start_str,
                                     end_str).to_qfq().reset_index().drop(
        columns=['code']).set_index('date').close


def get_qfq_index_close(start, end) -> pd.DataFrame:
    """读取指数的日线收盘价数据"""
    start_str = start if isinstance(start, str) else date_to_str(start)
    end_str = end if isinstance(end, str) else date_to_str(end)
    code = get_benchmark_code()

    return pd.DataFrame.from_dict(
        {code: QA.QA_fetch_index_day_adv(code, start_str,
                                         end_str).reset_index().drop(
            columns=['code']).set_index('date').close})


def plot_line_daily_close(title, codes, start, end,
                          benchmark_code=get_benchmark_code(), legend_top='15%',
                          datazoom_extra_type='both',
                          is_datazoom_extra_show=True,
                          datazoom_extra_orient='horizontal',
                          **kwargs):
    """使用 `pyechart` 绘制Line。使用 **收盘价格** 经过 **归一化** 后绘制。
    绘制图片时横坐标可以缩放。

    使用 `legend_top` 控制图例的位置。使其不会与标题重叠。

    Args:
        datazoom_extra_type: 参见 `line.add` 方法的同名参数
        is_datazoom_extra_show: 参见 `line.add` 方法的同名参数
        datazoom_extra_orient: 参见 `line.add` 方法的同名参数
        legend_top: 参见 `line.add` 方法的同名参数
        datazon
        title: 主标题
        codes: 待绘制的股票代码
        start: 开始日期
        end: 结束日期
        benchmark_code: 指数代码
        **kwargs: 参考 `Line` 中的参数

    Returns:(pyecharts.Line,pd.DataFrame)
    """
    line = Line(title, **kwargs)
    # 读取收盘价
    df = get_qfq_index_close(start, end)
    for code in codes:
        df = df.join(pd.DataFrame.from_dict(
            {code: get_qfq_stock_close(code, start, end)}))  # 取复权收盘价
    df = normalize_data(df.fillna(method='ffill'))  # 归一化，并且填充nan值
    line.add(benchmark_code, df.index.date, np.round(df[benchmark_code], 2))
    for code in codes:
        line.add(code, df.index.date, np.round(df[code], 2),
                 datazoom_extra_type=datazoom_extra_type, legend_top=legend_top,
                 is_datazoom_extra_show=is_datazoom_extra_show,
                 datazoom_extra_orient=datazoom_extra_orient)
    return line, df


def _talib_matype_tostr(matype: MA_Type):
    if matype == MA_Type.SMA:
        return "Simple Moving Average"
    elif matype == MA_Type.EMA:
        return "Exponential Moving Average"
    elif matype == MA_Type.DEMA:
        return "Double Exponential Moving Average"
    elif matype == MA_Type.KAMA:
        return "Kaufman Adaptive Moving Averagee"
    elif matype == MA_Type.MA:
        return "Moving average"
    elif matype == MA_Type.MAMA:
        return "MESA Adaptive Moving Average"
    elif matype == MA_Type.T3:
        return "Triple Exponential Moving Average (T3)"
    elif matype == MA_Type.TEMA:
        return "Triple Exponential Moving Average"
    elif matype == MA_Type.TRIMA:
        return "Triangular Moving Average"
    elif matype == MA_Type.WMA:
        return "Weighted Moving Average"
    return ''


def talib_bbands_tostr(matype: MA_Type = None, timeperiod=None, nbdevup=None,
                       nbdevdn=None):
    s = ''
    if matype:
        s = s + '{0},'.format(_talib_matype_tostr(matype))
    if timeperiod:
        s = s + '时间段:{},'.format(timeperiod)
    if nbdevup:
        s = s + '上限:{} 标准差,'.format(nbdevup)
    if nbdevdn:
        s = s + '下限:{} 标准差,'.format(nbdevdn)
    return s


def get_talib_stock_daily(stock_code, s, e, append_ori_close=False,
                          norms=['volume', 'amount', 'ht_dcphase', 'obv',
                                 'adosc', 'ad', 'cci']):
    """获取经过talib处理后的股票日线数据"""
    stock_data = QA.QA_fetch_stock_day_adv(stock_code, s, e)
    stock_df = stock_data.to_qfq().data
    if append_ori_close:
        stock_df['o_close'] = stock_data.data['close']
    # stock_df['high_qfq'] = stock_data.to_qfq().data['high']
    # stock_df['low_hfq'] = stock_data.to_hfq().data['low']

    close = np.array(stock_df['close'])
    high = np.array(stock_df['high'])
    low = np.array(stock_df['low'])
    _open = np.array(stock_df['open'])
    _volume = np.array(stock_df['volume'])

    stock_df['dema'] = talib.DEMA(close)
    stock_df['ema'] = talib.EMA(close)
    stock_df['ht_tradeline'] = talib.HT_TRENDLINE(close)
    stock_df['kama'] = talib.KAMA(close)
    stock_df['ma'] = talib.MA(close)
    stock_df['mama'], stock_df['fama'] = talib.MAMA(close)
    # MAVP
    stock_df['midpoint'] = talib.MIDPOINT(close)
    stock_df['midprice'] = talib.MIDPRICE(high, low)
    stock_df['sar'] = talib.SAR(high, low)
    stock_df['sarext'] = talib.SAREXT(high, low)
    stock_df['sma'] = talib.SMA(close)
    stock_df['t3'] = talib.T3(close)
    stock_df['tema'] = talib.TEMA(close)
    stock_df['trima'] = talib.TRIMA(close)
    stock_df['wma'] = talib.WMA(close)

    stock_df['adx'] = talib.ADX(high, low, close)
    stock_df['adxr'] = talib.ADXR(high, low, close)
    stock_df['apo'] = talib.APO(close)

    stock_df['aroondown'], stock_df['aroonup'] = talib.AROON(high, low)
    stock_df['aroonosc'] = talib.AROONOSC(high, low)
    stock_df['bop'] = talib.BOP(_open, high, low, close)
    stock_df['cci'] = talib.CCI(high, low, close)
    stock_df['cmo'] = talib.CMO(close)
    stock_df['dx'] = talib.DX(high, low, close)
    # MACD
    stock_df['macd'], stock_df['macdsignal'], stock_df[
        'macdhist'] = talib.MACDEXT(
        close)
    # MACDFIX
    stock_df['mfi'] = talib.MFI(high, low, close, _volume)
    stock_df['minus_di'] = talib.MINUS_DI(high, low, close)
    stock_df['minus_dm'] = talib.MINUS_DM(high, low)
    stock_df['mom'] = talib.MOM(close)
    stock_df['plus_di'] = talib.PLUS_DI(high, low, close)
    stock_df['plus_dm'] = talib.PLUS_DM(high, low)
    stock_df['ppo'] = talib.PPO(close)
    stock_df['roc'] = talib.ROC(close)
    stock_df['rocp'] = talib.ROCP(close)
    stock_df['rocr'] = talib.ROCR(close)
    stock_df['rocr100'] = talib.ROCR100(close)
    stock_df['rsi'] = talib.RSI(close)
    stock_df['slowk'], stock_df['slowd'] = talib.STOCH(high, low, close)
    stock_df['fastk'], stock_df['fastd'] = talib.STOCHF(high, low, close)
    # STOCHRSI - Stochastic Relative Strength Index
    stock_df['trix'] = talib.TRIX(close)
    stock_df['ultosc'] = talib.ULTOSC(high, low, close)
    stock_df['willr'] = talib.WILLR(high, low, close)

    stock_df['ad'] = talib.AD(high, low, close, _volume)
    stock_df['adosc'] = talib.ADOSC(high, low, close, _volume)
    stock_df['obv'] = talib.OBV(close, _volume)

    stock_df['ht_dcperiod'] = talib.HT_DCPERIOD(close)
    stock_df['ht_dcphase'] = talib.HT_DCPHASE(close)
    stock_df['inphase'], stock_df['quadrature'] = talib.HT_PHASOR(close)
    stock_df['sine'], stock_df['leadsine'] = talib.HT_PHASOR(close)
    stock_df['ht_trendmode'] = talib.HT_TRENDMODE(close)

    stock_df['avgprice'] = talib.AVGPRICE(_open, high, low, close)
    stock_df['medprice'] = talib.MEDPRICE(high, low)
    stock_df['typprice'] = talib.TYPPRICE(high, low, close)
    stock_df['wclprice'] = talib.WCLPRICE(high, low, close)

    stock_df['atr'] = talib.ATR(high, low, close)
    stock_df['natr'] = talib.NATR(high, low, close)
    stock_df['trange'] = talib.TRANGE(high, low, close)

    stock_df['beta'] = talib.BETA(high, low)
    stock_df['correl'] = talib.CORREL(high, low)
    stock_df['linearreg'] = talib.LINEARREG(close)
    stock_df['linearreg_angle'] = talib.LINEARREG_ANGLE(close)
    stock_df['linearreg_intercept'] = talib.LINEARREG_INTERCEPT(close)
    stock_df['linearreg_slope'] = talib.LINEARREG_SLOPE(close)
    stock_df['stddev'] = talib.STDDEV(close)
    stock_df['tsf'] = talib.TSF(close)
    stock_df['var'] = talib.VAR(close)

    stock_df = stock_df.reset_index().set_index('date')

    if norms:
        x = stock_df[norms].values  # returns a numpy array
        x_scaled = MinMaxScaler().fit_transform(x)
        stock_df = stock_df.drop(columns=norms).join(
            pd.DataFrame(x_scaled, columns=norms, index=stock_df.index))

    # stock_df = stock_df.drop(columns=['code', 'open', 'high', 'low'])
    stock_df = stock_df.dropna()
    stock_df = stock_df.drop(columns=['code'])
    return stock_df


def get_calc_data(stock_code, s, e, fq='qfq',
                  drop_columns=['code', 'preclose', 'adj'],
                  scaler=['amount', 'volume'],
                  scaler_func=sklearn.preprocessing.MinMaxScaler):
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


def create_validate_df_close(df, days) -> pd.DataFrame:
    '''根据 `df` 中的 close 列，制作新的数据。
    根据参数 `days` 增加列，有多少days增加多少列，每一列对应了当前日期后第几天的close数据
    '''
    if 'close' not in df.columns:
        raise ValueError('数据中不包含 close 列。')
    df_copy = df.copy()
    for i in range(1, days + 1):
        df_copy[i] = df_copy.shift(i * -1).close
    return df_copy[[i for i in range(1, days + 1)]].dropna()


def get_prediction_close(f, days, df) -> pd.DataFrame:
    """对应了 `create_validate_df_close` 创建的数据的获取验证结果的方法

    Args:
        f: `fit` 方法返回值0的实例。
        days:
        df: `get_calc_data` 方法返回的计算数据的全部或部分

    Returns:

    """
    test = f.predict(df)
    result = df['close'].reset_index().join(
        pd.DataFrame(test, columns=[i for i in range(1, days + 1)])).set_index(
        'date')
    return result
    return result['close'][1:].to_frame().reset_index().join(
        result.iloc[0].to_frame('prediction')).set_index('date')


def fit(df, days, test_size=0.1, func=sklearn.linear_model.Ridge,
        create_validate_func=create_validate_df_close,random_state=4):
    """
    Args:
        df:
        days:
        func:
        create_validate_func:
        test_size: 测试集占比

    Returns:
        (func经过fit后的实例，X_train, X_test, y_train, y_test)
    """
    y = create_validate_func(df, days)
    X = df[df.index.isin(y.index)]
    #     y=np.round(y,4)
    #     X=np.round(X,4)
    # 定义测试
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size,random_state=random_state)
    X_train.shape, X_test.shape, y_train.shape, y_test.shape
    f = func()
    f.fit(X_train, y_train)
    return f, X_train, X_test, y_train, y_test
