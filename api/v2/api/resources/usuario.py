from flask import jsonify
from flask_restful import Resource, reqparse
from flask_restful_swagger import swagger
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, verify_jwt_in_request
from functools import wraps
from api.models.usuario_model import Usuario
from api.utils.rbac import role_required
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient
from bson import ObjectId
import os
import datetime
import json

# Initialize MongoDB
client = MongoClient(os.environ.get('MONGO_URI'))
db = client['data']
usuarios_collection = db['usuarios']

# Request parser for creating and updating a user
usuario_parser = reqparse.RequestParser()
usuario_parser.add_argument('username', type=str, required=True, help='Username cannot be blank')
usuario_parser.add_argument('password', type=str, required=True, help='Password cannot be blank')
usuario_parser.add_argument('role', type=str, required=False, help='Role is autoset when blank')
usuario_parser.add_argument('parent_user', type=str, required=False, help='Parent user cannot be blank')


class UsuarioAuthResource(Resource):
    @swagger.operation(
        notes='Authenticate a user',
        responseClass=Usuario.__name__,
        nickname='post'
    )
    def post(self):
        data = usuario_parser.parse_args()
        usuario = usuarios_collection.find_one({'username': data['username']})
        if not usuario or not check_password_hash(usuario['password'], data['password']):
            return {'message': 'Invalid credentials'}, 401
        access_token = create_access_token(identity=str(usuario['role']))
        return {'access_token': access_token}, 200
    
class UsuarioResource(Resource):
    @swagger.operation(
        notes='Get a user by username',
        responseClass=Usuario.__name__,
        nickname='get'
    )
    
    @role_required('admin')
    def get(self, username):
        usuario = usuarios_collection.find_one({'username': username})
        if not usuario:
            return {'message': 'User not found'}, 404
        usuario['_id'] = str(usuario['_id'])  
        return json.loads(json.dumps(usuario, default=str))

    @swagger.operation(
        notes='Delete a user by username',
        responseMessages=[
            {
                'code': 204,
                'message': 'User deleted'
            },
            {
                'code': 404,
                'message': 'User not found'
            }
        ]
    )
    def delete(self, username):
        result = usuarios_collection.delete_one({'username': username})
        if result.deleted_count == 0:
            return {'message': 'User not found'}, 404
        return '', 204

    @swagger.operation(
        notes='Update a user by username',
        responseClass=Usuario.__name__,
        nickname='put'
    )
    def put(self, username):
        data = usuario_parser.parse_args()
        password_hash = generate_password_hash(data['password'])
        updated_user = {
            'username': data['username'],
            'password': password_hash,
            'role': data['role'],
            'parent_user': data['parent_user'],
            'fecha_creacion': datetime.datetime.now()
        }
        result = usuarios_collection.update_one({'username': username}, {'$set': updated_user})
        if result.matched_count == 0:
            return {'message': 'User not found'}, 404
        updated_user['_id'] = str(result.upserted_id)
        return updated_user

    @swagger.operation(
        notes='Create a new user',
        responseClass=Usuario.__name__,
        nickname='post'
    )
    def post(self):
        data = usuario_parser.parse_args()
        password_hash = generate_password_hash(data['password'])
        new_user = {
            'username': data['username'],
            'password': password_hash,
            'role': data['role'],
            'parent_user': data['parent_user'],
            'fecha_creacion': datetime.datetime.now()
        }
        result = usuarios_collection.insert_one(new_user)
        new_user['_id'] = str(result.inserted_id)
        return new_user, 201

    @swagger.operation(
        notes='Get a list of all users',
        responseClass=Usuario.__name__,
        nickname='get'
    )
    def get(self):
        usuarios = list(usuarios_collection.find())
        for usuario in usuarios:
            usuario['_id'] = str(usuario['_id'])
        return json.loads(json.dumps(usuarios, default=str))
