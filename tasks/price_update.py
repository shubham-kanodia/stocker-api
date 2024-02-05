from collection.data_collection import DataCollection


def price_update_task(data_collection: DataCollection):
    data_collection.collect_all_symbols_screener_prices()
