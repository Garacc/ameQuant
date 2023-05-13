import yfinance as yf
import streamlit as st
from yfDataPrepare import *
from yfInfoPlot import *
from enum import Enum
import time

# 数据准备
# @st.cache_data(experimental_allow_widgets=True) # 只执行一遍
def data_prepare(data_path=None, proxy=None, start_date=None):
    st.title("DATE_PREPARE STATE")

    # session_state 数据存储初始化
    if 'ticker_buys' not in st.session_state and 'ticker_sells' not in st.session_state:
        st.session_state['ticker_buys'] = []
        st.session_state['ticker_sells'] = []
        st.session_state['final_ticker_buys'] = set()
        st.session_state['final_ticker_sells'] = set()
    
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
    # ticker_list = ['AAPL', 'TSLA', 'NVDA', 'COIN', 'NFLX', 'GOOGL', 'META', 'EDU', 'BABA', 'PDD'] # for debug
    # ticker_list = ["A","AA","AAA","AAAU","AAC","AAC-U","AAC-WS","AACG","AACI","AACIU","AACIW","AACT-U","AADI","AADR","AAIC","AAIC-P-B","AAIC-P-C","AAIN","AAL","AAMC","AAME","AAN","AAOI","AAON","AAP","AAPB","AAPD","AAPL","AAPU","AAT","AAU","AAXJ","AB","ABB","ABBV","ABC","ABCB","ABCL","ABCM","ABEO","ABEQ","ABEV","ABG","ABIO","ABM","ABNB","ABOS","ABR","ABR-P-D","ABR-P-E","ABR-P-F","ABSI","ABST","ABT","ABUS","ABVC","AC","ACA","ACAB","ACABU","ACABW","ACAC","ACACU","ACACW","ACAD","ACAH","ACAHU","ACAHW","ACAQ","ACAQ-U","ACAQ-WS","ACAX","ACAXR","ACAXU","ACAXW","ACB","ACBA","ACBAU","ACBAW","ACCD","ACCO","ACDC","ACDCW","ACEL","ACER","ACES","ACET","ACGL","ACGLN","ACGLO","ACGN","ACHC","ACHL","ACHR","ACHV","ACI","ACIO","ACIU","ACIW","ACLS","ACLX","ACM","ACMR","ACN","ACNB","ACNT","ACON","ACONW","ACOR","ACP","ACP-P-A","ACR","ACR-P-C","ACR-P-D","ACRE","ACRO","ACRO-U","ACRO-WS","ACRS","ACRV","ACRX","ACSI","ACST","ACT","ACTG","ACTV","ACU","ACV","ACVA","ACVF","ACWI","ACWV","ACWX","ACXP","ADAG","ADAL","ADALU","ADALW","ADAP","ADBE","ADC","ADC-P-A","ADCT","ADD","ADEA","ADER","ADERU","ADERW","ADES","ADEX","ADEX-U","ADEX-WS","ADFI","ADI","ADIL","ADILW","ADIV","ADM","ADMA","ADME","ADMP","ADN","ADNT","ADNWW","ADOC","ADOCR","ADOCW","ADP","ADPT","ADPV","ADRT","ADRT-U","ADSE","ADSEW","ADSK","ADT","ADTH","ADTHW","ADTN","ADTX","ADUS","ADV","ADVM","ADX","ADXN","AE","AEAE","AEAEU","AEAEW","AEE","AEF","AEFC","AEG","AEHA","AEHL","AEHR","AEI","AEIS","AEL","AEL-P-A","AEL-P-B","AEM","AEMB","AEMD","AENZ","AEO","AEP","AEPPZ","AER","AES","AESC","AESI","AESR","AEVA","AEVA-WS","AEY","AEYE","AEZS","AFAR","AFARU","AFARW","AFB","AFBI","AFCG","AFG","AFGB","AFGC","AFGD","AFGE","AFIB","AFIF","AFK","AFL","AFLG","AFMC","AFMD","AFRI","AFRIW","AFRM","AFSM","AFT","AFTR","AFTR-U","AFTR-WS","AFTY","AFYA","AG","AGAC","AGAC-U","AGAE","AGBA","AGBAW","AGCO","AGD","AGE","AGEN","AGFS","AGFY","AGG","AGGH","AGGY","AGI","AGIH","AGIL","AGILW","AGIO","AGL","AGLE","AGM","AGM-A","AGM-P-C","AGM-P-D","AGM-P-E","AGM-P-F","AGM-P-G","AGMH","AGNC","AGNCL","AGNCM","AGNCN","AGNCO","AGNCP","AGNG","AGO","AGOV","AGOX","AGQ","AGR","AGRH","AGRI","AGRIW","AGRO","AGRX","AGS","AGTC","AGTI","AGX","AGYS","AGZ","AGZD","AHCO","AHG","AHH","AHH-P-A","AHI","AHL-P-C","AHL-P-D","AHL-P-E","AHOY","AHRN","AHRNU","AHRNW","AHT","AHT-P-D","AHT-P-F","AHT-P-G","AHT-P-H","AHT-P-I","AHYB","AI","AIA","AIB","AIBBR","AIBBU","AIC","AIEQ","AIF","AIG","AIG-P-A","AIH","AIHS","AILG","AILV","AIM","AIMAU","AIMAW","AIMBU","AIMD","AIMDW","AIN","AINC","AIO","AIP","AIQ","AIR","AIRC","AIRG","AIRI","AIRR","AIRS","AIRT","AIRTP","AIT","AIU","AIV","AIVI","AIVL","AIXI","AIZ","AIZN","AJG","AJRD","AJX","AJXA","AKA","AKAM","AKAN","AKBA","AKLI","AKO-A","AKO-B","AKR","AKRO","AKTS","AKTX","AKU","AKUS","AKYA","AL","AL-P-A","ALAR","ALB","ALBT","ALC","ALCC","ALCO","ALCYU","ALDX","ALE","ALEC","ALEX","ALG","ALGM","ALGN","ALGS","ALGT","ALHC","ALIM","ALIT","ALK","ALKS","ALKT","ALL","ALL-P-B","ALL-P-H","ALL-P-I","ALLE","ALLG","ALLG-WS","ALLK","ALLO","ALLR","ALLT","ALLY","ALNY","ALOR","ALORU","ALORW","ALOT","ALPA","ALPAU","ALPAW","ALPN","ALPP","ALPS","ALRM","ALRN","ALRS","ALSA","ALSAR","ALSAU","ALSAW","ALSN","ALT","ALTG","ALTG-P-A","ALTI","ALTIW","ALTL","ALTO","ALTR","ALTU","ALTUU","ALTUW","ALTY","ALV","ALVO","ALVOW","ALVR","ALX","ALXO","ALYA","ALZN","AM","AMAL","AMAM","AMAO","AMAOU","AMAOW","AMAT","AMAX","AMBA","AMBC","AMBI","AMBI-WS","AMBO","AMBP","AMBP-WS","AMC","AMCR","AMCX","AMD","AME","AMED","AMEH","AMG","AMGN","AMH","AMH-P-G","AMH-P-H","AMID","AMJ","AMK","AMKR","AMLI","AMLP","AMLX","AMN","AMNA","AMNB","AMND","AMOM","AMOT","AMP","AMPE","AMPG","AMPGW","AMPH","AMPL","AMPS","AMPX","AMPX-WS","AMPY","AMR","AMRC","AMRK","AMRN","AMRS","AMRX","AMS","AMSC","AMSF","AMST","AMSWA","AMT","AMTB","AMTD","AMTI","AMTR","AMTX","AMUB","AMV","AMWD","AMWL","AMX","AMZA","AMZD","AMZN","AMZU","AN","ANAB","ANDE","ANEB","ANET","ANEW","ANF","ANGH","ANGHW","ANGI","ANGL","ANGN","ANGO","ANIK","ANIP","ANIX","ANNX","ANPC","ANSS","ANTE","ANTX","ANVS","ANY","ANZU","ANZUU","ANZUW","AOA","AOD","AOGO","AOGOW","AOK","AOM","AOMR","AON","AOR","AORT","AOS","AOSL","AOTG","AOUT","AP","AP-WS","APA","APAC","APACU","APACW","APAM","APCA","APCA-U","APCA-WS","APCB","APCX","APCXW","APD","APDN","APE","APEI","APG","APGB","APGB-U","APGB-WS","APGN","APGNW","APH","API","APIE","APLD","APLE","APLM","APLMW","APLS","APLT","APLY","APM","APMI","APMIU","APMIW","APMU","APO","APOG","APP","APPF","APPH","APPHW","APPN","APPS","APRD","APRE","APRH","APRJ","APRN","APRQ","APRT","APRW","APRZ","APT","APTM","APTMU","APTMW","APTO","APTV","APTV-P-A","APTX","APUE","APVO","APWC","APXI","APXIU","APXIW","APYX","AQB","AQMS","AQN","AQNA","AQNB","AQNU","AQST","AQU","AQUA","AQUNR","AQUNU","AQWA","AR","ARAV","ARAY","ARB","ARBB","ARBE","ARBEW","ARBG","ARBGU","ARBGW","ARBK","ARBKL","ARC","ARCB","ARCC","ARCE","ARCH","ARCK","ARCKU","ARCKW","ARCM","ARCO","ARCT","ARDC","ARDS","ARDX","ARE","AREB","AREBW","AREC","AREN","ARES","ARGD","ARGO","ARGO-P-A","ARGT","ARGU","ARGUU","ARGUW","ARGX","ARHS","ARI","ARIS","ARIZ","ARIZR","ARIZU","ARIZW","ARKF","ARKG","ARKK","ARKO","ARKQ","ARKR","ARKW","ARKX","ARL","ARLO","ARLP","ARMK","ARMP","ARMR","ARNC","AROC","AROW","ARP","ARQQ","ARQQW","ARQT","ARR","ARR-P-C","ARRW","ARRWU","ARRWW","ARRY","ARTE","ARTEU","ARTEW","ARTL","ARTLW","ARTNA","ARTW","ARVL","ARVN","ARVR","ARW","ARWR","ARYD","ARYE","ASA","ASAI","ASAN","ASAP","ASB","ASB-P-E","ASB-P-F","ASBA","ASC","ASCA","ASCAR","ASCAU","ASCAW","ASCB","ASCBR","ASCBU","ASCBW","ASEA","ASET","ASG","ASGI","ASGN","ASH","ASHR","ASHS","ASHX","ASIX","ASLE","ASLN","ASM","ASMB","ASML","ASND","ASNS","ASO","ASPA","ASPAU","ASPAW","ASPI","ASPN","ASPS","ASPY","ASR","ASRT","ASRV","ASST","ASTC","ASTE","ASTI","ASTL","ASTLW","ASTR","ASTS","ASTSW","ASUR","ASX","ASXC","ASYS","ATAI","ATAK","ATAKR","ATAKU","ATAKW","ATAQ","ATAQ-U","ATAT","ATCO-P-D","ATCO-P-H","ATCO-P-I","ATCOL","ATEC","ATEK","ATEK-U","ATEK-WS","ATEN","ATER","ATEST-A","ATEST-B","ATEST-C","ATEST-G","ATEST-H","ATEST-L","ATEX","ATFV","ATGE","ATH-P-A","ATH-P-C","ATH-P-D","ATH-P-E","ATHA","ATHE","ATHM","ATHX","ATI","ATIF","ATIP","ATKR","ATLC","ATLCL","ATLCP","ATLO","ATMC","ATMCR","ATMCU","ATMCW","ATMP","ATMV","ATMVR","ATMVU","ATNF","ATNFW","ATNI","ATNM","ATNX","ATO","ATOM","ATOS","ATR","ATRA","ATRC","ATRI","ATRO","ATSG","ATTO","ATUS","ATVI","ATXG","ATXI","ATXS","AU","AUB","AUB-P-A","AUBN","AUD","AUDC","AUGX","AUGZ","AUID","AULT","AULT-P-D","AUMN","AUPH","AUR","AURA","AURC","AURCU","AURCW","AUROW","AUSF","AUST","AUTL","AUUD","AUUDW","AUVI","AUVIP","AVA","AVAC","AVACU","AVACW","AVAH","AVAL","AVAV","AVB","AVD","AVDE","AVDL","AVDV","AVDX","AVEM","AVES","AVGE","AVGO","AVGR","AVHI","AVHIU","AVHIW","AVID","AVIE","AVIG","AVIR","AVIV","AVK","AVLV","AVMU","AVNS","AVNT","AVNW","AVO","AVPT","AVPTW","AVRE","AVRO","AVSC","AVSD","AVSE","AVSF","AVSU","AVT","AVTA","AVTE","AVTR","AVTX","AVUS","AVUV","AVXL","AVY","AWAY","AWEG","AWF","AWH","AWI","AWIN","AWINW","AWK","AWP","AWR","AWRE","AWX","AX","AXAC","AXAC-R","AXAC-WS","AXDX","AXGN","AXL","AXLA","AXNX","AXON","AXP","AXR","AXS","AXS-P-E","AXSM","AXTA","AXTI","AY","AYI","AYRO","AYTU","AYX","AZ","AZEK","AZN","AZO","AZPN","AZRE","AZTA","AZTD","AZUL","AZYO","AZZ","B","BA","BAB","BABA","BABX","BAC"]
    total_ticker_size = len(ticker_list)
    st.write("共计股票数为：{}".format(total_ticker_size))

    st.write("数据准备中，请稍后")
    # Add placeholders
    prepare_iter = st.empty()
    prepare_bar = st.progress(0)
    prepare_info = st.empty()

    for i, symbol in enumerate(ticker_list):
        prepare_iter.write("Ticker {}, Symbol {}".format(i + 1, symbol))
        prepare_bar.progress((i + 1) / total_ticker_size)
        yfd = yfDataAtomic(symbol, data_path, proxy, start_date, end_date)
        yfd.reload_data()
        yfd.download_data()
        if yfd.ticker_data is None:
            prepare_info.write("Ticker {} is inavailable.".format(symbol))
            continue
        yfd.calc_indicator()
        yfd.judge_strategy()
        if yfd.ticker_selected == 'buy_signal':
            st.session_state.ticker_buys.append(yfd)
        elif yfd.ticker_selected == 'sold_signal':
            st.session_state.ticker_sells.append(yfd)
    
    st.write("数据准备完成，请点击按键继续。")
    st.button("请点击继续", on_click=state_change)


