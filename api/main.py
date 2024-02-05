from fastapi import FastAPI, Depends, Request, status
from fastapi.middleware.cors import CORSMiddleware

from apscheduler.schedulers.background import BackgroundScheduler

from db.crud_operations import CRUDOperations

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config import Config

from collection.data_collection import DataCollection
from tasks.main import run_all_tasks

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
