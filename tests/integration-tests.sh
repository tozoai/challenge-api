#!/bin/bash

if [ -z "$1" ]; then
  echo "Usage: $0 <endpoint>"
  exit 1
fi

ENDPOINT="$1"
USERNAME="$2"
PASSWORD="$3"

# Function to make a curl request
make_curl_request() {
    local method="$1"
    local url="$2"
    local data="$3"
    local token="$4"

    curl -s -X "$method" "$url" \
        -H "Authorization: Bearer $token" \
        -H "Content-Type: application/json" \
        -d "$data"
}

# CREATE FIRST USER (Admin)
RESPONSE=$(make_curl_request "PUT" "$ENDPOINT/auth" "{\"username\":\"$USERNAME\", \"password\":\"$PASSWORD\", \"role\":\"admin\"}")

echo "Response from creating first user: $RESPONSE"

# Perform authentication
TOKEN=$(make_curl_request "POST" "$ENDPOINT/auth" "{\"username\":\"$USERNAME\", \"password\":\"$PASSWORD\"}" | jq -r '.access_token')

# Check if the token was successfully extracted
if [ "$TOKEN" == "null" ] || [ -z "$TOKEN" ]; then
    echo "Authentication failed."
    exit 1
fi

echo "Authentication successful."
echo $TOKEN

# Create dummy users
for i in {1..3}; do
  USERNAME="user$i"
  PASSWORD="password$i"
  ROLE="user"

  RESPONSE=$(make_curl_request "PUT" "$ENDPOINT/auth" "{\"username\":\"$USERNAME\", \"password\":\"$PASSWORD\", \"role\":\"usuario\"}")

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
  "bloqueo": alse
}
EOF
  )

  RESPONSE=$(make_curl_request "PUT" "$ENDPOINT/proveedores" "$PROVEEDOR_DATA" "$TOKEN")

  echo "Response from creating proveedor $i: $RESPONSE"
done

# Perform a search for proveedores
SEARCH_RESPONSE=$(make_curl_request "GET" "$ENDPOINT/proveedores/busca?nombre=Proveedor" "" "$TOKEN")

echo "Search response: $SEARCH_RESPONSE"
