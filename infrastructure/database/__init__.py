from sqlalchemy import create_engine
from sqlalchemy.engine.base import Engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from settings import settings


Base = declarative_base()
metadata = Base.metadata

engine: Engine = create_engine(settings.postgres_dsn)
Session: sessionmaker = sessionmaker(bind=engine)
