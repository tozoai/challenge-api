import flask
from flask import request, jsonify

app = flask.Flask(__name__)
app.config["DEBUG"] = True

provedores = [
    {
        "id": 1,
        "Nombre":"Fornecedor 1",
        "Razon_Social":"Razon Social 1",
        "Nombre_Contato":"Nombre del contato 1",
        "email":"email@contato1.com",
        "Direccion_Fiscal":"Direccion contato 1",
        "Tipo_Servicio":"Tipo Servicio Contato 1",
        "Criticidad":"Baja",
        "role":"usuario"
    },
    {
        "id": 2,
        "Nombre":"Nombre 2",
        "Razon_Social":"Razon Social 2",
        "Nombre_Contato":"Nombre del contato 2",
        "email":"email@contato2.com",
        "Direccion_Fiscal":"Direccion contato 2",
        "Tipo_Servicio":"Tipo Servicio Contato 2",
        "Criticidad":"Alta",
        "role":"administrador"
    }
]

@app.route('/', methods=['GET'])

def home():
    return '''<head>API Challenge</head><br>
      <p>This is the default API Response   </p>'''

@app.route('/api/v1/provedores', methods=['GET'])

def mostra_provedores():
    return jsonify(provedores)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
