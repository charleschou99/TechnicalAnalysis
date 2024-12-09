"""
Data Getter from providers
"""

import pandas as pd

##############################################################
##############################################################
##############################################################
import yfinance as yf
class yfinanceGetter:
    """
    Provider: Yahoo Finance
    Functions: -
    """
    def set_tickers(
            self,
            tickers:str=None
    ):
        """
        :param tickers: string of ticker, seperate by space if multiple tickers
        """
        if tickers is None:
            raise ValueError("tickers has not been communicated")

        if not isinstance(tickers, str):
            raise TypeError(f"tickers expeted type: Str, got: {type(tickers)}")

        else:
            if len(tickers.split()) == 1:
                self._tickers = yf.Ticker(tickers)
                self.list_tickers = [self._tickers]
            else:
                self._tickers = yf.Tickers(tickers)
                self.list_tickers = [yf.Ticker(t) for t in tickers.split()]

    def history(
            self,
            tickers:str=None,
            period:str=None,
            interval:str=None,
            start:str=None,
            end:str=None,
            prepost:bool=False,
            actions:bool=True,
            auto_adjust:bool=True,
            back_adjust:bool=False,
            proxy:str=None,
            rounding:bool=False,
            # tz:str=None,
            # timeout:str=None,
                ):
        """
        :Parameters:
            period : str
                Valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
                Either Use period parameter or use start and end
            interval : str
                Valid intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
                Intraday data cannot extend last 60 days
            start: str
                Download start date string (YYYY-MM-DD) or _datetime.
                Default is 1900-01-01
            end: str
                Download end date string (YYYY-MM-DD) or _datetime.
                Default is now
            prepost : bool
                Include Pre and Post market data in results?
                Default is False
            auto_adjust: bool
                Adjust all OHLC automatically? Default is True
            back_adjust: bool
                Back-adjusted data to mimic true historical prices
            proxy: str
                Optional. Proxy server URL scheme. Default is None
            rounding: bool
                Round values to 2 decimal places?
                Optional. Default is False = precision suggested by Yahoo!
        """
        if tickers is not None:
            self.set_tickers(tickers)

        if interval is None:
            raise ValueError(f"Please specify interval")

        try:
            dict_df_history = {}

            if period is None:
                for ticker in self.list_tickers:
                    dict_df_history[ticker.ticker] = ticker.history(
                            interval=interval,
                            start=start,
                            end=end,
                            prepost=prepost,
                            actions=actions,
                            auto_adjust=auto_adjust,
                            back_adjust=back_adjust,
                            proxy=proxy,
                            rounding=rounding,
                        )

            else:
                for ticker in self.list_tickers:
                     dict_df_history[ticker.ticker] = ticker.history(
                        interval=interval,
                        period=period,
                        prepost=prepost,
                        actions=actions,
                        auto_adjust=auto_adjust,
                        back_adjust=back_adjust,
                        proxy=proxy,
                        rounding=rounding,
                    )
            return dict_df_history

        except Exception as e:
            raise Exception(f"Fail to retrieve history with following error:{e}")

    def financials(self):
        """
        Get financials of each company
        """
        try:
            dict_df_financials = {}

            for stock in self.list_tickers:
                df_financials = stock.financials
                dict_df_financials[stock.ticker] = df_financials

            return dict_df_financials

        except Exception as e:
            raise Exception(f"Fail to retrieve financials with following error:{e}")

    def news(self):
        """
        Get news of each company
        """
        try:
            dict_news = {}

            for stock in self.list_tickers:
                dict_n = stock.get_news()
                dict_news[stock.ticker] = dict_n

            return dict_news

        except Exception as e:
            raise Exception(f"Fail to retrieve news with following error:{e}")

    def __repr__(self):
        return "Yahoo Finance getter service"