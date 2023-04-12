import talib
import json
import copy
import matplotlib.pyplot as plt
from mplfinance.original_flavor import candlestick_ohlc
import matplotlib.dates as mdates
import pandas as pd

class YfinanceTickerInfo:
    def __init__(self, ticker, data_frame):
        # data
        self.ticker = ticker
        self.__data = data_frame

        # indicators
        # self.__indicators = {}
        self.__indicators = self.__data.copy() # dataFrame方便操作
        self.init_K()
        self.init_MA()
    
    def init_K(self):
        pass # data数据集成open/low/high/close

    def init_MA(self):
        # 移动平均线MA(SMA) default
        self.__indicators['MA5'] = talib.SMA(self.__indicators['Close'], timeperiod=5)
        self.__indicators['MA10'] = talib.SMA(self.__indicators['Close'], timeperiod=10)
        self.__indicators['MA20'] = talib.SMA(self.__indicators['Close'], timeperiod=20)
        self.__indicators['MA30'] = talib.SMA(self.__indicators['Close'], timeperiod=30)
        self.__indicators['MA50'] = talib.SMA(self.__indicators['Close'], timeperiod=50)
        self.__indicators['MA60'] = talib.SMA(self.__indicators['Close'], timeperiod=60)
        self.__indicators['MA120'] = talib.SMA(self.__indicators['Close'], timeperiod=120)
        self.__indicators['MA250'] = talib.SMA(self.__indicators['Close'], timeperiod=250)

    def get_indicators(self):
        return self.__indicators

    def get_K(self):
        return self.__indicators[['Open', 'Low', 'High', 'Close']]

    def get_MA(self, period):
        key = 'MA' + str(period)
        if self.__indicators.get(key) is None:
            self.__indicators[key] = talib.SMA(self.__indicators['Close'], timeperiod=period)
        
        return self.__indicators[key]

    def get_BOLL(self, period=20, delta=2):
        # 布林(BOLL)线
        # ma
        makey = 'MA' + str(period)
        if self.__indicators.get(makey) is None:
            self.__indicators[makey] = talib.SMA(self.__indicators['Close'], timeperiod=period)
        # std
        stdkey = 'STD' + str(period)
        if self.__indicators.get(stdkey) is None:
            self.__indicators[stdkey] = talib.STDDEV(self.__indicators['Close'], timeperiod=period)
        # upper/lower band
        upkey = 'BOLL_' + str(period) + '_' + str(delta) + '_upper'
        lokey = 'BOLL_' + str(period) + '_' + str(delta) + '_lower'
        if self.__indicators.get(upkey) is None: # 默认上下限同步操作
            self.__indicators[upkey] = self.__indicators[makey] + delta * self.__indicators[stdkey]
            self.__indicators[lokey] = self.__indicators[makey] - delta * self.__indicators[stdkey]
        
        return self.__indicators[upkey], self.__indicators[lokey]

    def dump_data(self, data_path=None):
        with open('dmypy.json', 'r') as f:
            jsdata = json.load(f)
        tic_path = jsdata['folder_path'] if data_path is None else data_path
        tic_path += "\\indicator_data\\" # tickerInfo_path

        self.__indicators.tocsv(tic_path)
        print("成功导入{}。".format(self.ticker))
        return
    
    def plot_data(self, indicators=['K'], period=None):
        # 信息补全
        if 'BOLL' in indicators:
            boll_list = [col for col in self.__indicators.columns if ('BOLL' in col and 'upper' in col)]
            if len(boll_list) == 0:
                _, _ = self.get_BOLL(period=20, delta=2)

        plt_data = self.__indicators.tail(period).copy() if period is not None else self.__indicators.copy()
        plt_data['Date'] = pd.to_datetime(plt_data['Date']).map(mdates.date2num) # 画图需将时间轴转为mdates格式
        plt_data.set_index('Date', inplace=True)
        
        if len(indicators) < 1:
            print("绘制指标选择异常。")
            return
        
        fig, ax = plt.subplots(figsize=(16, 9))
        for ind in indicators:
            if ind == 'K':
                plt_k = plt_data[['Open', 'High', 'Low', 'Close']]
                plt_k.reset_index(inplace=True)
                candlestick_ohlc(ax, plt_k.values, width=0.75, colorup='red', colordown='green', alpha=0.75)
            elif ind == 'MA': # MA判别，暂仅支持一次性全部画全
                ma_list = [col for col in plt_data.columns if 'MA' in col]
                for ma in ma_list:
                    ax.plot(plt_data[ma], label=ma)
            elif ind == 'BOLL': # 布林线判别，暂仅支持一次性全部画全
                boll_list = [col for col in plt_data.columns if ('BOLL' in col and 'upper' in col)]
                if len(boll_list) == 0:
                    _, _ = self.get_BOLL(period=20, delta=2)
                    boll_list = [col for col in plt_data.columns if ('BOLL' in col and 'upper' in col)]
                for boll in boll_list:
                    boll_up = boll
                    boll_lo = boll[:-5] + 'lower'
                    ax.fill_between(plt_data.index, plt_data[boll_up], plt_data[boll_lo], alpha=0.2)
        
        ax.set_title(self.ticker, fontsize=20)
        ax.legend(loc='upper left')
        ax.set_xlabel('date')
        ax.set_ylabel('price')
        ax.xaxis_date()
        plt.show()



#     # 计算BOLL线
# df['MA20'] = talib.SMA(df['Close'], timeperiod=20)
# df['STD20'] = talib.STDDEV(df['Close'], timeperiod=20)
# df['UpperBand'] = df['MA20'] + 2 * df['STD20']
# df['LowerBand'] = df['MA20'] - 2 * df['STD20']

# # 计算买卖信号
# df['Signal'] = 0
# df.loc[df['Close'] < df['LowerBand'], 'Signal'] = 1
# df.loc[df['Close'] > df['UpperBand'], 'Signal'] = -1

# # 计算持仓状态和收益
# df['Position'] = df['Signal'].shift(1)
# df['Position'].fillna(method='ffill', inplace=True)
# df['Returns'] = df['Close'] * df['Position'].shift(1)

# # 计算累计收益率和绘图
# df['CumReturns'] = (df['Returns'].cumsum() + 1).fillna(1)
# df[['Close', 'MA20', 'UpperBand', 'LowerBand']].plot(figsize=(10, 6))
# # df['CumReturns'].plot(figsize=(10, 6), secondary_y=True)


