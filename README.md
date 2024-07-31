# Challenge-API

[![Flask Logo](https://flask.palletsprojects.com/en/1.1.x/_images/flask-logo.png)](https://flask.palletsprojects.com/en/1.1.x/)

Challenge-API es una API con autenticacion JWT y CRUD de proveedores y usuarios y usa los seguientes middlewares.

  - Flask-RESTful
  - Flask-JWT-Extended
  - Flask-RESTful-Swagger
  - Flask_CORS
  - PyDantic
  - MongoDB
  - Docker Compose

## Installation

Clone ese repo:

```bash
$ git clone https://github.com/tozoai/challenge-api.git
````

Ejecuta-lo via docker-compose

```bash
$ cd challenge-api
$ docker compose up
```

Dos containers inician, siendo un webserver con el Challenge-API y un MongoDB latest

```bash
$ docker ps
IMAGE               COMMAND                 PORTS                      NAMES
challenge-api-web   "python3 api/app.py"     0.0.0.0:8080->8080/tcp     challenge-api-web-1
mongo               "docker-entrypoint.s…"   0.0.0.0:27017->27017/tcp   challenge-api-db-1
```

No hay usuarios en banco de datos entonces temos que crealo, para hacer-lo vamos usar el endpoint /usuarios/registro

```bash
$ curl -X 'POST' \
  'http://localhost:8080/usuarios/registro' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "username": "root",
  "password": "password"
}'
```

La respuesta deve ser:
```
    "message": "Nuevo admin creado con exito"
````

Despues que el primer usuario fue creado en el banco, es possible autenticar y empezar a crear los proveedores y usuarios:

Es possible hacer eso usando la interface de documentacion swagger acediendo la URI /docs con un web browser:

http://localhost:8080/docs

[![Documentation](#)](https://raw.githubusercontent.com/tozoai/challenge-api/tree/main/img/Screenshot.png)




