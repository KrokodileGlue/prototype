import jwt

from werkzeug.security import generate_password_hash, check_password_hash

from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import Column, Integer, String

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String, nullable=False, unique=True)

    def serialize(self):
        return {
            'id': self.id,
            'username': self.username,
        }

engine = create_engine('sqlite:///database.sqlite3')
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine, autoflush=False)
session = Session()
