from pydantic import BaseModel
from typing import List


class Message(BaseModel):
    message: str


class WatchListElement(BaseModel):
    symbol: str
    added_price: float
    current_price: float


class Watchlist(BaseModel):
    symbols: List[WatchListElement]


class WatchlistNotification(BaseModel):
    symbol: str
    message: str


class WatchlistNotifications(BaseModel):
    notifications: List[WatchlistNotification]


class PriceChange(BaseModel):
    symbol: str
    price_change: float


class PriceChanges(BaseModel):
    stocks: List[PriceChange]


class Token(BaseModel):
    access_token: str


OK = Message(message="OK")
NotOK = Message(message="Failed")