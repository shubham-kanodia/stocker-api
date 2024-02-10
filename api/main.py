from fastapi import FastAPI, Depends, Request, status
from fastapi.middleware.cors import CORSMiddleware

from apscheduler.schedulers.background import BackgroundScheduler

from db.crud_operations import CRUDOperations

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config import Config

from collection.data_collection import DataCollection
from tasks.main import run_all_tasks

from api.models.inputs import *
from api.models.outputs import *

app = FastAPI()

config = Config()
engine = create_engine(config.db_path)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db_session = SessionLocal()

crud_ops = CRUDOperations(db_session)

data_collection = DataCollection(crud_ops)

scheduler = BackgroundScheduler()
scheduler.add_job(run_all_tasks, trigger='interval', hours=1, args=[data_collection, crud_ops])
scheduler.start()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": f"Welcome to Stocker!"}


@app.post("/watchlist/add")
async def add_to_watchlist(inp: WatchlistInput):
    try:
        current_price = crud_ops.get_most_recent_price(inp.symbol)
        crud_ops.add_to_watchlist(inp.symbol, current_price)

        return OK

    except Exception as exp:
        return NotOK


@app.get("/watchlist")
async def get_watchlist():
    try:
        symbols_and_prices = crud_ops.get_watchlist()
        current_prices = crud_ops.get_most_recent_prices_of_all_symbols()

        return Watchlist(
            symbols=[WatchListElement(symbol=symbol, added_price=price, current_price=current_prices[symbol]) for symbol, price in symbols_and_prices if symbol in current_prices]
        )

    except Exception as exp:
        print(exp)
        return NotOK


@app.get("/watchlist/notifications")
async def get_watchlist_notifications():
    try:
        notifications = crud_ops.get_recent_watchlist_notifications()

        return WatchlistNotifications(
            notifications=[WatchlistNotification(symbol=symbol, message=message) for symbol, message in notifications]
        )

    except Exception as exp:
        return NotOK


@app.get("/winners")
async def get_recent_winners():
    try:
        winners = crud_ops.get_winners()

        return PriceChanges(
            stocks=[PriceChange(symbol=symbol, price_change=price_change) for symbol, price_change in winners]
        )

    except Exception as exp:
        return NotOK


@app.get("/losers")
async def get_recent_losers():
    try:
        losers = crud_ops.get_losers()

        return PriceChanges(
            stocks=[PriceChange(symbol=symbol, price_change=price_change) for symbol, price_change in losers]
        )

    except Exception as exp:
        return NotOK
