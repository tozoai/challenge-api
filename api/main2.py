from flask import Flask, request, jsonify
from flask_restful import Api, Resource
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, verify_jwt_in_request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient
from pydantic import BaseModel, ValidationError
from bson.objectid import ObjectId
import datetime
import os
import re
from flask_swagger_ui import get_swaggerui_blueprint

app = Flask(__name__)
api = Api(app)

# Configurations
api.app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY')
api.app.config['MONGO_URI'] = os.environ.get('MONGO_URI')
if not api.app.config['MONGO_URI'] or not api.app.config['JWT_SECRET_KEY']:
    raise RuntimeError('Environment variables not set, exiting...')

# Initialize JWT
jwt = JWTManager(api.app)

# Initialize MongoDB
client = MongoClient(api.app.config['MONGO_URI'])
db = client['data']
usuarios_collection = db['usuarios']
proveedores_collection = db['proveedores']

# Models
class Usuario(BaseModel):
    username: str
    password: str
    role: str
    fecha_creacion: datetime.datetime = datetime.datetime.now()
    parent_user: str

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
    criticidad: str
    bloqueo: bool = False
    parent_user: str
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

def sanitize_string(input_string):
    pattern = r'[^a-zA-Z0-9\s.,;:!?\-_@#%&()+=]'
    sanitized_string = re.sub(pattern, '', input_string)
    return sanitized_string

# Rate Limiting
limiter = Limiter(
    get_remote_address,
    app=api.app,
    default_limits=["1000 per day", "30 per minute"]
)

# Security Headers
@api.app.after_request 
def add_security_headers(response):
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['Content-Security-Policy'] = "default-src 'self'"
    response.headers['Referrer-Policy'] = 'no-referrer'
    return response

# Swagger UI setup
SWAGGER_URL = '/swagger'
API_URL = 'static/swagger.json'
swaggerui_blueprint = get_swaggerui_blueprint(SWAGGER_URL, API_URL, config={'app_name': "asd"})
api.app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

# Auth
def get_user(username):
    return usuarios_collection.find_one({'username': username})

def authenticate_user(username, password):
    user = get_user(username)
    if user and check_password_hash(user['password'], password):
        return user
    return None

def validate_username(username):
    if not username:
        return False
    pattern = r'[A-Za-z0-9]{4,12}$'
    return re.match(pattern, username) is not None

def validate_password(password):
    if not password:
        return False
    pattern = (r'(?=\D*\d)(?=[^A-Z]*[A-Z])(?=[^a-z]*[a-z])[A-Za-z0-9]{10,}$')
    return re.match(pattern, password) is not None

class Auth(Resource):
    @limiter.limit("20 per minute")
    def post(self):
        response = request.get_json()
        username = response.get('username')
        password = response.get('password')
        user = authenticate_user(username, password)
        if not user:
            return jsonify({"msg": "Bad username or password"}), 401
        access_token = create_access_token(identity={'username': user['username'], 'role': user['role']})
        return jsonify(access_token=access_token), 200            

    @limiter.limit("20 per minute")
    def put(self):
        response = request.get_json()
        if response is None:
            return jsonify({"msg": "Bad request"}), 400
        username = response.get('username')
        password = response.get('password')
        role = response.get('role')
        if not validate_username(username):
            return jsonify({"msg": "Invalid Username"}), 400
        if not validate_password(password):
            return jsonify({"msg": "Password complexity not met"}), 400
        current_user = sanitize_get_jwt()
        if not current_user:
            if usuarios_collection.count_documents({}) == 0:
                new_user = Usuario(username=username, password=password, role="admin", fecha_creacion=datetime.datetime.now(), parent_user="root")
                new_user.save_to_db()
                return jsonify({"msg": "Admin user created successfully"}), 201
            return jsonify({"msg": "Admin privilege required"}), 403
        if current_user['role'] != 'admin':
            return jsonify({"msg": "Admin privilege required"}), 403
        existing_user = usuarios_collection.find_one({'username': username})
        if existing_user:
            return jsonify({"msg": "User already exists"}), 402
        if username == password:
            return jsonify({"msg": "Username cannot be the same as password"}), 402
        try:    
            new_user = Usuario(username=username, password=password, role=role, parent_user=current_user['username'])
            new_user.save_to_db()
        except ValidationError:
            return jsonify({"msg": "Bad request"}), 400
        return jsonify({"msg": "User created successfully"}), 201

class Proveedores(Resource):
    @limiter.limit("20 per minute")
    @jwt_required()
    def put(self):
        current_user = get_jwt_identity()
        if current_user['role'] != 'admin':
            return jsonify({"msg": "Admin privilege required"}), 403
        response = request.get_json()
        parent_user = current_user['username']
        for key, value in response.items():
            response[key] = sanitize_string(value)
        response = {**response, 'parent_user': parent_user}
        try:
            proveedor = Proveedor(**response)
            proveedor.save_to_db()
            return jsonify({"msg": "Created successfully"}), 201
        except ValidationError:
            return jsonify({"msg": "Bad request"}), 400

    @limiter.limit("20 per minute")
    @jwt_required()
    def post(self):
        verify_jwt_in_request()
        current_user = get_jwt_identity()
        if current_user['role'] != 'admin':
            return jsonify({"msg": "Admin privilege required"}), 403
        req = request.get_json()
        if not req.get('_id') or 'bloqueo' not in req:
            return jsonify({"msg": "Bad Request"}), 400
        id = req['_id']
        try:
            proveedores_collection.update_one({'_id': ObjectId(id)}, {'$set': {'bloqueo': req['bloqueo']}})
            if req['bloqueo']:
                return jsonify({"msg": "bloqueo cambiado!"}), 200
        except ValidationError:
            return jsonify({"msg": "Bad Request"}), 400

    @limiter.limit("20 per minute")
    @jwt_required()
    def get(self):
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

class BuscaProveedor(Resource):
    @limiter.limit("20 per minute")
    @jwt_required()
    def get(self):
        current_user = get_jwt_identity()
        query_params = ['nombre', 'criticidad', 'tipo_servicio']
        if not any(param in request.args for param in query_params):
            return jsonify({"msg": "Bad Request"}), 400
        query = {}
        for param in query_params:
            if param in request.args:
                query[param] = {'$regex': request.args[param], '$options': 'i'}
        if current_user['role'] == 'admin':
            proveedores = list(proveedores_collection.find(query, {'_id': False}))
        else:
            proveedores = list(proveedores_collection.find(query, {'bloqueo': False}, {'_id': False}))
        if not proveedores:
            return jsonify({"msg": "Not Found"}), 404
        return jsonify(proveedores)

# Adding resources to the API
api.add_resource(Auth, '/auth')
api.add_resource(Proveedores, '/proveedores')
api.add_resource(BuscaProveedor, '/proveedores/busca')

api.app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL, name='asd')

if __name__ == '__main__':
    api.app.run(host="0.0.0.0", port=8080, threaded=True)