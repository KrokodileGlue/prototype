from flask import request
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import create_access_token

from model import User
from session import session

from UserSchema import UserSchema

schema = UserSchema()

api = Namespace('auth', description='Authentication operations')

@api.route('/register')
class Register(Resource):
    def post(self):
        '''Register a new user'''

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
            }, 409

        # Any error should've been handled at this point. If there's an
        # unhandled exception here then Flask will send a 500 for us.
        session.add(u)
        session.commit()

        return schema.dump(u)

@api.route('/login')
class Login(Resource):
    def post(self):
        '''Log in to the server to get an authentication token'''

        print(request.json)

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
                'status': 'success',
                'message': 'Incorrect login'
            }

        return { 'access_token': create_access_token(identity=username) }