# 信息绘图
def info_plot():
    st.title("INFO_PLOT STATE")
    st.write("绘图阶段共计考虑{}支股票".format(len(st.session_state.ticker_buys)))
    
    # session_state 画图序列状态初始化
    if 'plot_idx' not in st.session_state:
        st.session_state.plot_idx = 0

    plot_tag = st.empty()
    plot_bar = st.progress(0)
    plot_info = st.empty()
    plot_fig = st.empty()

    column = st.empty()
    _, col1, _, col2, _ = column.columns(5)
    with col1:
        if st.button("保留"):
            st.session_state.final_ticker_buys.add(st.session_state.ticker_buys[st.session_state.plot_idx]) 
            st.session_state.plot_idx += 1 # 股票idx自增
    with col2:
        if st.button("放弃"):
            st.session_state.plot_idx += 1 # 股票idx自增    

    if st.session_state.plot_idx < len(st.session_state.ticker_buys):
        cur_ticker = st.session_state.ticker_buys[st.session_state.plot_idx]

        plot_tag.write("股票{}触发买入信号，请关注".format(cur_ticker.ticker))
        plot_bar.progress((st.session_state.plot_idx + 1) / len(st.session_state.ticker_buys), text="第{}支候选股票".format(st.session_state.plot_idx + 1))

        plot_info.json(ticker_info_to_json(cur_ticker))
        PERIOD = 60
        ax, fig = st_info_plot(cur_ticker, period=PERIOD)
        plot_fig.pyplot(fig)
    else:
        column.empty()
        st.write("信息绘图完成，请点击按键继续。")
        st.button("请点击继续", on_click=state_change)


