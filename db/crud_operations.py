from sqlalchemy.orm import Session
from sqlalchemy import func
from db.models import ScreenerIDS, Prices, Logs, Watchlist, Notifications
from datetime import datetime, timedelta


def handle_exception(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            args[0].db.rollback()
            return None

    return wrapper


class CRUDOperations:
    def __init__(self, db: Session):
        self.db = db

    @handle_exception
    def add_screener_ids(self, data):
        records = []
        for symbol, id in data.items():
            id_record = ScreenerIDS(
                id=id,
                symbol=symbol
            )
            records.append(id_record)

        self.db.add_all(records)
        self.db.commit()

    @handle_exception
    def get_screener_id(self, symbol: str):
        record = self.db.query(ScreenerIDS) \
            .filter(ScreenerIDS.symbol == symbol).first()

        return record.id if record else None

    @handle_exception
    def get_all_symbols(self):
        records = self.db.query(ScreenerIDS).all()
        symbols = [_.symbol for _ in records]

        return symbols

    @handle_exception
    def get_symbol_prices(self, symbol: str):
        records = self.db.query(Prices).filter(Prices.symbol == symbol).all()
        date_price_data = {record.date: record.price for record in records}
        return date_price_data

    @handle_exception
    def add_symbol_prices(self, symbol: str, date_price_dict):
        existing_symbol_price_dates = set(self.get_symbol_prices(symbol).keys())
        revised_date_price_data = {}

        for date in date_price_dict:
            if date not in existing_symbol_price_dates:
                revised_date_price_data[date] = date_price_dict[date]

        records = []
        for date, price in revised_date_price_data.items():
            record = Prices(
                symbol=symbol,
                date=date,
                price=price
            )
            records.append(record)

        # Update today's price
        date_today = str(datetime.now().strftime("%Y-%m-%d"))
        today_record = self.db.query(Prices) \
            .where((Prices.symbol == symbol) & (Prices.date == date_today)).first()
        if today_record and date_today in date_price_dict:
            today_record.price = date_price_dict[date_today]
            self.db.commit()

        if len(records):
            self.db.add_all(records)
            self.db.commit()

    @handle_exception
    def get_most_recent_price(self, symbol):
        def get_last_working_day(day):

            if day.weekday() == 6:
                last_working_day = day - timedelta(days=2)
            elif day.weekday() == 5:
                last_working_day = day - timedelta(days=1)
            else:
                last_working_day = day

            return last_working_day.strftime("%Y-%m-%d")

        today = datetime.now()
        last_working_day = str(get_last_working_day(today))
        record = self.db.query(Prices) \
            .where((Prices.symbol == symbol) & (Prices.date == last_working_day)).first()

        if not record:
            last_working_day = str(get_last_working_day(today - timedelta(days=1)))
            record = self.db.query(Prices) \
                .where((Prices.symbol == symbol) & (Prices.date == last_working_day)).first()

        return record.price if record else None

    @handle_exception
    def get_most_recent_prices_of_all_symbols(self):
        def get_last_working_day(day):

            if day.weekday() == 6:
                last_working_day = day - timedelta(days=2)
            elif day.weekday() == 5:
                last_working_day = day - timedelta(days=1)
            else:
                last_working_day = day

            return last_working_day.strftime("%Y-%m-%d")

        today = datetime.now()
        last_working_day = str(get_last_working_day(today))
        records = self.db.query(Prices) \
            .where((Prices.date == last_working_day)).all()

        if not len(records):
            last_working_day = str(get_last_working_day(today - timedelta(days=1)))
            records = self.db.query(Prices) \
                .where((Prices.date == last_working_day)).all()

        return {record.symbol: record.price for record in records}

    @handle_exception
    def add_log(self, log: str):
        record = Logs(
            log=log
        )

        self.db.add(record)
        self.db.commit()

    @handle_exception
    def add_to_watchlist(self, symbol, price):
        current_watchlist = self.get_watchlist()

        if symbol not in [_[0] for _ in current_watchlist]:

            record = Watchlist(
                symbol=symbol,
                price=price
            )

            self.db.add(record)
            self.db.commit()

        else:
            record = self.db.query(Watchlist).filter(Watchlist.symbol == symbol).first()
            record.price = price

            self.db.commit()

    @handle_exception
    def get_watchlist(self):
        records = self.db.query(Watchlist).all()

        return [(record.symbol, record.price) for record in records]

    @handle_exception
    def add_notifications(self, notifications):
        records = []

        max_batch = self.db.query(Notifications).query(Notifications.batch, func.max(Notifications.batch))
        batch_id = max_batch.batch + 1

        for symbol, message in notifications.items():
            record = Notifications(
                symbol=symbol,
                message=message,
                batch=batch_id
            )
            records.append(record)

        self.db.add_all(records)
        self.db.commit()
