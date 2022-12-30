from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required

from model import User
from session import session
from schema import UserSchema

schema = UserSchema()
api = Namespace('suggestion', description='Suggestions')

@api.route('/username/<string:username>')
@api.param('username', 'Partially completed username')
class UsernameSuggestion(Resource):
    @jwt_required()
    def get(self, username):
        '''Get usernames similar to a given username'''
        filter = User.username.like('%{}%'.format(username))
        results = session.query(User).filter(filter).all()
        return {
            'status': 'success',
            'results': [schema.dump(result) for result in results]
        }
