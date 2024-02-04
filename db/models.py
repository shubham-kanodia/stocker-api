from sqlalchemy import Column, String, Integer, Boolean, Float

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
