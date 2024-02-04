import os
import pickle
import json
import numpy as np
from datetime import datetime
from pymongo import MongoClient
from collection.config import CONFIG

from db.crud_operations import CRUDOperations


class DAO:
    def __init__(self, crud_ops: CRUDOperations):
        self.crud_ops = crud_ops
        cluster = MongoClient(CONFIG.MONGO_URI)
        _db = cluster["stocker"]
        self.collection_stock_names = _db["stock_names"]
        self.collection_stock_prices = _db["stock_prices"]
        self.collection_stock_financials = _db["financial_data"]
        self.collection_screener_prices = _db["screener_prices"]
        self.collection_golden_crossover = _db["golden_crossover"]
        self.collection_covid_effect = _db["covid_effect"]
        self.collection_quarterly_income_statement = _db["quarterly_income_statement"]

        path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "../res/screener_ids.json"
        )
        self.screener_id_dict = json.load(open(path, "rb"))

    def get_symbols(self):
        return self.crud_ops.get_all_symbols()

    def add_symbol(self, symbol, data):
        if self.collection_stock_names.find_one({"_id": symbol}):
            self.collection_stock_names.update_one({"_id": symbol}, {"$set": data})
        else:
            data["_id"] = symbol
            self.collection_stock_names.insert_one(data)

    def add_data(self, symbol, data):
        if self.collection_stock_prices.find_one({"_id": symbol}):
            self.collection_stock_prices.update_one({"_id": symbol}, {"$set": data})
        else:
            data["_id"] = symbol
            self.collection_stock_prices.insert_one(data)

    def add_screener_price_data(self, symbol, data):
        self.crud_ops.add_symbol_prices(symbol, data)

    def get_stock_data(self, symbol):
        return self.collection_stock_prices.find({"_id": symbol})[0]

    @staticmethod
    def get_financial_doc(symbol):
        with open(f"res/screener-docs/{symbol}.pkl", "rb") as fl:
            page = pickle.load(fl)
        return page

    @staticmethod
    def _merge_financial_data(prior_data, recent_financial_data):
        for key in prior_data:
            if key in recent_financial_data:
                recent_financial_data[key] = {**prior_data[key], **recent_financial_data[key]}
            else:
                recent_financial_data[key] = prior_data[key]
        return recent_financial_data

    def add_stock_financial_data(self, symbol, financial_data):
        prior_data = self.collection_stock_financials.find_one({"_id": symbol})
        if prior_data:
            merged_data = self._merge_financial_data(prior_data, financial_data)
            self.collection_stock_financials.update_one({"_id": symbol}, {"$set": merged_data})
        else:
            self.collection_stock_financials.insert_one({"_id": symbol, **financial_data})

    def get_screener_id(self, stock_symbol):
        screener_id = self.screener_id_dict.get(stock_symbol, None)
        return str(screener_id) if screener_id else None

    def update_golden_crossover_collection(self, data):
        self.collection_golden_crossover.remove({})

        data["_id"] = 1
        self.collection_golden_crossover.insert_one(data)

    def get_golden_crossover_data(self):
        return self.collection_golden_crossover.find({"_id": 1})[0]

    def update_covid_effect_collection(self, data):
        data["_id"] = datetime.today().date().strftime("%d-%b-%Y")
        self.collection_covid_effect.insert_one(data)

    def get_stock_price_history(self, symbol):
        symbol_price = self.get_stock_data(symbol)
        dates = sorted(
            list(
                symbol_price.keys())[1:],
                key=lambda date: datetime.strptime(date, "%d-%b-%Y")
        )
        prices = [float(symbol_price[date]["close_price"].replace(",", "")) for date in dates]
        return dates, prices

    def check_stock_split(self, symbol, period):
        try:
            _, prices = self.get_stock_price_history(symbol)
            prices = np.array(prices[-1 * period:])

            for ind in range(1, len(prices)):
                prev_price = prices[ind - 1]
                price = prices[ind]

                if abs(price - prev_price) * 100 / prev_price > 20:
                    return True
            return False
        except Exception:
            return False

    def add_quarterly_income_statement_data(self, symbol, data):
        data["_id"] = symbol
        prior_data = self.collection_quarterly_income_statement.find_one({"_id": symbol})
        if prior_data:
            self.collection_quarterly_income_statement.update_one({"_id": symbol}, {"$set": data})
        else:
            self.collection_quarterly_income_statement.insert_one(data)

    def get_stock_financial_data(self, symbol):
        return self.collection_stock_financials.find({"_id": symbol})[0]
