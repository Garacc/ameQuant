import yfinance as yf
import pandas as pd
import datetime as dt
import json
import requests
import csv
import os

class YfinanceDataLoader:
    def __init__(self, data_path=None, proxy=None):
        # config
        with open('dmypy.json', 'r') as f:
            jsdata = json.load(f)
        self.data_path = jsdata['folder_path'] if data_path is None else data_path # parent_path
        self.data_path += "\\origin_data\\" # dataLoader_path
        self.proxy = jsdata['proxy'] if proxy is None else proxy
        self.__api_key = jsdata['alpha_vantage_key']

        # inner default var
        self.init_date = jsdata['init_date']
        self.end_date = dt.datetime.now() + dt.timedelta(days=1)
        self.end_date = self.end_date.strftime('%Y-%m-%d')

        # data
        self.__tickers_list = []
        self.__tickers_data = {}
        self.__failed_tickers_list = []
    
    def init_tickers_list(self):
        # 获取股票数据
        # path 1 从datahub.io中搜索数据（数据不全）
        # all_tickers = pd.read_csv('https://datahub.io/core/s-and-p-500-companies/r/constituents.csv')
        # all_tickers_symbols = all_tickers.Symbol.tolist()
        # path 2 从www.alphavantage.co中拉取股票代码
        # 设置API密钥和API地址
        api_url = f'https://www.alphavantage.co/query?function=LISTING_STATUS&apikey={self.__api_key}'

        # 发送请求并获取JSON数据
        with requests.Session() as req:
            response = req.get(api_url)
            data = response.content.decode('utf-8')
            cr = csv.reader(data.splitlines(), delimiter=',')
            cr_list = list(cr)

        df = pd.DataFrame(cr_list[1:], columns=cr_list[0])
            
        # 提取股票代码并打印
        self.__tickers_list = list(df['symbol'])
        print("股票代码：{}".format(",".join(self.__tickers_list)))
        return

    def set_tickers_list(self, tickers_list):
        self.__tickers_list = tickers_list
        return True
    
    def get_tickers_list(self):
        return self.__tickers_list

    def get_failed_tickers_list(self):
        return self.__failed_tickers_list

    def get_data(self, ticker):
        return self.__tickers_data[ticker]

    def get_ticker_info(self, ticker):
        # 通过 yfinance 获取该公司的信息
        company = yf.Ticker(ticker, proxy=self.proxy)

        # 打印该公司的市盈率、市净率、行业、公司简介等信息
        print(f"Stock symbol: {ticker}")
        print(f"Stock name: {company.info['longName']}")
        print(f"Price: {company.info['regularMarketPrice']:.2f}")
        print(f"P/E Ratio: {company.info['trailingPE']:.2f}")
        print(f"P/B Ratio: {company.info['priceToBook']:.2f}")
        print(f"Industry: {company.info['industry']}")
        print(f"Market Cap: {company.info['marketCap']:.2f}")
        print(f"Description: {company.info['longBusinessSummary']}")
        print(f"Financial reports: {company.info['financialsCurrency']}")
        print(f"Company website: {company.info['website']} \n")
        
        return

    def reload_data(self):
        success_cnt = 0
        for tic in self.__tickers_list:
            tic_path = self.data_path + tic + ".csv"
            if os.path.exists(tic_path):
                df = pd.read_csv(tic_path)
                df = df.drop(labels='Unnamed: 0', axis=1)
                self.__tickers_data[tic] = df
                if 'Date' in df.columns:
                    date_min, date_max = df['Date'].min(), df['Date'].max()
                    success_cnt += 1
                    # print("股票代码：{} 历史信息导入完成，起始日期为：{}，结束日期为：{}。".format(tic, date_min, date_max)) # 为了加快运行速度，可以省略
                else:
                    print("股票代码：{} 数据格式错误，无\'Date\'字段")
            else:
                print("股票代码：{}无历史信息，无法导入。".format(tic))
        
        print("成功导入{}支股票。".format(success_cnt))
        return
    
    def download_data(self, start_date=None, end_date=None, is_dump=False):
        # 时间处理
        if start_date is None:
            start_date = self.init_date
            print("下载起始时间为: {}".format(start_date))
        if end_date is None:
            end_date = self.end_date
            print("下载结束时间为: {}".format(end_date))
        
        success_cnt = 0
        for tic in self.__tickers_list:
            if self.__tickers_data.get(tic) is None: # 原始数据集中不存在该文件
                print("未查找到股票{}的相关数据，将全部重新下载，开始时间为：{}，结束时间为：{}".format(tic, start_date, end_date))
                ticker_data = self.atomicTickerDownload(tic, start_date, end_date)
                if ticker_data is None:
                    self.__failed_tickers_list.append(tic)
                else: 
                    self.__tickers_data[tic] = ticker_data
                    success_cnt += 1
            else: # 原始数据集中存在该文件
                existed_ticker_data = self.__tickers_data[tic]
                date_min, date_max = existed_ticker_data['Date'].min(), existed_ticker_data['Date'].max()
                head_ticker_data, tail_ticker_data = None, None

                if date_min > start_date: # 需要进行头部数据补足
                    print("股票{}将进行头部数据补足，开始时间为：{}，结束时间为：{}".format(tic, start_date, date_min))
                    head_ticker_data = self.atomicTickerDownload(tic, start_date, date_min)    
                if date_max < end_date: # 需要进行尾部数据补足
                    print("股票{}将进行尾部数据补足，开始时间为：{}，结束时间为：{}".format(tic, date_max, end_date))
                    tail_ticker_data = self.atomicTickerDownload(tic, date_max, end_date)

                if head_ticker_data is None and tail_ticker_data is None:
                    self.__failed_tickers_list.append(tic)
                else:
                    # existed_ticker_data.append(head_ticker_data) if head_ticker_data is not None else None
                    # existed_ticker_data.append(tail_ticker_data)                      existed_ticker_data = pd.concat([existed_ticker_data, head_ticker_data]) if head_ticker_data is not None else existed_ticker_data
                    existed_ticker_data = pd.concat([existed_ticker_data, tail_ticker_data]) if tail_ticker_data is not None else existed_ticker_data
                    success_cnt += 1
                existed_ticker_data = existed_ticker_data.drop_duplicates().sort_values(by=['Date', 'Tic']).reset_index(drop=True)
                self.__tickers_data[tic] = existed_ticker_data
        
        print("数据下载已完成，共计股票数：{}".format(len(self.__tickers_list)))
        print("下载成功：{}".format(success_cnt))
        print("下载失败：{}".format(len(self.__failed_tickers_list)))

        if is_dump: # 数据是否要直接回写进文件
            self.dump_data()
        return True
    
    def dump_data(self):
        success_cnt = 0
        for tic in self.__tickers_data.keys():
            data = self.__tickers_data[tic]
            if tic == 'PRN': # extra check PRN is a reserved name in Windows
                tic += '_'
            tic_path = self.data_path + tic + ".csv"
            data.to_csv(tic_path)
            success_cnt += 1
        
        print("成功导入{}支股票。".format(success_cnt))
        return

    def report_data(self, type='dict'):
        print("共计股票数：{}".format(len(self.__tickers_data.keys())))
        
        if type == 'dict': # 直接返回字典，key=tic，value=tic_data_df
            return self.__tickers_data
        elif type == 'list': # 不同股票不合并为同一个dataFrame，而是放在一个list里
            return self.__tickers_data.values()
        elif type == 'df': # 不同股票合并为同一个dataFrame
            data_df = pd.DataFrame()
            for tic in self.__tickers_data.values():
                data_df.append(tic)
            return data_df.sort_values(by=['Date', 'Tic']).reset_index(drop=True)
        else:
            raise TypeError('Invalid report type.')

    def release_data(self):
        self.__tickers_list = []
        self.__tickers_data = {}
        self.__failed_tickers_list = []

    def atomicTickerDownload(self, ticker, start_date, end_date):
        tmptic_download = yf.download(ticker, start=start_date, end=end_date, threads=True, proxy=self.proxy)
        if tmptic_download.size == 0:
            print("股票{} 数据读取失败".format(ticker))
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
        print("数据处理，tickers={}".format(ticker))
        # print(tmptic_download.head(5))
        print("数据规模：{}".format(tmptic_download.shape))

        return tmptic_download


if __name__ == "__main__":
    proxy = '127.0.0.1:21882'

    yfd = YfinanceDataLoader(proxy=proxy)
    yfd.init_tickers_list()
    yfd.reload_data()
    yfd.download_data(is_dump=True)
