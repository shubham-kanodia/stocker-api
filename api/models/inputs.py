from pydantic import BaseModel


class WatchlistInput(BaseModel):
    symbol: str
