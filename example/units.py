import talib


def _translate_ma_type(ma_type: talib.MA_Type):
    """获取 `talib.MA_Type` 对应的中文信息"""
    if ma_type == talib.MA_Type.SMA:
        return '简单移动平均线'
    elif ma_type == talib.MA_Type.EMA:
        return '指数移动平均线'
    elif ma_type == talib.MA_Type.WMA:
        return '加权移动平均线'
    elif ma_type == talib.MA_Type.DEMA:
        return '双指数移动平均线'
    elif ma_type == talib.MA_Type.TEMA:
        return '三倍指数移动平均线'
    elif ma_type == talib.MA_Type.TRIMA:
        return '三角移动平均线'
    elif ma_type == talib.MA_Type.KAMA:
        return '考夫曼自适应移动平均线'
    elif ma_type == talib.MA_Type.MAMA:
        return 'MESA自适应移动平均线'
    elif ma_type == talib.MA_Type.T3:
        return '三倍广义双指数移动平均线'
