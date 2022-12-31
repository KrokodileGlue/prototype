'''Marshmallow schema definitions for models defined in `model.py`.

These schemas decentralize and standardize serialization and deserialization of
database entities consistently across API endpoints.

Examples:

    # Partially deserialize a user (i.e. allow required fields to be omitted)

    from schema import UserSchema
    user_data = UserSchema(partial=True).load(request.json)

    # Or serialize a user

    from flask_jwt_extended import current_user
    from schema import UserSchema
    user_data = UserSchema().dump(current_user) # Could return from a Flask route
'''

from marshmallow import Schema, fields, post_load
from model import User, Post

# In the API endpoint modules obviously you need to be able create and update
# these model objects, and since flask-restx has deprecated their parsers in
# favor of things like Marshmallow then it would be nice if Marshmallow had
# some way to validate input and perform complex transformations during
# deserialization (i.e. you could create a user given some JSON that describes a user).
# https://stackoverflow.com/questions/9667138/how-to-update-sqlalchemy-row-entry

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
        return Post(**data)
