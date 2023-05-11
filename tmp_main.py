import yfinance as yf
import time


aapl = yf.Ticker('AAPL')

aapl.get_info('127.0.0.1:21882')
# aapl.get_info()

# with open('yahoo-keys.txt', 'r') as f:


print('1')