    "/usuarios/registro": {
      "post": {
        "tags": [ "Usuario" ],
        "summary": "Registra el primer usuario",
        "description": "Registra el primer usuario como admin si el banco esta vacio",
        "operationId": "regUsuario",
        "consumes": [ "application/json" ],
        "produces": [ "application/json" ],
        "parameters": [
          {
            "in": "body",
            "name": "body",
            "description": "Credenciales del usuario",
            "required": true,
            "schema": {
              "type": "object",
              "properties": {
                "username": {
                  "type": "string"
                },
                "password": {
                  "type": "string"
                }
              },
              "required": [ "username", "password" ]
            }
          }
        ],
        "responses": {
          "201": {
            "description": "Usuario registrado con exito",
            "schema": {
              "type": "object",
              "properties": {
                "access_token": {
                  "type": "string"
                }
              }
            }
          },
          "400": {
            "description": "Requisición malformada"
          },
          "401": {
            "description": "Unauthorized"
          }
        }
      }
    },