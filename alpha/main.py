from alpha.yfDataLoader import *
from alpha.yfTickerInfo import *
from alpha.yfStrategy import *
import yfinance as yf

def main():
    # 构建dataLoader
    yfd = YfinanceDataLoader()
    yfd.release_data()
    # # 指定特定股票
    # candidate_tickers = ['AAPL', 'TSLA', 'NVDA', 'COIN', 'NFLX', 'GOOGL', 'META', 'EDU', 'BABA', 'PDD']
    # yfd.set_tickers_list(candidate_tickers)
    # 初始化所有股票
    yfd.init_tickers_list()

    # 加载数据
    yfd.reload_data()

    # 下载并落盘
    # yfd.download_data(is_dump=True)

    # 导出并释放
    tickers = yfd.report_data()
    yfd.release_data()

    # 将dataLoader的数据导入tickerInfo，用以做进一步分析
    tickers_info = {}
    for tic in tickers.keys():
        tickers_info[tic] = YfinanceTickerInfo(ticker=tic, data_frame=tickers[tic])
    print(tickers_info.keys())

    # stratey boll
    boll_buy_tickers = []
    boll_sold_tickers = []
    for tic in tickers_info.keys():
        tickers_info[tic].get_BOLL(period=20, delta=2)
        if strategy_boll(tickers_info[tic].get_indicators()) == 'buy_signal':
            boll_buy_tickers.append(tic)
        elif strategy_boll(tickers_info[tic].get_indicators()) == 'sold_signal':
            boll_sold_tickers.append(tic)
        else:
            pass

    # strategy sma
    sma_buy_tickers = []
    sma_sold_tickers = []
    for tic in tickers_info.keys():
        if strategy_sma(tickers_info[tic].get_indicators()) == 'buy_signal':
            sma_buy_tickers.append(tic)
        elif strategy_sma(tickers_info[tic].get_indicators()) == 'sold_signal':
            sma_sold_tickers.append(tic)
        else:
            pass

    joint_buy_tickers = []
    joint_sold_tickers = []
    for ele in boll_buy_tickers:
        if ele in sma_buy_tickers:
            joint_buy_tickers.append(ele)
    for ele in boll_sold_tickers:
        if ele in sma_sold_tickers:
            joint_sold_tickers.append(ele)

    final_buy_tickers = []
    for idx, ele in enumerate(joint_buy_tickers):
        print("当前为候选的第{}支股票".format(idx))
        yfd.get_ticker_info(ele)
        tickers_info[ele].plot_data(indicators=['K', 'BOLL', 'MA'], period=60)

        inp = input("请选择是否保留") # for pause
        if inp in ('Y', 'y', 'yes', '1'):
            final_buy_tickers.append(ele)
        else:
            pass
    
    print("选定观测买点股票为 {}".format(",".join(final_buy_tickers)))
    print("选定观测卖点股票为 {}".format(",".join(joint_sold_tickers)))


if __name__ == "__main__":
    main()