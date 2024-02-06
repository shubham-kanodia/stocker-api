from db.crud_operations import CRUDOperations


class DAO:
    def __init__(self, crud_ops: CRUDOperations):
        self.crud_ops = crud_ops

    def get_symbols(self):
        return self.crud_ops.get_all_symbols()

    def add_screener_price_data(self, symbol, data):
        self.crud_ops.add_symbol_prices(symbol, data)

    def get_screener_id(self, symbol: str):
        return self.crud_ops.get_screener_id(symbol)
