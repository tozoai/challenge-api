from flask import Flask, request, jsonify
from flask_restful import Api, Resource
from flask_swagger_ui import get_swaggerui_blueprint
from flask_restful_swagger import swagger
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, verify_jwt_in_request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient
import os
import datetime
import re

app = Flask(__name__)

# Configurations
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY')
app.config['MONGO_URI'] = os.environ.get('MONGO_URI')
if not app.config['MONGO_URI'] or not app.config['JWT_SECRET_KEY']:
    raise RuntimeError('Environment variables not set, exiting...')

# Initialize MongoDB
client = MongoClient(app.config['MONGO_URI'])
db = client['data']
usuarios_collection = db['usuarios']
proveedores_collection = db['proveedores']

# Initialize the Flask extensions
api = Api(app)
jwt = JWTManager(app)
limiter = Limiter(key_func=get_remote_address, app=app)

SWAGGER_URL = '/swagger'
API_URL = '/static/swagger.json'
swaggerui_blueprint = get_swaggerui_blueprint(SWAGGER_URL, API_URL, config={'app_name': "Hello World API"})
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

class Usuario(Resource):
    @jwt_required()  # JWT authentication required
    @limiter.limit("5 per minute")  # Rate limiting
    
    def __init__(self, username=None, password=None, role=None, fecha_creacion=None, parent_user=None):
        self.username = username
        self.password = password
        self.role = role if role else ''
        self.fecha_creacion = fecha_creacion if fecha_creacion else datetime.datetime.now()
        self.parent_user = parent_user
        
    def get(self):
        current_user = get_jwt_identity()
        return {"message": f"Hello, {current_user}!"}

    def save_to_db(self):
        password_hash = generate_password_hash(self.password)
        usuarios_collection.insert_one({
            'username': self.username,
            'password': password_hash,
            'role': self.role,
            'fecha_creacion': self.fecha_creacion,
            'parent_user': self.parent_user
        })

api.add_resource(Usuario, '/')

@app.route('/auth', methods=['POST'])
def login():
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400
    
    def get_user(username):
        return usuarios_collection.find_one({'username': username})

    def authenticate_user(username, password):
        user = get_user(username)
        if user and check_password_hash(user['password'], password):
            return user
        return None

    response = request.get_json()
    username = response.get('username')
    password = response.get('password')
    user = authenticate_user(username, password)
    
    if not user:
        return jsonify({"msg": "Bad username or password"}), 401
    access_token = create_access_token(identity={'username': user['username'], 'role': user['role']})
    return jsonify(access_token=access_token), 200

@app.route('/auth/create', methods=['POST'])
@limiter.limit("20 per minute")
def create_user():
    response = request.get_json()
    
    # Username Validation
    def validate_username(username):
        if not username:
          return False
        pattern = r'[A-Za-z0-9]{4,12}$'
        return re.match(pattern, username) is not None
    
    #def sanitize_get_jwt():
    #   try:
    #        verify_jwt_in_request()
    #        return get_jwt_identity()
    #    except Exception:
    #        return jsonify({"msg": "Bad request"}), 400

    # Password Complexity enabled
    def validate_password(password):
        if not password:
            return False
        pattern = (r'(?=\D*\d)(?=[^A-Z]*[A-Z])(?=[^a-z]*[a-z])[A-Za-z0-9]{10,}$')
        return re.match(pattern, password) is not None

    if response is None:
        return jsonify({"msg": "Bad request"}), 400
    
    username = response.get('username')
    password = response.get('password')
    role = response.get('role')
    
    if not validate_username(username):
        return jsonify({"msg": "Invalid Username"}), 400
    
    if not validate_password(password):
        return jsonify({"msg": "Password complexity not met"}), 400
    
    verify_jwt_in_request()
    current_user = get_jwt_identity()
     
    if not current_user:
        if usuarios_collection.count_documents({}) == 0:
            new_user = Usuario(username=username, password=password, role="admin", fecha_creacion=datetime.datetime.now(), parent_user="root")
            new_user.save_to_db()
            return jsonify({"msg": "Admin user created successfully"}), 201
        return jsonify({"msg": "Admin privilege required"}), 403
    
    import ipdb; ipdb.set_trace()
    if current_user['role'] != 'admin':
        return jsonify({"msg": "Admin privilege required"}), 403
    
    existing_user = usuarios_collection.find_one({'username': username})
    
    if existing_user:
        return jsonify({"msg": "User already exists"}), 402
    if username == password:
        return jsonify({"msg": "Username cannot be the same as password"}), 402
    #try:    
    new_user = Usuario(username=username, password=password, role=role, parent_user=current_user['username'])
    new_user.save_to_db()
    #except: 
    return jsonify({"msg": "User created successfully"}), 201

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080, threaded=True)