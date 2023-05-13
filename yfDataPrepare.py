import yfinance as yf
import pandas as pd
import datetime as dt
import json
import requests
import csv
import os
import talib
from yfDataStrategy import *

def init_tickers_list(__api_key):
        # 获取股票数据
        # path 1 从datahub.io中搜索数据（数据不全）
        # all_tickers = pd.read_csv('https://datahub.io/core/s-and-p-500-companies/r/constituents.csv')
        # all_tickers_symbols = all_tickers.Symbol.tolist()
        # path 2 从www.alphavantage.co中拉取股票代码
        # 设置API密钥和API地址
        api_url = f'https://www.alphavantage.co/query?function=LISTING_STATUS&apikey={__api_key}'

        # 发送请求并获取JSON数据
        with requests.Session() as req:
            response = req.get(api_url)
            data = response.content.decode('utf-8')
            cr = csv.reader(data.splitlines(), delimiter=',')
            cr_list = list(cr)

        df = pd.DataFrame(cr_list[1:], columns=cr_list[0])
            
        # 提取股票代码并打印
        tickers_list = list(df['symbol'])
        print("股票代码：{}".format(",".join(tickers_list)))
        return tickers_list

class yfDataAtomic:
    def __init__(self, ticker, data_path, proxy, start_date, end_date):
        self.ticker = ticker
        self.data_path = data_path
        self.proxy = proxy
        self.start_date = start_date
        self.end_date = end_date
        self.ticker_data = None
        self.ticker_info = None
        self.ticker_selected = None
    
    def reload_data(self):
        if self.ticker == 'PRN': # extra check PRN is a reserved name in Windows
                self.ticker += '_'
        tic_path = self.data_path + self.ticker + ".csv"
        if os.path.exists(tic_path):
            df = pd.read_csv(tic_path)
            df = df.drop(labels='Unnamed: 0', axis=1)
            self.ticker_data = df
        if self.ticker == 'PRN': # extra check PRN is a reserved name in Windows
            self.ticker = self.ticker[:-1]
        
        # company info
        # yFinance接口异常，待数据库修复
        # self.ticker_info = yf.Ticker(self.ticker, proxy=self.proxy)
    
    def download_data(self, is_dump=True):
        if self.ticker_data is None: # 原始数据集中不存在该文件
            ticker_data = self.atomicTickerDownload(self.ticker, self.start_date, self.end_date)
            if ticker_data is not None:
                self.ticker_data = ticker_data
        else: # 原始数据集中存在该文件
            existed_ticker_data = self.ticker_data
            date_min, date_max = existed_ticker_data['Date'].min(), existed_ticker_data['Date'].max()
            head_ticker_data, tail_ticker_data = None, None

            if date_min > self.start_date: # 需要进行头部数据补足
                head_ticker_data = self.atomicTickerDownload(self.ticker, self.start_date, date_min)    
            if date_max < self.end_date: # 需要进行尾部数据补足
                tail_ticker_data = self.atomicTickerDownload(self.ticker, date_max, self.end_date)

            if head_ticker_data is None and tail_ticker_data is None:
                self.ticker_data = None
            else:
                existed_ticker_data = pd.concat([existed_ticker_data, head_ticker_data]) if head_ticker_data is not None else existed_ticker_data
                existed_ticker_data = pd.concat([existed_ticker_data, tail_ticker_data]) if tail_ticker_data is not None else existed_ticker_data
            existed_ticker_data = existed_ticker_data.drop_duplicates().sort_values(by=['Date', 'Tic']).reset_index(drop=True)
            self.tickers_data = existed_ticker_data
        
        # company info
        # yFinance接口异常，待数据库修复
        # if self.ticker_info is None:
        #     self.ticker_info = yf.Ticker(self.ticker, proxy=self.proxy)

        if is_dump and self.ticker_data is not None: # 数据是否要直接回写进文件
            if self.ticker == 'PRN': # extra check PRN is a reserved name in Windows
                self.ticker += '_'
            tic_path = self.data_path + self.ticker + ".csv"
            self.ticker_data.to_csv(tic_path)
            if self.ticker == 'PRN': # extra check PRN is a reserved name in Windows
                self.ticker = self.ticker[:-1]
    
    def atomicTickerDownload(self, ticker, start_date, end_date):
        tmptic_download = yf.download(ticker, start=start_date, end=end_date, threads=True, proxy=self.proxy)
        if tmptic_download.size == 0:
            # print("股票{} 数据读取失败".format(ticker))
            return None
        
        try:
            # 用调整后的收盘价代替原始收盘价
            # tmptic_his = tmptic_his.reset_index()
            tmptic_download = tmptic_download.reset_index(drop=False)
            tmptic_download['Close'] = tmptic_download['Adj Close']
            tmptic_download = tmptic_download.drop(labels='Adj Close', axis=1)
            tmptic_download['Tic'] = ticker
        except NotImplementedError:
            print('Downloaded data is not supported.')
        # 获取/format 时间
        tmptic_download['Day'] = tmptic_download['Date'].dt.day_of_week
        tmptic_download['Date'] = tmptic_download['Date'].apply(lambda x:x.strftime('%Y-%m-%d')) # 避免画图故障
        # 去除NaN
        tmptic_download = tmptic_download.dropna()
        # sort data
        tmptic_download = tmptic_download.sort_values(by=['Date', 'Tic']).reset_index(drop=True)

        return tmptic_download

    def calc_indicator(self, ind=['K', 'MA', 'BOLL']): # 指标计算逻辑不写入离线数据
        if 'K' in ind:
            pass # 原生数据自带olhc open/low/high/close
        if 'MA' in ind:
            self.ticker_data['MA5'] = talib.SMA(self.ticker_data['Close'], timeperiod=5)
            self.ticker_data['MA10'] = talib.SMA(self.ticker_data['Close'], timeperiod=10)
            self.ticker_data['MA20'] = talib.SMA(self.ticker_data['Close'], timeperiod=20)
            self.ticker_data['MA30'] = talib.SMA(self.ticker_data['Close'], timeperiod=30)
            self.ticker_data['MA50'] = talib.SMA(self.ticker_data['Close'], timeperiod=50)
            self.ticker_data['MA60'] = talib.SMA(self.ticker_data['Close'], timeperiod=60)
            self.ticker_data['MA120'] = talib.SMA(self.ticker_data['Close'], timeperiod=120)
            self.ticker_data['MA250'] = talib.SMA(self.ticker_data['Close'], timeperiod=250)
        if 'BOLL' in ind: # be fixed as BOLL 20 2 temporary
            PERIOD = 20
            MA_KEY = 'MA20'
            STD_KEY = 'STD20'
            DELTA = 2
            # std
            self.ticker_data[STD_KEY] = talib.STDDEV(self.ticker_data['Close'], timeperiod=PERIOD)
            # upper/lower bound
            upkey = 'BOLL_upper'
            lokey = 'BOLL_lower'
            self.ticker_data[upkey] = self.ticker_data[MA_KEY] + DELTA * self.ticker_data[STD_KEY]
            self.ticker_data[lokey] = self.ticker_data[MA_KEY] - DELTA * self.ticker_data[STD_KEY]

    def judge_strategy(self):
        # BOLL strategy judge
        sig_boll = strategy_boll(self.ticker_data)
        # SMA strategy judge
        sig_sma = strategy_sma(self.ticker_data)
        # others strategy
        # ...

        # join判断购买
        if sig_boll == sig_sma and 'buy_signal' == sig_boll:
            self.ticker_selected = 'buy_signal'
        # union判断卖出
        elif 'sold_signal' == sig_boll or 'sold_signal' == sig_sma:
            self.ticker_selected = 'sold_signal'
        else:
            pass

def ticker_info_to_json(ticker):
    # check ticker dataType
    if not isinstance(ticker, yfDataAtomic):
        print("Unavailable ticker type!")
        return None

    ans_dict = {}

    # 打印该公司的市盈率、市净率、行业、公司简介等信息
    ans_dict["股票代码"] = ticker.ticker
    # ans_dict["公司名称"] = ticker.ticker_info.info['longName']
    # ans_dict["股票价格"] = ticker.ticker_info.info['regularMarketPrice']
    # ans_dict["市盈率 P/E Ratio"] = ticker.ticker_info.info['trailingPE']
    # ans_dict["市净率 P/B Ratio"] = ticker.ticker_info.info['priceToBook']
    # ans_dict["所属行业"] = ticker.ticker_info.info['industry']
    # ans_dict["公司市值"] = ticker.ticker_info.info['marketCap']
    # ans_dict["公司简介"] = ticker.ticker_info.info['longBusinessSummary']
    # ans_dict["财报货币单位"] = ticker.ticker_info.info['financialsCurrency']
    # ans_dict["公司网站"] = ticker.ticker_info.info['website']

    return json.dumps(ans_dict)