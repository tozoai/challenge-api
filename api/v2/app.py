from flask import Flask
from flask_restful import Api
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint
from flask_jwt_extended import JWTManager
from api.utils.swagger import get_swagger_docs
from api.resources.usuario import UsuarioResource, UsuarioAuthResource
from api.resources.proveedor import ProveedorResource
import os

app = Flask(__name__)

# Swagger UI configuration
SWAGGER_URL = '/swagger'
API_URL = '/static/swagger.json'
swaggerui_blueprint = get_swaggerui_blueprint(SWAGGER_URL, API_URL, config={'app_name': "Challenge-API"})
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

# Flask-Restful CORS API
CORS(app)
api = Api(app)
get_swagger_docs(api, app)
jwt = JWTManager(api.app)
api.app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY')
#import ipdb; ipdb.set_trace()
# Register Resources
api.add_resource(UsuarioResource, '/usuarios')
api.add_resource(UsuarioAuthResource, '/usuarios/auth')
api.add_resource(ProveedorResource, '/proveedores')

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080, threaded=True, debug=True)
