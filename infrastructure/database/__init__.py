from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from settings import settings

Base = declarative_base()
metadata = Base.metadata

engine = create_engine(settings.postgres_dsn)
Session = sessionmaker(bind=engine)
