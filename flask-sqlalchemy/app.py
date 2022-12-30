#!/usr/bin/env python3

import jwt
import os

from flask import Flask
from flask_restx import Api
from flask_jwt_extended import JWTManager

from session import session

app = Flask(__name__)

app.config.update(
    PROPAGATE_EXCEPTIONS = True,
    SECRET_KEY = os.getenv('SECRET_KEY'),
    JWT_SECRET_KEY = os.getenv('SECRET_KEY'),
    JWT_TOKEN_LOCATION = ['cookies'],
    JWT_COOKIE_CSRF_PROTECT = True,
    JWT_CSRF_CHECK_FORM = True
)

api = Api(app,
          version='0.5',
          title='Honk',
          description='Honk API',
          errors=Flask.errorhandler)

jwt_manager = JWTManager(app)

from user import api as user_api
from auth import api as auth_api
from suggestion import api as suggestion_api
from post import api as post_api

api.add_namespace(user_api)
api.add_namespace(auth_api)
api.add_namespace(suggestion_api)
api.add_namespace(post_api)

@jwt_manager.user_identity_loader
def user_identity_lookup(user):
    return user.id

from model import User

@jwt_manager.user_lookup_loader
def user_lookup_callback(jwt_header, jwt_data):
    id = jwt_data['sub']
    return session.query(User).filter_by(id=id).one_or_none()

@jwt_manager.expired_token_loader
def expired_signature_error_handler(jwt_header, jwt_payload):
    return {
        'status': 'fail',
        'message': 'Your login has expired; please log in again'
    }, 400

if __name__ == '__main__':
    app.run(debug=True)
