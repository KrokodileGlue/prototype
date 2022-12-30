from flask import request
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, current_user

from model import User, Post
from session import session
from schema import PostSchema

api = Namespace('post', description='Post operations')

@api.route('/<int:id>')
@api.param('id', 'The id of the desired post')
class PostResource(Resource):
    @jwt_required()
    def get(self, id):
        '''Get public information about a post'''
        post = session.query(Post).filter_by(id=id)
        if post.count() == 0:
            return {
                'status': 'fail',
                'message': 'No such post exists'
            }, 404
        else:
            return PostSchema().dump(post.first())

@api.route('')
class NewPost(Resource):
    @jwt_required()
    def post(self):
        '''Create a new post'''
        
        try:
            p = PostSchema().load(request.json)
        except Exception as e:
            print(e.__str__())
            return {
                    'status': 'fail',
                    'message': 'Couldn\'t deserialize post'
            }, 500

        p.author = current_user

        session.add(p)
        session.commit()

        return {
            'status': 'success',
            'message': 'Post created successfully'
        }
