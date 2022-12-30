#!/usr/bin/env python3

from flask import Flask
from flask_restful import Resource, Api

from model import session, User

app = Flask(__name__)
api = Api(app)

class UserResource(Resource):
    def get(self, username):
        u = session.query(User).filter_by(username=username)
        if u.count() == 0:
            return {
                    'status': 'fail',
                    'message': 'No such user exists'
            }, 404
        else:
            return u.first().serialize()

api.add_resource(UserResource, '/u/<string:username>')

if __name__ == '__main__':
    app.run(debug=True)
