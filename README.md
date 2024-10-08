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

No hay usuarios en banco de datos entonces temos que crealo, para hacer-lo vamos usar el endpoint `/usuarios/registro`

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

[![privileged-auth](https://i.imgur.com/wiktB2U.png)](https://i.imgur.com/wiktB2U.png)

Despues que el primer usuario fue creado en el banco, es possible autenticar y empezar a crear los proveedores y usuarios:

Es possible hacer eso usando la interface de documentacion swagger acediendo la URI `/docs` con un web browser:


==[http://localhost:8080/docs](http://localhost:8080/docs)==

Si todo va bien, la pagina de documentacion debe ser mostrada:

[![Flask Logo](https://i.imgur.com/WuhpNY0.png)](https://127.0.0.1:8080/docs)


Abajo temos un ejemplo de como autenticar con el usuario que creamos

[![privileged-auth](https://i.imgur.com/6hEgqo5.png)](https://i.imgur.com/6hEgqo5.png)

Entonces podemos crear dos nuevos proveedores, un bloqueado y otro no (Bloqueo = true)

[![privileged-auth](https://i.imgur.com/GOKEOVa.png)](https://i.imgur.com/GOKEOVa.png)

Crear un proveedor sin bloqueo

[![privileged-auth](https://i.imgur.com/qih6Hks.png)](https://i.imgur.com/qih6Hks.png)

Despues de autenticar, con el token JWT se puede crear usuarios sin privilegios

[![privileged-auth](https://i.imgur.com/o6DxqM9.png)](https://i.imgur.com/o6DxqM9.png)

Y usar-lo para autenticar

[![privileged-auth](https://i.imgur.com/5Z0IDpY.png)](https://i.imgur.com/5Z0IDpY.png)

Con el usuario sin privilegios vamos listar los proveedores y ver que solo podemos ver los proveedores no bloqueados

[![privileged-auth](https://i.imgur.com/gcnwlRG.png)](https://i.imgur.com/gcnwlRG.png)

Ahora vamos autenticar con un usuario administrador

[![privileged-auth](https://i.imgur.com/6hEgqo5.png)](https://i.imgur.com/6hEgqo5.png)

Y listar los proveedores, el admin puede listar todos los proveedores

[![privileged-auth](https://i.imgur.com/MaNWfTt.png)](https://i.imgur.com/MaNWfTt.png)

Asi podemos eliminar un proveedor, pero es necessario saber el _id 

[![privileged-auth](https://i.imgur.com/2lh1Nor.png)](https://i.imgur.com/2lh1Nor.png)

Tambien para alterar el atributo bloqueo, es necessario tener el "admin" role

[![privileged-auth](https://i.imgur.com/LsuwSPJ.png)](https://i.imgur.com/LsuwSPJ.png)

Y con admin 

[![privileged-auth](https://i.imgur.com/C642LCz.png)](https://i.imgur.com/C642LCz.png)


Todas las acciones ejecutadas arriba pueden ser ejecutadas por la interface swagger en /docs





