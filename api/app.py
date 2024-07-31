from flask import Flask
from flask_restful import Api
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint
from flask_jwt_extended import JWTManager
from api.resources.usuario import UsuarioResource, UsuarioAuthResource, UsuarioAuthSetupResource
from api.resources.proveedor import ProveedorResource
import os

app = Flask(__name__)

app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY')
app.config['MONGO_URI'] = os.environ.get('MONGO_URI')
if not app.config['MONGO_URI'] or not app.config['JWT_SECRET_KEY']:
    raise RuntimeError('Environment variables MONGO_URI or JWT_SECRET_KEY not set, exiting...')

# Swagger UI configuration
SWAGGER_URL = '/docs'
API_URL = '/static/swagger.json'
swaggerui_blueprint = get_swaggerui_blueprint(SWAGGER_URL, API_URL, config={'app_name': "Challenge-API"})

# Flask-Restful CORS API
CORS(app)
api = Api(app)
jwt = JWTManager(api.app)
api.app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY')

@api.app.after_request 
def add_security_headers(response):
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    #response.headers['Content-Security-Policy'] = "default-src 'self'; frame-ancestors 'none'; object-src 'none'; base-uri 'self';"
    response.headers['Referrer-Policy'] = 'no-referrer'
    return response

# Register Resources
api.add_resource(UsuarioResource, '/usuarios')
api.add_resource(UsuarioAuthResource, '/usuarios/auth')
api.add_resource(UsuarioAuthSetupResource, '/usuarios/registro')
api.add_resource(ProveedorResource, '/proveedores')

api.app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080, threaded=True)