from sqlalchemy import Column, String, Integer, Boolean, Float, TIMESTAMP
from datetime import datetime

from db.database import Base


class ScreenerIDS(Base):
    __tablename__ = "screener_ids"

    id = Column(Integer, primary_key=True, unique=True, index=True)
    symbol = Column(String, unique=True, nullable=False)


class Prices(Base):
    __tablename__ = "prices"

    id = Column(Integer, primary_key=True, autoincrement=True, unique=True)

    symbol = Column(String, nullable=False, index=True)
    date = Column(String, nullable=False)
    price = Column(Float)


class Logs(Base):
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, autoincrement=True, unique=True)

    time = Column('timestamp', TIMESTAMP(timezone=False), nullable=False, default=datetime.now())
    log = Column(String, nullable=False)
