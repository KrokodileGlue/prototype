from marshmallow import Schema, fields, post_load
from model import User, Post

class UserSchema(Schema):
    name = fields.Str(required=True)
    username = fields.Str(required=True)
    email = fields.Str(load_only=True)

    @post_load
    def make_user(self, data, **kwargs):
        return User(**data)

class PostSchema(Schema):
    author = fields.Nested(UserSchema)
    body = fields.Str(required=True)

    @post_load
    def make_post(self, data, **kwargs):
        print(data)
        return Post(body=data['body'])
