from technicalanalysis.src.data.dataGetter import yfinanceGetter

yfClass = yfinanceGetter()

# tickers = "nvda goog"
tickers = "nvda"
yfClass.set_tickers(tickers)

period = '1mo'
interval='1h'
dict_df_history = yfClass.history(period=period, interval=interval)
# dict_financial = yfClass.financials()
# dict_financial = yfClass.news()

# import yfinance as yf
# test = yf.Ticker("nvda goog")
# financials = test.financials
# news = test.get_news()