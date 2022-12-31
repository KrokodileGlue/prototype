from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker

# SQLAlchemy works with metaclasses to create a list of all the database models
# defined in `model.py`. This works by storing them all in an object called the
# `metadata` which is stored in the `Base` (from DeclarativeBase) which all of
# our models inherit from. In order for the database models to be accessible
# here for `create_all` and so we can create the session, we have to get the
# same `Base` that was used when we declared the models.
from model import Base

engine = create_engine('sqlite:///database.sqlite3')
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine, autoflush=False)
session = Session()
