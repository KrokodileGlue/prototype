"""API endpoints related to user access and updates.

Basic usage is like this:

    from flask import Flask
    from flask_restx import Api
    app = Flask()
    api = Api(app)
    from user import api as user_api
    api.add_namespace(user_api)       # Routes defined in user.py are now active
"""

from flask import request
from flask_restx import Namespace, Resource, fields, marshal_with
from flask_jwt_extended import jwt_required, current_user

from model import User
from session import session
from schema import UserSchema

api = Namespace('user', description='User operations')

full_user_model = api.model('User', {
    'name': fields.String(description='The user\'s name'),
    'username': fields.String(description='The user\'s username'),
})

@api.route('/<string:username>')
@api.response(404, 'No such user')
@api.param('username', 'The username of the desired user')
class UserResource(Resource):
    @jwt_required()
    @marshal_with(full_user_model)
    def get(self, username):
        '''Get public information about a user'''
        u = session.query(User).filter_by(username=username)
        if u.count() == 0:
            return {
                'status': 'fail',
                'message': 'No such user exists'
            }, 404
        return UserSchema().dump(u.first())

    @jwt_required()
    def put(self, username):
        '''Update an existing user'''

        u = session.query(User).filter_by(username=username)

        if u.count() == 0:
            return {
                'status': 'fail',
                'message': 'No such user exists'
            }, 404

        u = u.first()

        if u != current_user:
            return {
                'status': 'fail',
                'message': 'You don\'t have permission to update that user'
            }, 403

        # `password` isn't a valid property of `User`, but the user thinks it
        # is so we have to snag it here before we validate the rest of the
        # request. Same thing with `email`.

        password = request.json.pop('password', None)
        email = request.json.pop('email', None)

        # During registration the user has to specify all of the required
        # fields like the username and password. This is a partial update
        # though, where we still want the request to roughly correspond to a
        # user and Marshmallow's validation is the way to go. In olden days we
        # would've used flask-restx's parsers. By setting `partial=True` when
        # we create the schema we allow these partial updates we want.
        try:
            schema = UserSchema(partial=True)
            user_data = schema.load(request.json)
        except:
            return {
                'status': 'fail',
                'message': 'Couldn\'t deserialize user'
            }

        # Update the email first because it could fail and we want to return
        # early if it does.
        if email != None:
            email_status, email_error = u.set_email(email)

            if not email_status:
                return {
                        'status': 'fail',
                        'message': email_error
                }

        if password != None:
            u.set_password(password)

        update_status, update_message = u.update(user_data)

        if not update_status:
            return {
                    'status': 'fail',
                    'message': update_message
            }

        session.add(u)
        session.commit()

        return {
            'status': 'success',
            'message': 'Updated user successfully'
        }
