from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required

from model import User
from session import session

from UserSchema import UserSchema

schema = UserSchema()

api = Namespace('user', description='User operations')

user = api.model('User', {
    'username': fields.String(required=True, description='The user\'s name')
})

@api.route('/<string:username>')
@api.response(404, 'No such user')
@api.param('username', 'The username of the desired user')
class UserResource(Resource):
    @jwt_required()
    def get(self, username):
        '''Get public information about a user'''
        u = session.query(User).filter_by(username=username)
        if u.count() == 0:
            return {}, 404
        else:
            return schema.dump(u.first())
