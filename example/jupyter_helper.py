# jupyter 部分帮助方法
from QUANTAXIS import QA_fetch_index_day_adv

def _test_index(code,start='2018-01-01',end='2018-12-31'):
    """测试指数数据是否在本地能读取到
    
    Return:
        如果数据读取正常，则返回True，否则返回False
    """
    return not QA_fetch_index_day_adv(code,start,end).data.empty

def get_zs_code():
    """获取示例时的指数（沪深300）代码，返回000300或者399300"""

    ZS_CODE=['399300','000300']#指数代码。沪深300
    for z in ZS_CODE:
        if _test_index(z):
            return z
    if not isinstance(ZS_CODE, str):
        raise AssertionError