from flask_restx import Namespace, Resource, fields

from model import User
from session import session

api = Namespace('user', description='User operations')

user = api.model('User', {
    'id': fields.Integer(readonly=True, description='The unique user identifier'),
    'username': fields.String(required=True, description='The user\'s name')
})

@api.route('/<string:username>')
@api.response(404, 'No such user')
@api.param('username', 'The username of the desired user')
class UserResource(Resource):
    @api.doc('show_user')
    @api.marshal_list_with(user)
    def get(self, username):
        '''Get information about a user'''
        u = session.query(User).filter_by(username=username)
        if u.count() == 0:
            return {}, 404
        else:
            return u.first()
