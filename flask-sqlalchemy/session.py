from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker

from model import Base

engine = create_engine('sqlite:///database.sqlite3')
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine, autoflush=False)
session = Session()
