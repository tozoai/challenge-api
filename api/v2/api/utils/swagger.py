from flask_restful_swagger import swagger

def get_swagger_docs(api, app):
    api = swagger.docs(api, apiVersion='1.0', api_spec_url='/api/swagger.json')
    return api
