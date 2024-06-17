from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, verify_jwt_in_request
from flask_limiter.wrappers import Limit
from werkzeug.security import generate_password_hash, check_password_hash
from flask_limiter import Limiter, RateLimitExceeded
from flask_limiter.wrappers import Limit
from flask_limiter.util import get_remote_address
from pymongo import MongoClient
from bson.objectid import ObjectId
import os

flask_app = Flask(__name__)

flask_app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY')
if not flask_app.config['JWT_SECRET_KEY']:
    raise RuntimeError('Environment variable JWT_SECRET_KEY is not set, exiting...')

flask_app.config['MONGO_URI'] = os.environ.get('MONGO_URI')
if not flask_app.config['MONGO_URI']:
    raise RuntimeError('Environment variable MONGO_URI is not set, exiting...')

jwt = JWTManager(flask_app)

client = MongoClient(flask_app.config['MONGO_URI'])
db = client['data']
usuarios_collection = db['usuarios']
proveedores_collection = db['proveedores']

# Models

class Usuario:
    def __init__(self, username, password, role):
        self.username = username
        self.password = generate_password_hash(password)
        self.role = role
        #self.creation_data = datetime.datetime.now()
        #self.parent_user = parent_user
        #self.last_login = None
        
    def save_to_db(self):
        usuarios_collection.insert_one({
            'username': self.username,
            'password': self.password,
            'role': self.role
            # 'creation_data': self.creation_data,
            # 'parent_user': self.parent_user,
            # 'last_login': self.last_login
        })

class Proveedor:
    def __init__(self, nombre, razon_social, nombre_contato, email, direccion_fiscal, tipo_servicio, criticidad, bloqueo):
        self.nombre = nombre
        self.razon_social = razon_social
        self.nombre_contato = nombre_contato
        self.email = email
        self.direccion_fiscal = direccion_fiscal
        self.tipo_servicio = tipo_servicio
        self.criticidad = criticidad
        self.bloqueo = bloqueo
        #self.fecha_creacion = datetime.datetime.now()
        #self.usuario_creacion = sanitize_get_jwt().get('username')
        #self.fecha_modificacion = None
 
    def save_to_db(self):
        result = proveedores_collection.insert_one(self.__dict__) 
        self._id = result.inserted_id 

# Security

def sanitize_get_jwt():
    try:
        return get_jwt_identity()
    except Exception:
        return None

# Add Rate Limit

limiter = Limiter(
    get_remote_address,
    app=flask_app,
    default_limits=["200 per day", "5 per minute"]
)

@flask_app.after_request 
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

@flask_app.route('/auth', methods=['POST'])
def login():
    try: 
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        user = authenticate_user(username, password)
        if not user:
            return jsonify({"msg": "Bad username or password"}), 401
        access_token = create_access_token(identity={'username': user['username'], 'role': user['role']})
        return jsonify(access_token=access_token), 200            
    except RateLimitExceeded:
        return jsonify({"msg": "Rate limit exceeded"}), 429

@flask_app.route('/auth', methods=['PUT'])
@limiter.limit("3 per minute")
def create_user():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    role = data.get('role')
    if get_user(username):
        return jsonify({"msg": "User already exists"}), 400
    
    # Primero usuario no necessita auth
    if usuarios_collection.count_documents({}) == 0:
        new_user = Usuario(username, password, "admin")
        new_user.save_to_db()
        return jsonify({"msg": "Admin user created successfully"}), 201
    
    current_user = sanitize_get_jwt()
    if current_user is None or current_user.get('role') != 'admin':
       return jsonify({"msg": "Admin privilege required"}), 403
    
    new_user = Usuario(username, password, role)
    new_user.save_to_db()
    return jsonify({"msg": "User created successfully"}), 201

@flask_app.route('/proveedores', methods=['PUT'])
@jwt_required()
def create_proveedor():
    current_user = get_jwt_identity()
    if current_user['role'] != 'admin':
        return jsonify({"msg": "Admin privilege required"}), 403
    data = request.get_json()
    proveedor = Proveedor(**data)
    proveedor.save_to_db()
    return jsonify({"msg": "Created successfully"}), 201

@flask_app.route('/proveedores/atualiza/<id>', methods=['PATCH'])
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

@flask_app.route('/proveedores', methods=['GET'])
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

@flask_app.route('/proveedores/busca', methods=['GET'])
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
    flask_app.run(host="0.0.0.0", port=8080)