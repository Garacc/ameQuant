import yfinance as yf
import streamlit as st
from yfDataPrepare import *
from enum import Enum

# state definition
class State(Enum):
    DATA_PREPARE = 1
    INFO_PLOT = 2
    FINAL_PRESENT = 3


# session_state 状态初始化
if 'flow_state' not in st.session_state:
    st.session_state.flow_state = State.DATA_PREPARE


# 数据准备
@st.cache # 只执行一遍
def data_prepare(data_path=None, proxy=None, start_date=None):
    data_prepare_container = st.container()
    data_prepare_container.title("DATE_PREPARE STATE")

    # session_state 数据存储初始化
    if 'ticker_lists' not in st.session_state:
        st.session_state.ticker_lists = []
        st.session_state.final_ticker_buys = []
        st.session_state.final_ticker_sells = []

    # config
    with open('dmypy.json', 'r') as f:
        jsdata = json.load(f)
    data_path = jsdata['folder_path'] if data_path is None else data_path # parent_path
    data_path += "\\origin_data\\" # dataLoader_path
    proxy = jsdata['proxy'] if proxy is None else proxy
    __api_key = jsdata['alpha_vantage_key']

    # time modify
    start_date = jsdata['init_date'] if start_date is None else start_date
    end_date = dt.datetime.now() + dt.timedelta(days=1)
    end_date = end_date.strftime('%Y-%m-%d')
    
    ticker_list = init_tickers_list(__api_key)
    total_ticker_size = len(ticker_list)

    data_prepare_container.write("数据准备中，请稍后")
    # Add placeholders
    prepare_iter = st.empty()
    prepare_info = st.empty()
    prepare_bar = st.process()


    for i, symbol in enumerate(ticker_list):
        prepare_iter.write("Ticker {}, Symbol {}".format(i, symbol))
        prepare_bar.process((i + 1) / total_ticker_size)
        yfd = yfDataAtomic(symbol, data_path, proxy, start_date, end_date)
        yfd.reload_data()
        yfd.download_data()
        if yfd.ticker_data is None:
            prepare_info.write("Ticker {} is inavailable.".format(symbol))
            continue
        yfd.calc_indicator()
        yfd.judge_strategy()
        if yfd.ticker_selected is not None:
            st.session_state.ticker_lists.append(yfd)
    
    st.write("数据准备完成，请点击按键继续。")
    if st.button("请点击继续"):
        st.session_state.flow_state = State.INFO_PLOT


# 信息绘图
def info_plot():
    st.title("INFO_PLOT STATE")
    # session_state 画图序列状态初始化
    if 'plot_idx' not in st.session_state:
        st.session_state.plot_idx = 0

    if st.session_state.plot_idx < len(st.session_state.ticker_lists):
        st.write("当前为第{}支候选的股票".format(st.session_state.plot_idx + 1))

        cur_ticker = st.session_state.ticker_lists[st.session_state.plot_idx]
            
        if cur_ticker.ticker_selected == 'sold_signal':
            st.session_state.final_ticker_sells.append()
        else:
            # tickers_info[ele].st_plot_data(indicators=['K', 'BOLL', 'MA'], period=60)
            st.json(ticker_info_to_json(cur_ticker))
            if st.button("保留该股票"):
                st.session_state.final_ticker_buys.append(cur_ticker)
                st.session_state.plot_idx += 1 # 股票idx自增
            elif st.button("放弃该股票"):
                st.session_state.plot_idx += 1 # 股票idx自增
            else:
                raise RuntimeError
        pass
    else:
        st.write("信息绘图完成，请点击按键继续。")
        if st.button("请点击继续"):
            st.session_state.flow_state = State.FINAL_PRESENT


# 结果展示
def final_present():
    st.title('FINAL_PRESENT STATE')
    ticker_buys_symbol = [ticker.ticker for ticker in st.session_state.final_ticker_buys]
    ticker_sells_symbol = [ticker.ticker for ticker in st.session_state.final_ticker_sells]
    st.write("最终选定的观测买点股票为")
    st.write(",".join(ticker_buys_symbol))
    st.write("最终选定的观测卖点股票为")
    st.write(",".join(ticker_sells_symbol))
    st.write("请根据选择操作，选择完成后请关闭本程序，感谢使用。")
    pass


def main():
    st.title("ameQuant Streamlit v1.0")

    # data prepare
    if st.session_state.flow_state == State.DATA_PREPARE:
        data_prepare()

    # info plot
    if st.session_state.flow_state == State.INFO_PLOT:
        info_plot()
    
    # final present
    if st.session_state.flow_state == State.FINAL_PRESENT:
        final_present()


if __name__ == "__main__":
    main()