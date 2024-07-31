from flask_restful import Resource, reqparse
from flask_restful_swagger import swagger
from flask_jwt_extended import create_access_token
from api.models.usuario_model import Usuario
from api.utils.rbac import role_required
from pydantic import ValidationError
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient
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
        notes='Autentica usuarios',
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

class UsuarioAuthSetupResource(Resource):
    @swagger.operation(
        notes='Endpoint usado solo para registrar el primer usuario',
        responseClass=Usuario,
        nickname='post'
    )
    def post(self):
        if usuarios_collection.count_documents({}) != 0:
            return {'message': 'Unauthorized'}, 401
        
        data = usuario_parser.parse_args()
        usuario = data['username']
        password = generate_password_hash(data['password'])            
        try:
            primer_usuario = Usuario(
                username=usuario, 
                password=password, 
                role="admin", 
                fecha_creacion=datetime.datetime.now(), 
                parent_user="root"
                )
            usuarios_collection.insert_one(primer_usuario.model_dump())
            return {'message': 'Nuevo admin creado con exito'}, 201
        except ValidationError:
            return {'message': 'Requisicion malformada'}, 400
    

class UsuarioResource(Resource):
    @swagger.operation(
        notes='Lista usuarios',
        responseClass=Usuario,
        nickname='listaUsuario'
    )
    
    @role_required('admin')  
    def get(self):
        users = list(usuarios_collection.find({}, {'password': 0}))
        return json.loads(json.dumps(users, default=str))

    @swagger.operation(
        notes='Delete a user by username',
        responseClass=Usuario,
        nickname='deleteUsuario'
    )
    
    @role_required('admin')
    def delete(self, username):
        result = usuarios_collection.delete_one({'username': username})
        if result.deleted_count == 0:
            return {'message': 'User not found'}, 404
        return 'Usuario eliminado', 204

    @swagger.operation(
        notes='Atualiza un usuario',
        responseClass=Usuario,
        nickname='putUsuario'
    )
    @role_required('admin')
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
        notes='Crea um nuevo usuario',
        responseClass=Usuario,
        nickname='postUsuario'
    )
    
    @role_required('admin')
    def post(self):
        data = usuario_parser.parse_args()
        password_hash = generate_password_hash(data['password'])
        nuevo_usuario = Usuario(
                username=data['username'], 
                password=password_hash,
                role=data['role'], 
                fecha_creacion=datetime.datetime.now()
                )
        
        result = usuarios_collection.insert_one(nuevo_usuario.model_dump())
        return nuevo_usuario, 201
