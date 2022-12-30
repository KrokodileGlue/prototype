#!/usr/bin/env python3

from flask import Flask
from flask_restx import Api, Resource, fields

from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker

from model import Base, User

engine = create_engine('sqlite:///database.sqlite3')
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine, autoflush=False)
session = Session()

app = Flask(__name__)
api = Api(app,
          version='0.5',
          title='honk',
          description='The honk API')

ns = api.namespace('user', description='User operations')

user = api.model('User', {
    'id': fields.Integer(readonly=True, description='The unique user identifier'),
    'username': fields.String(required=True, description='The user\'s name')
})

@ns.route('/<string:username>')
@ns.response(404, 'No such user')
@ns.param('username', 'The username of the desired user')
class UserResource(Resource):
    @ns.doc('show_user')
    @ns.marshal_list_with(user)
    def get(self, username):
        '''Get information about a user'''
        u = session.query(User).filter_by(username=username)
        if u.count() == 0:
            return {}, 404
        else:
            return u.first()

if __name__ == '__main__':
    app.run(debug=True)
