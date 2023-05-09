import pandas as pd

# ticker_info is a dataFrame
def strategy_boll(ticker_info):
    # 布林线策略-改
    # 近7天内连续两次下穿下界，构成买入信号
    # 近7天内连续两次上穿上界，构成卖出信号
    ticker = ticker_info.copy()
    ticker['Signal'] = 0
    # close price
    ticker.loc[ticker['Close'] < ticker['BOLL_lower'], 'Signal'] = 1
    ticker.loc[ticker['Close'] > ticker['BOLL_upper'], 'Signal'] = -1
    # 最近7个交易日2次价格出发下BOLL界，买入信号
    if ticker['Signal'].tail(7).sum() >= 2:
        return 'buy_signal'
    # 最近7个交易日2次价格触发上BOLL界，卖出信号
    if ticker['Signal'].tail(7).sum() <= -2:
        return 'sold_signal'
    
    return None

def strategy_sma(ticker_info):
    # SMA策略
    # 近7天内5日/10日均线上穿20日/50日均线时买入
    # 近7天内5日/10日均线下穿20日/50日均线时卖出
    ticker = ticker_info.copy()
    ticker['Signal'] = 0
    # close price
    ticker.loc[ticker['MA5'] > ticker['MA20'], 'Signal'] = 1
    ticker.loc[ticker['MA5'] < ticker['MA20'], 'Signal'] = -1
    ticker['Shift_signal'] = ticker['Signal'].shift(-1)
    ticker['Final_signal'] = 0
    # 前一天<0，当天>0，买入
    ticker.loc[(ticker['Signal'] > 0) & (ticker['Shift_signal'] < 0), 'Final_signal'] = 1
    # 前一天>0，当天>0，卖出
    ticker.loc[(ticker['Signal'] < 0) & (ticker['Shift_signal'] > 0), 'Final_signal'] = -1
    # 近7天存在买入信号，买入
    if ticker['Final_signal'].tail(7).sum() > 0:
        return 'buy_signal'
    # 近7天存在卖出信号，卖出
    if ticker['Final_signal'].tail(7).sum() < 0:
        return 'sold_signal'
    
    return None