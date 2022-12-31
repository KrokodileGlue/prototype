import bcrypt

from sqlalchemy import ForeignKey, Column
from sqlalchemy.types import JSON
from sqlalchemy.orm import DeclarativeBase, Mapped, relationship, mapped_column

from email_validator import validate_email

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)

    #       /- name
    #       |
    #       |
    # /--\  v
    # |🪿| epic goose 💯 ----------------
    # \__/ @goose          joined 2022
    #       ^
    #       |
    #       |
    #       \- username (no @ in the actual username)

    name: Mapped[str]
    username: Mapped[str] = mapped_column(unique=True)
    validated_email: Mapped[str] = mapped_column(unique=True)
    password_hash: Mapped[str] = mapped_column(nullable=False, unique=True)

    posts: Mapped[list['Post']] = relationship(back_populates='author')

    def set_password(self, password):
        self.password_hash = bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt(14))

    def check_password(self, password):
        return bcrypt.checkpw(password, self.password_hash)

    def set_email(self, email):
        try:
            # email email email email
            self.validated_email = validate_email(email).email
            return True, 'Success'
        except Exception as e:
            # NOTE: Might be worth customizing the error messages at some point.
            return False, str(e)

    def update(self, user_data):
        '''Update the user'''

        # Conceptually we could've written this:
        #
        # for k, v in request.json.items():
        #     setattr(self, k, v)
        #
        # The issue is things like the difference between the password expected
        # in the request and the `password_hash` that's actually in the model.
        # I previously considered setting the password with `User.set_password`
        # in the Marshmallow schema but I decided that was beyond the scope of
        # what it should do. Any code that wants to create or update a user has
        # to manually call `set_password` and such, the schema in that case is
        # only good for doing basic validation.

        name = user_data.pop('name', None)
        username = user_data.pop('username', None)

class Post(Base):
    __tablename__ = 'posts'

    id: Mapped[int] = mapped_column(primary_key=True)
    author_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    author: Mapped['User'] = relationship(back_populates='posts')
    body = Column(JSON)
