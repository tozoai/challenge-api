from flask import jsonify
from flask_restful import Resource, reqparse
from flask_restful_swagger import swagger
from flask_jwt_extended import jwt_required, get_jwt_identity
from pymongo import MongoClient
from pydantic import ValidationError
from bson import ObjectId
from api.utils.rbac import role_required
from api.models.proveedor_model import Proveedor
import datetime
import os

# Initialize MongoDB
client = MongoClient(os.environ.get('MONGO_URI'))
db = client['data']
proveedores_collection = db['proveedores']

all_attributes = reqparse.RequestParser()
all_attributes.add_argument('_id', type=ObjectId, required=False, help='ID is optional except for delete and updates')
all_attributes.add_argument('nombre', type=str , required=True, help='Nombre no puede estar vacio')
all_attributes.add_argument('tipo_servicio', type=str, required=True, help='Tipo Servicio no puede estar vacio')
all_attributes.add_argument('criticidad', type=str, required=True, help='Criticidad no puede estar vacio')
all_attributes.add_argument('razon_social', type=str, required=False, help='Razon Social no puede estar vacio')
all_attributes.add_argument('nombre_contacto', type=str, required=False, help='Nombre Contacto no puede estar vacio')
all_attributes.add_argument('email', type=str, required=False, help='Email no puede estar vacio')
all_attributes.add_argument('direccion_fiscal', type=str, required=True, help='Direccion Fiscal no puede estar vacio')
all_attributes.add_argument('bloqueo', type=str, required=False, help='Bloqueo is optional')

class ProveedorResource(Resource):
    @swagger.operation(
        desc='GET Lista todos los proveedores',
        asd=Proveedor,
        nickname='getProveedores'
    )
    @jwt_required()

    def get(self):
        current_user = get_jwt_identity()
        if current_user == 'admin':
            lista_proveedores = list(proveedores_collection.find({}))
            todos_proveedores = []
            for proveedor in lista_proveedores:
                proveedor['_id'] = str(proveedor['_id'])
                todos_proveedores.append(proveedor)
            return jsonify(todos_proveedores)
        else:
            proveedores_desbloqueados = list(proveedores_collection.find({'bloqueo': False}))
            for proveedor in proveedores_desbloqueados:
                proveedor['_id'] = str(proveedor['_id'])
            return jsonify(proveedores_desbloqueados)

    @swagger.operation(
        desc='POST Crea un proveedor',
        responseClass=Proveedor,
        nickname='createProveedor'
    )
    @jwt_required()
    def post(self):
        data = all_attributes.parse_args()
        try:
            proveedor = Proveedor(**data)
            proveedores_collection.insert_one(proveedor.model_dump())
            return {'message': 'Proveedor creado con exito'}, 201
        except ValidationError:
            return {'message': 'Requisicion malformada'}, 400
    
    @swagger.operation(
        desc='PUT Actualiza un proveedor',
        responseClass=Proveedor,
        nickname='updateProveedor'
    )
    @jwt_required()
    def put(self):
        all_attributes.replace_argument('_id', type=ObjectId, required=True, help='Atributo _id es requerido para esta operacion')
        all_attributes.replace_argument('nombre', type=str, required=False, help='Nombre is optional')
        all_attributes.replace_argument('tipo_servicio', type=str, required=False, help='Tipo Servicio is optional')
        all_attributes.replace_argument('criticidad', type=str, required=False, help='Criticidad is optional')
        data = all_attributes.parse_args()
        proveedor_id = data.pop('_id', None)
       
        if not proveedor_id:
            return {'message': 'ID es necesario'}, 400
        
        if get_jwt_identity() != 'admin':
            return {'message': 'Admin privilege required'}, 403
         
        try:
            proveedor = Proveedor(**data)
            result = proveedores_collection.update_one(
                {'_id': proveedor_id},
                {'$set': proveedor.model_dump()}
            )
            if result.matched_count == 0:
                return {'message': 'Proveedor not found'}, 404
            return {'message': 'Proveedor actualizado con exito'}, 200
        except ValidationError:
            return {'message': 'Requisicion malformada'}, 400
    
    @swagger.operation(
        desc='DELETE elimina un proveedor',
        responseClass=Proveedor,
        nickname='deleteProveedor'
    )
    @jwt_required()
    @role_required('admin')
    def delete(self):
        all_attributes.replace_argument('_id', type=ObjectId, required=True, help='Atributo _id es requerido para esta operacion')
        all_attributes.replace_argument('nombre', type=str, required=False, help='Nombre is optional')
        all_attributes.replace_argument('tipo_servicio', type=str, required=False, help='Tipo Servicio is optional')
        all_attributes.replace_argument('criticidad', type=str, required=False, help='Criticidad is optional')
        data = all_attributes.parse_args()
        proveedor_id = data.pop('_id', None)
        
        if not proveedor_id:
            return {'message': '_id es necesario'}, 400
        
        result = proveedores_collection.delete_one({'_id': proveedor_id})
        if result.deleted_count == 0:
            return {'message': 'Proveedor not found'}, 404
        return {'message': 'Proveedor eliminado con exito'}, 200