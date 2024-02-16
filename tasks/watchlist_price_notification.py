"""
Should notify user when (Priority increases downwards):

-   Stock is rallying upwards and has been rising for more than 2 days
-   Stock in watchlist falls below 5%
-   Stock in watchlist has been falling since more than 2 days

Later (Maybes)

-   Stock has a golden crossover
"""

"""
Notifications about general stocks:

-   Stocks that have been falling for max number of days
-   Stocks that have been rising for max number of days

"""

from db.crud_operations import CRUDOperations
from tasks.utils.price_notification_utils import PriceNotificationsChecker


def get_symbol_prices(records, symbol):
    price_data = {record.date: record.price for record in records if record.symbol == symbol}
    return price_data


def get_symbol_notifications(symbol: str, prices, pnc: PriceNotificationsChecker):
    notifications = []
    sorted_dict = sorted(prices.items())
    prices_lst = [_[1] for _ in sorted_dict]

    # Check for rising above threshold
    (check, price_change) = pnc.has_risen_above_threshold(prices_lst)

    if check:
        price_change = round(price_change, 2)
        notifications.append((symbol, f"{symbol} has last increased by {price_change}%."))

    # Check falling below threshold
    (check, price_change) = pnc.has_fallen_below_threshold(prices_lst)

    if check:
        price_change = round(price_change, 2)
        notifications.append((symbol, f"{symbol} has last decreased by {price_change}%."))

    # Increasing for number of days
    (days, price_change) = pnc.rising_days(prices_lst)

    if days >= 2:
        price_change = round(price_change, 2)
        notifications.append((symbol,
                              f"{symbol} has been increasing since {days} days, it has increased by {price_change}% since {days} days."))

    # Falling for number of days
    (days, price_change) = pnc.falling_days(prices_lst)

    if days >= 2:
        price_change = round(price_change, 2)
        notifications.append((symbol,
                              f"{symbol} has been decreasing since {days} days, it has decreased by {price_change}% since {days} days."))

    return notifications


def generate_price_notifications(crud_ops: CRUDOperations):
    pnc = PriceNotificationsChecker()

    symbols = crud_ops.get_all_symbols()
    records = crud_ops.get_all_prices()

    notifications = []

    for symbol in symbols:
        try:
            prices = get_symbol_prices(records, symbol)
            symbol_notification = get_symbol_notifications(symbol, prices, pnc)

            notifications.extend(symbol_notification)
        except Exception as exp:
            print(f"[SKIPPED] {symbol}")

    crud_ops.add_notifications(notifications)
