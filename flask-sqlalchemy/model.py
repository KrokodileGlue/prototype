import bcrypt

from sqlalchemy import Column
from sqlalchemy.types import JSON
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    email: Mapped[str] = mapped_column(unique=True)
    password_hash: Mapped[str] = mapped_column(nullable=False, unique=True)

    def set_password(self, password):
        self.password_hash = bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt(14))

    def check_password(self, password):
        return bcrypt.checkpw(password, self.password_hash)

class Post(Base):
    __tablename__ = 'posts'

    id: Mapped[int] = mapped_column(primary_key=True)
    author: Mapped[str]
    body = Column(JSON)
