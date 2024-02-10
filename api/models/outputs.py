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


OK = Message(message="OK")
NotOK = Message(message="Failed")