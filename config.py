from envyaml import EnvYAML
from dotenv import load_dotenv

import os


class Config:
    current_path = os.path.dirname(os.path.realpath(__file__))
    load_dotenv(os.path.join(current_path, "data/.env"))

    source = EnvYAML(os.path.join(current_path, "data/config.yaml"))

    db_user = source.get("db.user")
    db_name = source.get("db.database")
    db_server = os.getenv("DB_SERVER")

    db_pass = os.getenv("DB_PASSWORD")

    db_path = f"postgresql://{db_user}:{db_pass}@{db_server}/{db_name}"
