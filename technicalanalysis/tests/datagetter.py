from technicalanalysis.src.data.dataGetter import yfinanceGetter

yfClass = yfinanceGetter()

tickers = "nvda goog"
yfClass.set_tickers(tickers)

period = '1mo'
interval='1h'
df = yfClass.history(period=period, interval=interval)

