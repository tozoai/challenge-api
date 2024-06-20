from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, verify_jwt_in_request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient
from pydantic import BaseModel
from bson.objectid import ObjectId
import datetime
import os
import re

application = Flask(__name__)

# Configurations
application.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY')
if not application.config['JWT_SECRET_KEY']:
    raise RuntimeError('Environment variable JWT_SECRET_KEY is not set, exiting...')

application.config['MONGO_URI'] = os.environ.get('MONGO_URI')
if not application.config['MONGO_URI']:
    raise RuntimeError('Environment variable MONGO_URI is not set, exiting...')

# Initialize JWT
jwt = JWTManager(application)

# Initialize MongoDB
client = MongoClient(application.config['MONGO_URI'])
db = client['data']
usuarios_collection = db['usuarios']
proveedores_collection = db['proveedores']

# Models
class Usuario(BaseModel):
    username: str
    password: str
    role: str
    fecha_creacion: datetime.datetime = datetime.datetime.now()
    parent_user: str = None

    def save_to_db(self):
        password_hash = generate_password_hash(self.password)
        usuarios_collection.insert_one({
            'username': self.username,
            'password': password_hash,
            'role': self.role,
            'fecha_creacion': self.fecha_creacion,
            'parent_user': self.parent_user
        })

class Proveedor(BaseModel):
    nombre: str
    razon_social: str
    nombre_contacto: str
    email: str
    direccion_fiscal: str
    tipo_servicio: str
    criticidad: int
    bloqueo: bool = False
    fecha_creacion: datetime.datetime = datetime.datetime.now()

    def save_to_db(self):
        result = proveedores_collection.insert_one(self.dict())
        self._id = result.inserted_id

# Security
def sanitize_get_jwt():
    try:
        verify_jwt_in_request()
        return get_jwt_identity()
    except Exception:
        return None

# Rate Limiting
limiter = Limiter(
    get_remote_address,
    app=application,
    default_limits=["1000 per day", "30 per minute"]
)

@application.after_request 
def add_security_headers(response):
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['Content-Security-Policy'] = "default-src 'self'"
    response.headers['Referrer-Policy'] = 'no-referrer'
    return response

# Auth
def get_user(username):
    return usuarios_collection.find_one({'username': username})

def authenticate_user(username, password):
    user = get_user(username)
    if user and check_password_hash(user['password'], password):
        return user
    return None

def validate_username(username):
    pattern = r'^[A-Za-z0-9]{4,12}$'
    return re.match(pattern, username) is not None

def validate_password(password):
    pattern = (r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d]{8,}$')
    return re.match(pattern, password) is not None

@application.route('/auth', methods=['POST'])
@limiter.limit("5 per minute")
def login():
    response = request.get_json()
    username = response.get('username')
    password = response.get('password')
    user = authenticate_user(username, password)
    if not user:
        return jsonify({"msg": "Bad username or password"}), 401
    access_token = create_access_token(identity={'username': user['username'], 'role': user['role']})
    return jsonify(access_token=access_token), 200            

@application.route('/auth', methods=['PUT'])
@limiter.limit("3 per minute")
def create_user():
    response = request.get_json()
    username = response.get('username')
    password = response.get('password')
    role = response.get('role')
    if not validate_username(username):
        return jsonify({"msg": "Invalid Username length"}), 400
    if not validate_password(password):
        return jsonify({"msg": "Password complexity not met"}), 400
    current_user = sanitize_get_jwt()
    if not current_user:
        return jsonify({"msg": "Admin privilege required not current user"}), 403
    if current_user['role'] != 'admin':
        return jsonify({"msg": "Admin privilege required not current role"}), 403
    existing_user = usuarios_collection.find_one({'username': username})
    if existing_user:
        return jsonify({"msg": "User already exists"}), 402
    if username == password:
        return jsonify({"msg": "Username cannot be the same as password"}), 402

    # First user does not require auth
    if usuarios_collection.count_documents({}) == 0:
        new_user = Usuario(username=username, password=password, role="admin")
        new_user.save_to_db()
        return jsonify({"msg": "Admin user created successfully"}), 201
    
    new_user = Usuario(username=username, password=password, role=role)
    new_user.save_to_db()
    return jsonify({"msg": "User created successfully"}), 201

@application.route('/proveedores', methods=['PUT'])
@jwt_required()
def create_proveedor():
    current_user = get_jwt_identity()
    if current_user['role'] != 'admin':
        return jsonify({"msg": "Admin privilege required"}), 403
    response = request.get_json()
    proveedor = Proveedor(**response)
    proveedor.save_to_db()
    return jsonify({"msg": "Created successfully"}), 201

@application.route('/proveedores/atualiza/<id>', methods=['PATCH'])
@jwt_required()
def update_proveedor(id):
    verify_jwt_in_request()
    current_user = get_jwt_identity()
    if current_user['role'] != 'admin':
        return jsonify({"msg": "Admin privilege required"}), 403
    data = request.get_json()
    if 'bloqueo' in data:
        proveedores_collection.update_one({'_id': ObjectId(id)}, {'$set': {'bloqueo': data['bloqueo']}})
        if data['bloqueo']:
            return jsonify({"msg": "Proveedor bloqueado!"}), 200
        return jsonify({"msg": "Proveedor desbloqueado!"}), 200
    else:
        return jsonify({"msg": "Bad Request"}), 400

@application.route('/proveedores', methods=['GET'])
@jwt_required()
def get_proveedores():
    verify_jwt_in_request()
    current_user = get_jwt_identity()
    if current_user['role'] == 'admin':
        lista_proveedores = list(proveedores_collection.find({}))
        todos_proveedores = []
        for proveedor in lista_proveedores:
            proveedor['_id'] = str(proveedor['_id'])
            todos_proveedores.append(proveedor)
        return jsonify(todos_proveedores)
    proveedores = list(proveedores_collection.find({'bloqueo': False}, {'_id': False}))
    return jsonify(proveedores)

@application.route('/proveedores/busca', methods=['GET'])
@jwt_required()
def busca_proveedor():
    current_user = get_jwt_identity()
    query_params = ['nombre', 'criticidad', 'tipo_servicio']
    query = {param: request.args[param] for param in query_params if param in request.args}
    if current_user['role'] != 'admin':
        query['bloqueo'] = False
    proveedores = list(proveedores_collection.find(query, {'_id': False}))
    if not proveedores:
        return jsonify({"msg": "Not Found"}), 404
    return jsonify(proveedores)

if __name__ == '__main__':
    application.run(host="0.0.0.0", port=8080)

