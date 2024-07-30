# Challenge-API

[![Build Status](https://flask.palletsprojects.com/en/1.1.x/_images/flask-logo.png)](https://flask.palletsprojects.com/en/1.1.x/)

Challenge-API es una API con autenticacion JWT y CRUD de proveedores y usuarios.
  - Flask-RESTful
  - Flask-JWT-Extended
  - Flask-RESTful-Swagger
  - Flask_CORS
  - PyDantic
  - MongoDB
  - Docker Compose

## Installation

Build docker image:

```bash

docker build -t challenge-api .
docker image (get image id)
docker run --name challenge-api -d challenge-api

docker pull mongo:latest
docker run mongo:latest

```

To set proper keys create as environment variables

```
JWT_SECRET_KEY=your_secret_key_here
MONGO_URI=mongodb://localhost:27017
```

##### Then install install Requirements
```sh
$ pip install -r requirements.txt 
$ flask run
```
Navigate to your server address in your preferred browser.
```sh
127.0.0.1:5000
```
 

![App](screenshot.png)

##### Other endpoints and customizations can then be added, THIS IS JUST A BASIC BOILERPLATE
 
 ```sh
```


##### Database migrations can also be made
```sh
$ flask db init
$ flask db migrate
$ flask db upgrade
```

### Development
Want to contribute? Great!

Feel free to reachout
 

### Todos

 - Implementation of marshmallow (for object serialization/deserialization)
 - Addition of JWT


## Autenticación
- **POST /auth**: Inicia sesión un usuario y devuelve un token JWT.
```
curl -X POST https://wjyegimi32.us-east-1.awsapprunner.com/auth \
     -H "Content-Type: application/json" \
     -d '{
           "username": "admin",
           "password": "password",
           "role": "admin"
         }'
```

- **PUT /auth**: Crea un nuevo usuario. Si no existen usuarios, se crea un usuario administrador. Se requiere privilegio de administrador para la creación de usuarios posteriores. Limitado a 20 solicitudes por minuto.

## Proveedores
```
curl -X PUT https://wjyegimi32.us-east-1.awsapprunner.com/auth \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer [JWT_TOKEN]"
     -d '{
           "username": "usuario",
           "password": "password",
           "role": "role"
         }'
```

- **GET /proveedores**: Recupera una lista de todos los proveedores. Los usuarios administradores obtienen todos los proveedores, los usuarios no administradores obtienen solo los proveedores no bloqueados. Limitado a 20 solicitudes por minuto.

```
curl -X GET https://wjyegimi32.us-east-1.awsapprunner.com/proovedores \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer [JWT_TOKEN]"
```

- **GET /proveedores/busca**: Busca proveedores en función de parámetros de consulta (nombre, criticidad, tipo de servicio). Los usuarios administradores obtienen todos los proveedores coincidentes, los usuarios no administradores obtienen solo los proveedores no bloqueados. Limitado a 20 solicitudes por minuto.

```
curl -X GET https://wjyegimi32.us-east-1.awsapprunner.com/proovedores/busca/nombre=Cloudflare&criticidad=Alta&tipo_servicio=TI_ \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer [JWT_TOKEN]"
```


- **PUT /proveedores**: Crea un nuevo proveedor. Requiere privilegio de administrador. Limitado a 20 solicitudes por minuto.

```
curl -X PUT https://wjyegimi32.us-east-1.awsapprunner.com/proveedores \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer [JWT_TOKEN]"
     -d '{
           "nombre": "Cloudflare",
           "criticidad": "Alta",
           "direccion_fiscal": "Sao Jose SC BR",
           "email": "cloudflare@cloudflare.com",
           "nombre_contacto": "Mario Masca",
           "razon_social": "Cloudflare Enterprise",
           "tipo_servicio": "TI"
           }'
```

- **POST /proveedores**: Actualiza el estado de bloqueo de un proveedor. Requiere privilegio de administrador. Limitado a 20 solicitudes por minuto.

```
curl -X POST https://wjyegimi32.us-east-1.awsapprunner.com/proovedores \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer [JWT_TOKEN]"
     -d '{
           "_id_": "9998ee04e85ce06a53a4a82c",
           "bloqueo": "true"
           }'
```



Run the app:

Set AWS Elastic Container Registry and push to AWS ECR
```
(Get-ECRLoginCommand).Password | docker login --username AWS --password-stdin 471112676018.dkr.ecr.us-east-2.amazonaws.com
docker build -t challenge-image-repository .
docker tag challenge-image-repository:latest 471112676018.dkr.ecr.us-east-2.amazonaws.com/challenge-image-repository:latest
docker push 471112676018.dkr.ecr.us-east-2.amazonaws.com/challenge-image-repository:latest
```