import os
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine
import mysql.connector

load_dotenv(dotenv_path="data.env")

engine = create_engine(
    f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}"
)


def _load_plants(engine) -> pd.DataFrame:
    with engine.connect() as conn:
        df = pd.read_sql("plants", conn, parse_dates=["acquired_at"])
    return df


def _load_leaves(engine) -> pd.DataFrame:
    with engine.connect() as conn:
        df = pd.read_sql("leaves", conn, parse_dates=["matured_at"])
    df["matured_at_estimated"] = df["matured_at_estimated"].astype(bool)
    return df

def load_and_combine() -> pd.DataFrame:
    plants = _load_plants(engine)
    leaves = _load_leaves(engine)
    df = leaves.merge(plants, left_on ="plant_id", right_on="id", how="left")

    return df

if __name__ == "__main__":
    df = load_and_combine()
    df = df.drop(columns=["id_y"])
    df.to_csv("data.csv")