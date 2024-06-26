from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Get the env var
DATABASE_URL = os.environ.get("DB_URL")

# create the 'engine'
engine = create_engine(DATABASE_URL)

# construct new session with the created engine
SessionLocal = sessionmaker(autoflush=False, bind=engine)

Base = declarative_base()