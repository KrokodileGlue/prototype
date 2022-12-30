#!/usr/bin/env python3

from flask import Flask
from flask_restx import Api

from session import session

app = Flask(__name__)
api = Api(app, version='0.5', title='Honk', description='Honk API')

from user import api as user_api

api.add_namespace(user_api)

if __name__ == '__main__':
    app.run(debug=True)
