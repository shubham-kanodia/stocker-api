import pickle
import datetime
import requests
from time import sleep
from bs4 import BeautifulSoup
from collection.dao import DAO
from urllib.request import Request
from collection.config import CONFIG
from nsetools.utils import byte_adaptor

from tqdm import tqdm


class Crawler:

    @staticmethod
    def crawl_weekly_price_history_html(stock_symbol):
        url = CONFIG.HISTORICAL_DATA_WEEK_URL.replace("STOCK_SYMBOL", stock_symbol)
        req = Request(url, None, CONFIG.HEADERS)

        resp = CONFIG.OPENER.open(req)
        resp = byte_adaptor(resp)

        return resp.read()

    @staticmethod
    def crawl_date_to_date_history(stock_symbol, from_date, to_date):
        url = CONFIG.HISTORICAL_DATA_DATE_TO_DATE_URL \
            .replace("STOCK_SYMBOL", stock_symbol) \
            .replace("FROM_DATE", from_date) \
            .replace("TO_DATE", to_date)
        req = Request(url, None, CONFIG.HEADERS)

        resp = CONFIG.OPENER.open(req)
        return resp.read()

    @staticmethod
    def crawl_financial_data(stock_symbol):
        url = CONFIG.SCREENER_URL.replace("STOCK_SYMBOL", stock_symbol)
        page = requests.get(url)
        return page


class Parser:

    @staticmethod
    def parse_price_table(resp):
        """
        ['Date', 'Symbol', 'Series', 'Open Price', 'High Price', 'Low Price',
        'Last Traded Price ', 'Close Price', 'Total Traded Quantity', 'Turnover (in Lakhs)']
        """
        data = {}
        from lxml import etree
        table = etree.HTML(resp).find("body/table/tbody")
        rows = iter(table)
        headers = [col.text for col in next(rows)]
        for row in rows:
            values = [col.text for col in row]
            data[values[0]] = {
                "close_price": values[7],
                "low_price": values[5],
                "high_price": values[4],
                "open_price": values[3]
            }
        return data

    @staticmethod
    def parse_balance_sheet_data(document):
        """
        Row 1 -> Time published (Annual)
        Row 2 -> Share Capital
        Row 3 -> Reserves
        Row 4 -> Borrowings
        Row 5 -> Other Liabilities
        Row 6 -> Total Liabilities
        Row 7 -> Fixed Assets
        Row 8 -> CWIP
        Row 9 -> Investments
        Row 10 -> Other Assets
        Row 11 -> Total Assets
        """

        soup = BeautifulSoup(document.content, 'html.parser')
        balance_sheet_table = soup.find(id="balance-sheet").find('table')

        lst = [
            [Fetcher.clean_string(cell.string) for cell in balance_sheet_table.find_all("tr")[0].find_all("th")[1:]]
        ]

        for row in balance_sheet_table.find_all("tr")[1:]:
            cells = row.find_all("td")
            lst.append(
                [Fetcher.clean_string(cell.string).replace(",", "") for cell in cells[1:]]
            )
        return lst

    @staticmethod
    def parse_income_statement(document):
        """
        Row 1 -> Time published (Annual)
        Row 2 -> sales
        Row 3 -> expenses
        Row 4 -> operating_profit
        Row 5 -> opm_percentage
        Row 6 -> other_income
        Row 7 -> interest
        Row 8 -> depreciation
        Row 9 -> profit_before_tax
        Row 10 -> tax_percentage
        Row 11 -> net_profit
        Row 12 -> eps_in_rs
        Row 13 -> dividend_payout
        """

        soup = BeautifulSoup(document.content, 'html.parser')
        income_statement_table = soup.find(id="profit-loss").find('table')

        lst = [
            [Fetcher.clean_string(cell.string) for cell in income_statement_table.find_all("tr")[0].find_all("th")[1:-1]]
        ]

        for row in income_statement_table.find_all("tr")[1:]:
            cells = row.find_all("td")
            lst.append(
                [None if not cell.string else Fetcher.clean_string(cell.string).replace(",", "") for cell in cells[1:-1]]
            )
        return lst

    @staticmethod
    def parse_quarterly_income_statement(document):
        """
        Row 1 -> Time published (Annual)
        Row 2 -> sales
        Row 3 -> expenses
        Row 4 -> operating_profit
        Row 5 -> opm_percentage
        Row 6 -> other_income
        Row 7 -> interest
        Row 8 -> depreciation
        Row 9 -> profit_before_tax
        Row 10 -> tax_percentage
        Row 11 -> net_profit
        Row 12 -> eps_in_rs
        Row 13 -> dividend_payout
        """

        soup = BeautifulSoup(document.content, 'html.parser')
        income_statement_table = soup.find(id="quarters").find('table')

        lst = [
            [Fetcher.clean_string(cell.string) for cell in income_statement_table.find_all("tr")[0].find_all("th")[1:]]
        ]

        for row in income_statement_table.find_all("tr")[1:]:
            cells = row.find_all("td")
            lst.append(
                [None if not cell.string else Fetcher.clean_string(cell.string).replace(",", "") for cell in cells[1:]]
            )
        return lst

    @staticmethod
    def parse_sector(document):
        soup = BeautifulSoup(document.content, 'html.parser')
        sector = soup \
            .find(id="peers") \
            .find("small", class_="sub") \
            .find("a").string.strip()
        return sector

    @staticmethod
    def parse_screener_id(document):
        soup = BeautifulSoup(document.content, 'html.parser')
        id = soup.find(id="company-info").attrs["data-company-id"]
        return id


