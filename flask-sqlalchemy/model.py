import bcrypt

from sqlalchemy import ForeignKey, Column
from sqlalchemy.types import JSON
from sqlalchemy.orm import DeclarativeBase, Mapped, relationship, mapped_column

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    email: Mapped[str] = mapped_column(unique=True)
    password_hash: Mapped[str] = mapped_column(nullable=False, unique=True)

    posts: Mapped[list['Post']] = relationship(back_populates='author')

    def set_password(self, password):
        self.password_hash = bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt(14))

    def check_password(self, password):
        return bcrypt.checkpw(password, self.password_hash)

class Post(Base):
    __tablename__ = 'posts'

    id: Mapped[int] = mapped_column(primary_key=True)
    author_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    author: Mapped['User'] = relationship(back_populates='posts')
    body = Column(JSON)
