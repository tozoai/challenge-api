from flask import request, jsonify
from flask_restful import Resource, reqparse
from flask_restful_swagger import swagger
from api.models.proveedor_model import Proveedor
from pymongo import MongoClient
import os
from api.utils.rbac import role_required

# Initialize MongoDB
client = MongoClient(os.environ.get('MONGO_URI'))
db = client['data']
proveedores_collection = db['proveedores']

proveedor_parser = reqparse.RequestParser()
proveedor_parser.add_argument('nombre', type=str, required=True, help='Nombre cannot be blank')
proveedor_parser.add_argument('razon_social', type=str, required=True, help='Razon Social cannot be blank')
proveedor_parser.add_argument('nombre_contacto', type=str, required=True, help='Nombre Contacto cannot be blank')
proveedor_parser.add_argument('email', type=str, required=True, help='Email cannot be blank')
proveedor_parser.add_argument('direccion_fiscal', type=str, required=True, help='Direccion Fiscal cannot be blank')
proveedor_parser.add_argument('tipo_servicio', type=str, required=True, help='Tipo Servicio cannot be blank')
proveedor_parser.add_argument('criticidad', type=str, required=True, help='Criticidad cannot be blank')
proveedor_parser.add_argument('bloqueo', type=bool, required=False, help='Bloqueo is optional')
proveedor_parser.add_argument('parent_user', type=str, required=True, help='Parent user cannot be blank')

class ProveedorResource(Resource):
    @swagger.operation(
        notes='Lista todos los proveedores',
        responseClass=Proveedor.__name__,
        nickname='get'
    )
    @role_required('admin')
    def get(self):
        lista_proveedores = proveedores_collection.find({})
        todos_proveedores = []
        for proveedor in lista_proveedores:
            proveedor['_id'] = str(proveedor['_id'])
            todos_proveedores.append(proveedor)
        #import ipdb; ipdb.set_trace()    
        return jsonify(todos_proveedores)

    @swagger.operation(
        notes='Deleta un proveedor por el id',
        responseMessages=[
            {
                'code': 204,
                'message': 'Proveedor deleted'
            },
            {
                'code': 404,
                'message': 'Proveedor not found'
            }
        ]
    )
    def delete(self, id):
        result = proveedores_collection.delete_one({'_id': id})
        if result.deleted_count == 0:
            return {'message': 'Proveedor not found'}, 404
        return '', 204

    @swagger.operation(
        notes='Update a Proveedor by nombre',
        responseClass=Proveedor.__name__,
        nickname='put'
    )
    def put(self, nombre):
        data = proveedor_parser.parse_args()
        updated_proveedor = {
            'nombre': data['nombre'],
            'razon_social': data['razon_social'],
            'nombre_contacto': data['nombre_contacto'],
            'email': data['email'],
            'direccion_fiscal': data['direccion_fiscal'],
            'tipo_servicio': data['tipo_servicio'],
            'criticidad': data['criticidad'],
            'bloqueo': data['bloqueo'] if data['bloqueo'] is not None else False,
            'parent_user': data['parent_user'],
            'fecha_creacion': datetime.datetime.now()
        }
        result = proveedores_collection.update_one({'nombre': nombre}, {'$set': updated_proveedor})
        if result.matched_count == 0:
            return {'message': 'Proveedor not found'}, 404
        return updated_proveedor

    @swagger.operation(
        notes='Create a new Proveedor',
        responseClass=Proveedor.__name__,
        nickname='post'
    )
    def post(self):
        data = proveedor_parser.parse_args()
        new_proveedor = {
            'nombre': data['nombre'],
            'razon_social': data['razon_social'],
            'nombre_contacto': data['nombre_contacto'],
            'email': data['email'],
            'direccion_fiscal': data['direccion_fiscal'],
            'tipo_servicio': data['tipo_servicio'],
            'criticidad': data['criticidad'],
            'bloqueo': data['bloqueo'] if data['bloqueo'] is not None else False,
            'parent_user': data['parent_user'],
            'fecha_creacion': datetime.datetime.now()
        }
        proveedores_collection.insert_one(new_proveedor)
        return new_proveedor, 201