class Fetcher:
    """Wrapper Class for using crawler and fetcher classes"""

    @staticmethod
    def fetch_weekly_data(stock_symbol):
        resp = Crawler.crawl_weekly_price_history_html(stock_symbol)
        data = Parser.parse_price_table(resp)
        return data

    @staticmethod
    def export_weekly_data(stock_symbol, exporter):
        data = Fetcher.fetch_weekly_data(stock_symbol)
        exporter.add_data(stock_symbol, data)

    @staticmethod
    def fetch_last_five_years_data(stock_symbol):
        to_date = datetime.date.today().strftime('%d-%m-%Y')
        split_date = to_date.split("-")
        from_date = "-".join([split_date[0],
                              split_date[1],
                              str(int(split_date[2]) - 5)])

        resp = Crawler.crawl_date_to_date_history(stock_symbol, from_date, to_date)
        data = Parser.parse_price_table(resp)

        return data

    @staticmethod
    def fetch_last_fifteen_years_data(stock_symbol):
        to_date = datetime.date.today().strftime('%d-%m-%Y')
        split_date = to_date.split("-")
        from_date = "-".join([split_date[0],
                              split_date[1],
                              str(int(split_date[2]) - 15)])

        resp = Crawler.crawl_date_to_date_history(stock_symbol, from_date, to_date)
        data = Parser.parse_price_table(resp)

        return data

    @staticmethod
    def export_five_years_data(stock_symbol, dao):
        data = Fetcher.fetch_last_five_years_data(stock_symbol)
        dao.add_data(stock_symbol, data)

    @staticmethod
    def export_fifteen_years_data(stock_symbol, dao):
        data = Fetcher.fetch_last_fifteen_years_data(stock_symbol)
        dao.add_data(stock_symbol, data)

    @staticmethod
    def export_stock_financial_docs(stock_symbol):
        try:
            data = Crawler.crawl_financial_data(stock_symbol)
            with open(f"res/screener-docs/{stock_symbol}.pkl", "wb") as fl:
                pickle.dump(data, fl)
        except Exception:
            print(
                f"Could not export financial data for symbol {stock_symbol}"
            )

    @staticmethod
    def clean_string(text):
        return text.strip(" ").strip("\n").strip(" ")

    @staticmethod
    def export_balance_sheet_data(stock_symbol, dao):
        parameters = [
            "time_published",
            "share_capital",
            "reserves",
            "borrowing",
            "other_liabilities",
            "total_liabilities",
            "fixed_assets",
            "cwip",
            "investments",
            "other_assets",
            "total_assets"
        ]
        try:
            document = dao.get_financial_doc(stock_symbol)
            financial_data = {}
            data = Parser.parse_balance_sheet_data(document)
            for time in data[0]:
                financial_data[Fetcher.clean_string(time)] = {}

            for row in range(1, len(data)):
                for col in range(len(data[0])):
                    financial_data[Fetcher.clean_string(data[0][col])][parameters[row]] = Fetcher.clean_string(data[row][col])

            dao.add_stock_financial_data(stock_symbol, financial_data)

        except Exception as exp:
            print(
                f"Could not parse balance sheet data"
            )

    @staticmethod
    def export_company_screener_id(stock_symbol, dao):
        document = dao.get_financial_doc(stock_symbol)
        id = Parser.parse_screener_id(document)
        data = {}
        try:
            with open("res/screener_id.pkl", "rb") as f:
                data = pickle.load(f)
                data[stock_symbol] = id
        except Exception:
            pass

        with open("res/screener_id.pkl", "wb") as f:
            pickle.dump(data, f)

    @staticmethod
    def export_income_statement_data(stock_symbol, dao):
        parameters = [
            "time_published",
            "sales",
            "expenses",
            "operating_profit",
            "opm_percentage",
            "other_income",
            "interest",
            "depreciation",
            "profit_before_tax",
            "tax_percentage",
            "net_profit",
            "eps_in_rs",
            "dividend_payout"
        ]
        try:
            document = dao.get_financial_doc(stock_symbol)
            financial_data = {}
            data = Parser.parse_income_statement(document)
            for time in data[0]:
                financial_data[time] = {}

            for row in range(1, len(data)):
                for col in range(len(data[0])):
                    financial_data[data[0][col]][parameters[row]] = data[row][col]

            dao.add_stock_financial_data(stock_symbol, financial_data)

        except Exception:
            print(
                f"[Skipped] Could not parse income statement data {stock_symbol}"
            )

    @staticmethod
    def export_quarterly_income_statement_data(stock_symbol, dao):
        parameters = [
            "time_published",
            "sales",
            "expenses",
            "operating_profit",
            "opm_percentage",
            "other_income",
            "interest",
            "depreciation",
            "profit_before_tax",
            "tax_percentage",
            "net_profit",
            "eps_in_rs"
        ]
        try:
            document = dao.get_financial_doc(stock_symbol)
            financial_data = {}
            data = Parser.parse_quarterly_income_statement(document)[:-1]
            for time in data[0]:
                financial_data[time] = {}

            for row in range(1, len(data)):
                for col in range(len(data[0])):
                    financial_data[data[0][col]][parameters[row]] = data[row][col]

            dao.add_quarterly_income_statement_data(stock_symbol, financial_data)

        except Exception as exp:
            print(
                f"[Skipped] Could not parse income statement data {stock_symbol}"
            )

    @staticmethod
    def export_stock_sector(stock_symbol, dao):
        try:
            document = dao.get_financial_doc(stock_symbol)
            stock_sector = Parser.parse_sector(document)
            dao.add_stock_sector(stock_symbol, stock_sector)
        except Exception:
            print(
                f"Could not parse sector data"
            )

    @staticmethod
    def export_screener_10k_prices(stock_symbol, dao):
        screener_id = str(dao.get_screener_id(stock_symbol))
        url = CONFIG.SCREENER_PRICE_URL.replace("COMPANY_SCREENER_ID", screener_id)
        headers = {
            "authority": "www.screener.in",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_0_1) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/87.0.4280.142 Safari/537.36",
            "x-requested-with": "XMLHttpRequest",
            "referer": "https://www.screener.in/company/INFY/consolidated/",
            "accept-language": "en-GB,en-US;q=0.9,en;q=0.8"
        }
        response = requests.get(url, headers=headers).json()["datasets"]
        values = []
        for dataset in response:
            if dataset["metric"] == "Price":
                values = dataset["values"]
        export_data = {value[0]: value[1] for value in values}

        dao.add_screener_price_data(stock_symbol, export_data)


