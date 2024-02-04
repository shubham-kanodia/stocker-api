from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from db.models import ScreenerIDS


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
