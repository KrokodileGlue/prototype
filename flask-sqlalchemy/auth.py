from flask import request, make_response
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import (
    jwt_required, create_access_token, set_access_cookies, unset_access_cookies
)

from email_validator import validate_email

from model import User
from session import session

from schema import UserSchema

schema = UserSchema()

api = Namespace('auth', description='Authentication operations')

registration_model = api.model('Register', {
    'username': fields.String(required=True, description='The user\'s name'),
    'email': fields.String(required=True, description='The user\'s email'),
    'password': fields.String(required=True, description='The user\'s password')
})

@api.route('/register')
class Register(Resource):
    def post(self):
        '''Register a new user'''

        # This is used in several places, so define it here to keep them in
        # sync.
        success_response = {
            'status': 'success',
            'message': 'Account created successfully'
        }

        email = request.json.get('email', None)
        password = request.json.get('password', None)

        try:
            email = validate_email(email).email
        except Exception as e:
            # NOTE: Might be worth customizing the error messages at some point.
            return {
                    'status': 'fail',
                    'message': e.__str__()
            }

        try:
            u = schema.load(request.json)
        except:
            return {
                    'status': 'fail',
                    'message': 'Couldn\'t deserialize user'
            }, 500

        if session.query(User).filter_by(username=u.username).count() > 0:
            return {
                'status': 'fail',
                'message': 'Username already in use'
            }

        if session.query(User).filter_by(email=u.email).count() > 0:
            # This is the case where an email address is already in use. It's
            # better not to tell the client that the email is being used,
            # because that could be used as the basis for an enumeration
            # attack. Failing silently is fine for now.

            # TODO: Send an email to the existing user notifying them that
            # someone is trying to sign up with their email. They can choose to
            # ignore it, or it'll remind them that they already have an account
            # if they were trying to sign up and forgot they already had one.

            return success_response

        u.set_password(password)

        # Any error should've been handled at this point. If there's an
        # unhandled exception here then Flask will send a 500 for us.
        session.add(u)
        session.commit()

        return success_response

@api.route('/login')
class Login(Resource):
    def post(self):
        '''Log in to the server to get an authentication token'''

        username = request.json.get('username', None)
        password = request.json.get('password', None)

        if username == None or password == None:
            return {
                    'status': 'fail',
                    'message': 'Username or password missing'
            }

        password = password.encode('utf8')
        u = session.query(User).filter_by(username=username).first()

        if u == None or not u.check_password(password):
            return {
                'status': 'fail',
                'message': 'Incorrect login'
            }

        access_token = create_access_token(identity=u)
        resp = make_response({
            'status': 'success',
            'message': 'Successfully logged in'
        })
        set_access_cookies(resp, access_token)
        return resp

@api.route('/logout')
class Logout(Resource):
    def post(self):
        '''Log out'''
        resp = make_response({
            'status': 'success',
            'message': 'Successfully logged out'
        })
        unset_access_cookies(resp)
        return resp