class DataCollection:
    """Handle multiple tickers' collection"""

    def __init__(self, crud_ops):
        self.dao = DAO(crud_ops)
        self.fetcher = Fetcher()
        self.all_symbols = self.dao.get_symbols()

    def collect_weekly_data_all(self):
        for symbol in self.all_symbols:
            try:
                self.fetcher.export_weekly_data(symbol, self.dao)
                print(f"[Added] {symbol}")
            except Exception:
                print(f"[Skipped] {symbol}")
        sleep(1)

    def collect_five_years_data_all(self):
        check = True
        for symbol in self.all_symbols:
            if symbol == "HEG":
                check = True
            if check:
                try:
                    print(f"[Added] {symbol}")
                    self.fetcher.export_five_years_data(symbol, self.dao)
                except Exception:
                    print(f"[Skipped] {symbol}")
        sleep(1)

    def collect_fifteen_years_data_all(self):
        check = False
        for symbol in self.all_symbols:
            try:
                print(f"[Added] {symbol}")
                if not check:
                    if symbol == "LTI":
                        check = True
                if check:
                    self.fetcher.export_fifteen_years_data(symbol, self.dao)
            except Exception:
                print(f"[Skipped] {symbol}")
        sleep(1)

    def collect_financial_data(self):
        should_skip = True
        for symbol in tqdm(self.all_symbols):
            if symbol == "BINDALAGRO":
                should_skip = False

            if should_skip:
                continue

            try:
                self.fetcher.export_stock_financial_docs(symbol)
                self.fetcher.export_balance_sheet_data(symbol, self.dao)
                self.fetcher.export_income_statement_data(symbol, self.dao)
                # print(f"[Added] {symbol}")
            except Exception:
                print(f"[SKIPPED] {symbol}")
            sleep(0.5)

    def collect_quarterly_income_statement(self):
        for symbol in self.all_symbols:
            try:
                self.fetcher.export_stock_financial_docs(symbol)
                self.fetcher.export_quarterly_income_statement_data(symbol, self.dao)
                print(f"[Added] {symbol}")
            except Exception:
                print(f"[SKIPPED] {symbol}")
        sleep(1)

    def collect_all_company_screener_id(self):
        for symbol in self.all_symbols:
            try:
                self.fetcher.export_company_screener_id(symbol, self.dao)
                print(f"[Added] {symbol}")
            except Exception as exp:
                print(f"[SKIPPED] {symbol}")

    def collect_all_symbols_screener_prices(self):
        for symbol in self.all_symbols:
            try:
                self.fetcher.export_screener_10k_prices(symbol, self.dao)
                print(f"[Added] {symbol}")

                sleep(1)
            except Exception as exp:
                print(f"[SKIPPED] {symbol}")
