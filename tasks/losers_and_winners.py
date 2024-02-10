from db.crud_operations import CRUDOperations
from tasks.utils.price_notification_utils import PriceNotificationsChecker


def get_symbol_prices(records, symbol):
    price_data = {record.date: record.price for record in records if record.symbol == symbol}
    sorted_dict = sorted(price_data.items())
    prices_lst = [_[1] for _ in sorted_dict]
    return prices_lst


def populate_top_losers_and_winners(crud_ops: CRUDOperations):
    pnc = PriceNotificationsChecker()

    symbols = crud_ops.get_all_symbols()
    records = crud_ops.get_all_prices()

    recent_change = {}
    for symbol in symbols:
        price_lst = get_symbol_prices(records, symbol)
        recent_change[symbol] = pnc._get_latest_price_change(price_lst)

    sorted_by_change = list(sorted(recent_change, key=lambda x: recent_change[x]))

    top_losers = [(_, round(recent_change[_], 2)) for _ in sorted_by_change][:10]
    top_winners = [(_, round(recent_change[_], 2)) for _ in sorted_by_change][-10:]

    crud_ops.add_losers(top_losers)
    crud_ops.add_winners(top_winners)
