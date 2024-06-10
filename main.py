from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, verify_jwt_in_request
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient
from config import config
import os

app = Flask(__name__)

env = os.environ.get('FLASK_ENV', 'default')
app.config.from_object(config[env])

jwt = JWTManager(app)

client = MongoClient('mongodb://localhost:5000/data?retryWrites=true&w=majority')
db = client['data']
usuarios_collection = db['usuarios']
proveedores_collection = db['proveedores']

class Usuario:
    def __init__(self, username, password, role):
        self.username = username
        self.password = generate_password_hash(password)
        self.role = role

    def save_to_db(self):
        usuarios_collection.insert_one({
            'username': self.username,
            'password': self.password,
            'role': self.role
        })

def get_user(username):
    return usuarios_collection.find_one({'username': username})

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
        self._id = None  

    def save_to_db(self):
        result = proveedores_collection.insert_one(self.__dict__) 
        self._id = result.inserted_id 

    def save_to_db(self):
        proveedores_collection.insert_one(self.__dict__)

def authenticate_user(username, password):
    user = get_user(username)
    if user and check_password_hash(user['password'], password):
        return user
    return None

@app.route('/auth', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    user = authenticate_user(username, password)
    if not user:
        return jsonify({"msg": "Bad username or password"}), 401
    access_token = create_access_token(identity={'username': user['username'], 'role': user['role']})
    return jsonify(access_token=access_token), 200

@app.route('/auth', methods=['PUT'])
def create_user():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    role = data.get('role')
    if get_user(username):
        return jsonify({"msg": "User already exists"}), 400

    # Allow creating the first user (admin) without authentication
    if usuarios_collection.count_documents({}) == 0:
        new_user = Usuario(username, password, role)
        new_user.save_to_db()
        return jsonify({"msg": "Admin user created successfully"}), 201

    # For subsequent users, require admin role
    current_user = get_jwt_identity()
    if not current_user or current_user['role'] != 'admin':
        return jsonify({"msg": "Admin privilege required"}), 403

    new_user = Usuario(username, password, role)
    new_user.save_to_db()
    return jsonify({"msg": "User created successfully"}), 201

@app.route('/proveedores', methods=['PUT'])
@jwt_required()
def create_supplier():
    current_user = get_jwt_identity()
    if current_user['role'] != 'admin':
        return jsonify({"msg": "Admin privilege required"}), 403
    data = request.get_json()
    supplier = Proveedor(**data)
    supplier.save_to_db()
    return jsonify({"msg": "Supplier created successfully"}), 201

@app.route('/proveedores', methods=['GET'])
@jwt_required()
def get_suppliers():
    verify_jwt_in_request()
    current_user = get_jwt_identity()
    if current_user['role'] != 'admin':
        proveedores_desbloqueados = list(proveedores_collection.find({'bloqueo': False}, {'_id': False}))
        return jsonify(proveedores_desbloqueados)

    suppliers = list(proveedores_collection.find({}, {'_id': False}))
    return jsonify(suppliers)

@app.route('/proveedores/busca', methods=['GET'])
@jwt_required()
def search_supplier():
    current_user = get_jwt_identity()
    query_params = ['nombre', 'criticidad', 'tipo_servicio']
    
    query = {param: request.args[param] for param in query_params if param in request.args}

    if current_user['role'] != 'admin':
        query['bloqueo'] = False

    suppliers = list(proveedores_collection.find(query, {'_id': False}))
    
    if not suppliers:
        return jsonify({"msg": "Suppliers not found"}), 404
        
    return jsonify(suppliers)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=80)