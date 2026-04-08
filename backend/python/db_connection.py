# db_connection.py
# Shared MongoDB connection for Streamlit & Jupyter

import mongoengine
from mongoengine.connection import disconnect
from dotenv import load_dotenv
from pathlib import Path
import os


def connect_to_mongodb():
    """
    Connect to MongoDB using MONGO_URI from .env
    """

    # Load .env from current folder
    env_path = Path(__file__).resolve().parent / '.env'
    load_dotenv(dotenv_path=env_path)

    MONGO_URI = os.getenv("MONGO_URI")
    MONGO_DB = os.getenv("MONGO_DB_NAME", "products_db")

    if not MONGO_URI:
        raise ValueError("MONGO_URI not found in .env file")

    # Disconnect existing connection (important in notebooks/streamlit reloads)
    disconnect(alias='default')

    # Connect using URI
    mongoengine.connect(
        host=MONGO_URI,
        alias='default'
    )

    return MONGO_DB