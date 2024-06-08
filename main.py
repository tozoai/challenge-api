from flask import Flask, request, json, Response
from pymongo import MongoClient
from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from bson import ObjectId
from bson.json_util import dumps
from flask import jsonify


app = Flask(__name__)
app.config["DEBUG"] = True

class PydanticObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")

class Proveedores(BaseModel):
    id: int
    Nombre: str
    Razon_Social: str
    Nombre_Contato: str
    email: EmailStr
    Direccion_Fiscal: str
    Tipo_Servicio: str
    Criticidad: str
    
client = MongoClient("mongodb://localhost:5000/data?retryWrites=true&w=majority")

db = client['data'] 
collection = db['proveedores']

@app.route('/proveedores', methods=['GET'])

def get_proveedores():

    proveedores = list(collection.find())
    return jsonify(dumps(proveedores))  # convert BSON to JSON


@app.route('/', methods=['GET'])

def home():
    return '''<head>API Challenge</head><br>
      <p>This is the default API Response   </p>
      
      '''

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=20000)
