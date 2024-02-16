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


class Watchlist(Base):
    __tablename__ = "watchlist"

    id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    symbol = Column(String, nullable=False)
    price = Column(Float)


class Notifications(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    symbol = Column(String, nullable=False)
    message = Column(String, nullable=False)
    batch = Column(Integer)


class TopWinners(Base):
    __tablename__ = "top_winners"
    symbol = Column(String, primary_key=True, nullable=False, unique=True)
    change = Column(Float, nullable=False)


class TopLosers(Base):
    __tablename__ = "top_losers"
    symbol = Column(String, primary_key=True, nullable=False, unique=True)
    change = Column(Float, nullable=False)


class Logs(Base):
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, autoincrement=True, unique=True)

    time = Column('timestamp', TIMESTAMP(timezone=False), nullable=False, default=datetime.now())
    log = Column(String, nullable=False)


class Users(Base):
    __tablename__ = "users"

    username = Column(String, primary_key=True, unique=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)

    password_hash = Column(String, nullable=False)
