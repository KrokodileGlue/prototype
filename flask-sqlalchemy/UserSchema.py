from marshmallow import Schema, fields, post_load
from model import User

class UserSchema(Schema):
    username = fields.Str()
    password = fields.Str(load_only=True)

    @post_load
    def make_user(self, data, **kwargs):
        u = User(username=data['username'])
        u.set_password(data['password'])
        return u
