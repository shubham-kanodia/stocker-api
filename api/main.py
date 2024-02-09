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

# scheduler = BackgroundScheduler()
# scheduler.add_job(run_all_tasks, trigger='interval', hours=1, args=[data_collection, crud_ops])
# scheduler.start()

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
        return Watchlist(
            symbols=[WatchListElement(symbol=symbol, price=price) for symbol, price in symbols_and_prices]
        )

    except Exception as exp:
        return NotOK
