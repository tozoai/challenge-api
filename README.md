# challenge-api

Stack Python + Flask + MongoDB + Docker


Github Actions -> AWS ECR -> AWS App Runner

## Descripción

API RESTful para la gestión de proveedores. Los usuarios pueden iniciar sesión, buscar, crear y bloquear proveedores. Los usuarios administradores pueden crear y buscar proveedores, así como bloquear proveedores. Los usuarios no administradores solo pueden buscar y crear proveedores. Los usuarios no administradores solo pueden ver proveedores no bloqueados.



## Autenticación
- **POST /auth**: Inicia sesión un usuario y devuelve un token JWT. Limitado a 20 solicitudes por minuto.
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
MONGO_URI=mongodb://localhost:5000
```

Run the app:

Set AWS Elastic Container Registry and push to AWS ECR
```
(Get-ECRLoginCommand).Password | docker login --username AWS --password-stdin 471112676018.dkr.ecr.us-east-2.amazonaws.com
docker build -t challenge-image-repository .
docker tag challenge-image-repository:latest 471112676018.dkr.ecr.us-east-2.amazonaws.com/challenge-image-repository:latest
docker push 471112676018.dkr.ecr.us-east-2.amazonaws.com/challenge-image-repository:latest
```