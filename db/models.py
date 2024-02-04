from sqlalchemy import Column, String, Integer, Boolean

from db.database import Base


class ScreenerIDS(Base):
    __tablename__ = "screener_ids"

    id = Column(Integer, primary_key=True, unique=True, index=True)
    symbol = Column(String, unique=True, nullable=False)
