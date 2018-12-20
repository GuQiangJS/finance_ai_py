# 模拟
import pandas as pd


def simulate_buy_sale(df: pd.DataFrame, price: int = 10000, per_max_count=100):
    df = df.sort_index().reset_index()
    result = []
    remaining_funds = price
    for index in range(len(df.index)):
        # [买入日期，买入价格，数量，卖出日期，卖出价格]
        m = per_max_count * df.iloc[index]['Close']
        hfq_c = df.iloc[index]['Close_hfq']
        qfq_c = df.iloc[index]['Close_qfq']
        d = df.iloc[index]['Date']
        c = df.iloc[index]['Close']
        if df.iloc[index]['opt'] == 'b':
            if remaining_funds > m:
                result.append([d, c, hfq_c, qfq_c, per_max_count])
                remaining_funds = remaining_funds - m
        elif df.iloc[index]['opt'] == 's':
            for i in range(len(result)):
                if len(result[i]) <= 5:
                    result[i].append(d)
                    result[i].append(c)
                    result[i].append(hfq_c)
                    result[i].append(qfq_c)
                    remaining_funds = remaining_funds + m
    return result
