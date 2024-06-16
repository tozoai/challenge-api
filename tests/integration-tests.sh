#!/bin/bash

if [ -z "$1" ]; then
  echo "Usage: $0 <endpoint>"
  exit 1
fi

ENDPOINT="http://$1"
USERNAME="admin"
PASSWORD="adminpassword"

# CREATE FIRST USER (Admin)
RESPONSE=$(curl -s -X PUT "$ENDPOINT/auth" \
    -H "Content-Type: application/json" \
    -d "{\"username\":\"$USERNAME\", \"password\":\"$PASSWORD\", \"role\":\"admin\"}")

echo "Response from creating first user: $RESPONSE"

# Perform authentication
TOKEN=$(curl -s -X POST "$ENDPOINT/auth" \
    -H "Content-Type: application/json" \
    -d "{\"username\":\"$USERNAME\", \"password\":\"$PASSWORD\"}" \
    | jq -r '.access_token')

# Check if the token was successfully extracted
if [ "$TOKEN" == "null" ] || [ -z "$TOKEN" ]; then
    echo "Authentication failed."
    exit 1
fi

echo "Authentication successful."

# Create dummy users
for i in {1..3}; do
  USERNAME="user$i"
  PASSWORD="password$i"
  ROLE="user"

  RESPONSE=$(curl -s -X PUT "$ENDPOINT/auth" \
      -H "Authorization: Bearer $TOKEN" \
      -H "Content-Type: application/json" \
      -d "{\"username\":\"$USERNAME\", \"password\":\"$PASSWORD\", \"role\":\"usuario\"}")

  echo "Response from creating user $i: $RESPONSE"
done

# Create dummy proveedores
for i in {1..3}; do
  PROVEEDOR_DATA=$(cat <<EOF
{
  "nombre": "Proveedor",
  "razon_social": "Razon Social $i",
  "nombre_contato": "Contacto $i",
  "email": "proveedor$i@example.com",
  "direccion_fiscal": "Direccion Fiscal $i",
  "tipo_servicio": "Servicio $i",
  "criticidad": "Alta",
  "bloqueo": false
}
EOF
  )

  RESPONSE=$(curl -s -X PUT "$ENDPOINT/proveedores" \
      -H "Authorization: Bearer $TOKEN" \
      -H "Content-Type: application/json" \
      -d "$PROVEEDOR_DATA")

  echo "Response from creating proveedor $i: $RESPONSE"
done

# Perform a search for proveedores
SEARCH_RESPONSE=$(curl -s -X GET "$ENDPOINT/proveedores/busca?nombre=Proveedor" \
    -H "Authorization: Bearer $TOKEN")

echo "Search response: $SEARCH_RESPONSE"
