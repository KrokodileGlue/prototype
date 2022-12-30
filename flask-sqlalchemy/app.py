#!/usr/bin/env python3

from flask import Flask
from flask_restx import Api
from flask_jwt_extended import JWTManager

from session import session

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'super-secret' # TODO: Use an env variable
api = Api(app, version='0.5', title='Honk', description='Honk API')
jwt = JWTManager(app)

from user import api as user_api
from auth import api as auth_api

api.add_namespace(user_api)
api.add_namespace(auth_api)

if __name__ == '__main__':
    app.run(debug=True)
