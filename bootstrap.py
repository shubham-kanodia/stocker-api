# Download the list from here -
# https://www.nseindia.com/products-services/indices-nifty500-index and place it in the res/ directory

# Rename the file to "stock_list.csv"

import csv
import json
import requests
from time import sleep
from collection.dao import DAO
from collection.data_collection import DataCollection
from tqdm import tqdm

file_name = "res/stock_list.csv"
symbols_data = []

with open(file_name, 'r', newline='') as file:
    csv_reader = csv.reader(file)

    for row in csv_reader:
        if row[0] == "Company Name":
            continue

        company_name = row[0]
        symbol = row[2]
        listed_sector = row[1]

        symbols_data.append((symbol, {
            "company_name": company_name
        }))

dao = DAO()

for elem in symbols_data:
    dao.add_symbol(elem[0], elem[1])


def get_symbol_screener_id(symbol):
    response = requests.get(f"https://www.screener.in/api/company/search/?q={symbol}").json()
    symbol_id = response[0]["id"]
    return symbol_id


screener_id_dict = {}

for elem in tqdm(symbols_data):
    try:
        symbol_id = get_symbol_screener_id(elem[0])
        screener_id_dict[elem[0]] = symbol_id

        sleep(0.1)
    except:
        try:
            symbol_id = get_symbol_screener_id(elem[0])
            screener_id_dict[elem[0]] = symbol_id

            sleep(0.1)
        except:
            print(f"Skipped symbol: [{elem[0]}]")

with open("res/screener_ids.json", "w") as f:
    json.dump(screener_id_dict, f, indent=2)

data_collection = DataCollection()
data_collection.collect_all_symbols_screener_prices()
