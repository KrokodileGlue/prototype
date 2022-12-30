import bcrypt

from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    password_hash = Column(String, nullable=False, unique=True)

    def set_password(self, password):
        self.password_hash = bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt(14))

    def check_password(self, password):
        return bcrypt.checkpw(password, self.password_hash)
