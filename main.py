from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, verify_jwt_in_request
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient
from config import config
from bson.objectid import ObjectId
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
 
    def save_to_db(self):
        result = proveedores_collection.insert_one(self.__dict__) 
        self._id = result.inserted_id 

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

    # Primero usuario no necessita auth
    if usuarios_collection.count_documents({}) == 0:
        new_user = Usuario(username, password, role)
        new_user.save_to_db()
        return jsonify({"msg": "Admin user created successfully"}), 201
    current_user = get_jwt_identity()
    if not current_user or current_user['role'] != 'admin':
        return jsonify({"msg": "Admin privilege required"}), 403
    new_user = Usuario(username, password, role)
    new_user.save_to_db()
    return jsonify({"msg": "User created successfully"}), 201

@app.route('/proveedores', methods=['PUT'])
@jwt_required()
def create_proveedor():
    current_user = get_jwt_identity()
    if current_user['role'] != 'admin':
        return jsonify({"msg": "Admin privilege required"}), 403
    data = request.get_json()
    proveedor = Proveedor(**data)
    proveedor.save_to_db()
    return jsonify({"msg": "Created successfully"}), 201

@app.route('/proveedores/atualiza/<id>', methods=['PUT'])
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

@app.route('/proveedores', methods=['GET'])
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

@app.route('/proveedores/busca', methods=['GET'])
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
    app.run(host="0.0.0.0", port=80)