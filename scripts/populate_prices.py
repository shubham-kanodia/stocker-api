from db.crud_operations import CRUDOperations

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config import Config

from collection.data_collection import DataCollection

config = Config()
engine = create_engine(config.db_path)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db_session = SessionLocal()

crud_ops = CRUDOperations(db_session)

data_collection = DataCollection(crud_ops)
data_collection.collect_all_symbols_screener_prices()
