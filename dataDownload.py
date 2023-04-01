import talib
import pandas as pd
import yfinance as yf
import datetime


GLOBAL_FILE_PATH = "E:\\amequant_data"

def download():
    # 下载股票历史数据
    symbol = 'AAPL'
    start_date = '2020-01-01'
    end_date = '2022-03-22'
    df = pd.DataFrame()
    df = yf.download(symbol, start=start_date, end=end_date)

    folder_path = GLOBAL_FILE_PATH + "\\" + level1_path
    file_path = GLOBAL_FILE_PATH + "\\" + level1_path + "\\" + level2_path + ".csv"

    # 计算BOLL线
    df['MA20'] = talib.SMA(df['Close'], timeperiod=20)
    df['STD20'] = talib.STDDEV(df['Close'], timeperiod=20)
    df['UpperBand'] = df['MA20'] + 2 * df['STD20']
    df['LowerBand'] = df['MA20'] - 2 * df['STD20']

    # 计算买卖信号
    df['Signal'] = 0
    df.loc[df['Close'] < df['LowerBand'], 'Signal'] = 1
    df.loc[df['Close'] > df['UpperBand'], 'Signal'] = -1

    # 计算持仓状态和收益
    df['Position'] = df['Signal'].shift(1)
    df['Position'].fillna(method='ffill', inplace=True)
    df['Returns'] = df['Close'] * df['Position'].shift(1)

    # 计算累计收益率和绘图
    df['CumReturns'] = (df['Returns'].cumsum() + 1).fillna(1)
    df[['Close', 'UpperBand', 'LowerBand']].plot(figsize=(10, 6))
    df['CumReturns'].plot(figsize=(10, 6), secondary_y=True)


if __name__ == "__main__":
    download()