# 结果展示
def final_present():
    st.title('FINAL_PRESENT STATE')
    st.session_state.final_ticker_sells = st.session_state.ticker_sells
    ticker_buys_symbol = [ticker.ticker for ticker in st.session_state.final_ticker_buys]
    ticker_sells_symbol = [ticker.ticker for ticker in st.session_state.final_ticker_sells]
    st.write("最终选定的观测买点股票为")
    st.write(",".join(ticker_buys_symbol))
    st.write("最终选定的观测卖点股票为")
    st.write(",".join(ticker_sells_symbol))
    st.write("请根据选择操作，选择完成后请关闭本程序，感谢使用。")


def state_change():
    if st.session_state.flow_state == "DATA_PREPARE":
        st.session_state.flow_state = "INFO_PLOT"
    elif st.session_state.flow_state == "INFO_PLOT":
        st.session_state.flow_state = "FINAL_PRESENT"
    else:
        pass


def save_ticker_and_add(ticker):
    st.session_state.final_ticker_buys.add(ticker) 
    st.session_state.plot_idx += 1 # 股票idx自增


def drop_ticker_and_add():
    st.session_state.plot_idx += 1 # 股票idx自增


def main():
    st.title("ameQuant Streamlit v1.0")
    # session_state 状态初始化
    # 将状态用Enum类标记时，会出现判断异常，待确认原因
    if 'flow_state' not in st.session_state:
        st.session_state.flow_state = "DATA_PREPARE"

    # data prepare
    if st.session_state.flow_state == "DATA_PREPARE":
        data_prepare()

    # info plot
    elif st.session_state.flow_state == "INFO_PLOT":
        info_plot()
        
    
    # final present
    elif st.session_state.flow_state == "FINAL_PRESENT":
        final_present()
    
    else:
        st.write('INVALID END')


if __name__ == "__main__":
    main()