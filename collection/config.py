from urllib.request import build_opener, HTTPCookieProcessor
from http.cookiejar import CookieJar


class CONFIG:
    HISTORICAL_DATA_WEEK_URL = "https://www1.nseindia.com/live_market/dynaContent/live_watch/get_quote/" \
                               "getHistoricalData.jsp?" \
                               "symbol=STOCK_SYMBOL&series=EQ&fromDate=undefined&toDate=undefined&datePeriod=week"

    HISTORICAL_DATA_DATE_TO_DATE_URL = "https://www1.nseindia.com/live_market/dynaContent/live_watch/get_quote/" \
                                       "getHistoricalData.jsp?" \
                                       "symbol=STOCK_SYMBOL&series=EQ&fromDate=FROM_DATE&toDate=TO_DATE"

    SCREENER_URL = "https://www.screener.in/company/STOCK_SYMBOL/consolidated/#balance-sheet"

    HEADERS = {'Accept': '*/*',
               'Accept-Language': 'en-US,en;q=0.5',
               'Host': 'www1.nseindia.com',
               'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:28.0) Gecko/20100101 Firefox/28.0',
               'X-Requested-With': 'XMLHttpRequest'
               }

    OPENER = build_opener(HTTPCookieProcessor(CookieJar()))

    MONGO_URI = "mongodb://localhost:27017"
    SCREENER_PRICE_URL = "https://www.screener.in/api/company/COMPANY_SCREENER_ID/chart/" \
                         "?q=Price-DMA50-DMA200-Volume&days=365&consolidated=true"
