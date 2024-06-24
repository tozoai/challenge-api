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

# CREATE FIRST USER (admin)
echo "Create the first admin user:"
echo $(make_curl_request "PUT" "$ENDPOINT/auth" "{\"username\":\"$USERNAME\", \"password\":\"$PASSWORD\", \"role\":\"admin\"}")

# Perform privileged authentication
echo "Authenticate with the admin user and print the token:"
TOKEN=$(make_curl_request "POST" "$ENDPOINT/auth" "{\"username\":\"$USERNAME\", \"password\":\"$PASSWORD\"}" | jq -r '.access_token')

# Check if the token was successfully extracted
if [ "$TOKEN" == "null" ] || [ -z "$TOKEN" ]; then
    echo "Authentication failed."
    exit 1
fi
echo "Authentication successful."

echo "$TOKEN"

echo "Create a duplicate user:"
echo $(make_curl_request "PUT" "$ENDPOINT/auth" "{\"username\":\"$USERNAME\", \"password\":\"$PASSWORD\", \"role\":\"admin\"}" "$TOKEN")
echo -e 
echo "Testing password complexity not met:"
echo $(make_curl_request "PUT" "$ENDPOINT/auth" "{\"username\":\"$USERNAME\", \"password\":\"senhafraca\", \"role\":\"admin\"}" "$TOKEN")
echo -e 
echo "Testing username same as password:"
echo $(make_curl_request "PUT" "$ENDPOINT/auth" "{\"username\":\"Adminin123\", \"password\":\"Adminin123\", \"role\":\"admin\"}" "$TOKEN")
echo -e 
echo "Response from testing invalid username:"
echo $(make_curl_request "PUT" "$ENDPOINT/auth" "{\"username\":\"$USERNAME\", \"password\":\"Admasdasdasin123\", \"role\":\"admin\"}" "$TOKEN")
echo -e 
echo "Response creating unprivileged user: $RESPONSE"
echo $(make_curl_request "PUT" "$ENDPOINT/auth" "{\"username\":\"usuario\", \"password\":\"Password123\", \"role\":\"usuario\"}" "$TOKEN")
echo -e 
echo "perform authentication with unprivileged user"
USERTOKEN=$(make_curl_request "POST" "$ENDPOINT/auth" "{\"username\":\"usuario\", \"password\":\"Password123\"}" | jq -r '.access_token')
echo -e 
# Check if the token was successfully extracted
if [ "$USERTOKEN" == "null" ] || [ -z "$USERTOKEN" ]; then
    echo "Authentication failed."
    exit 1
fi
echo -e 
echo "Authentication successful."
echo -e 
echo "Attempt to create an admin user:"
echo $(make_curl_request "PUT" "$ENDPOINT/auth" "{\"username\":\"usuario1\", \"password\":\"$PASSWORD\", \"role\":\"admin\"}" "$USERTOKEN")
echo -e 
echo "Attempt to Create another unprivileged user:"
echo $(make_curl_request "PUT" "$ENDPOINT/auth" "{\"username\":\"usuario2\", \"password\":\"$PASSWORD\", \"role\":\"usuario\"}" "$USERTOKEN")
echo -e 
# Create dummy proveedores
for i in {1..3}; do
  PROVEEDOR_DATA=$(cat <<EOF
{
  "nombre": "Proveedor",
  "razon_social": "Razon Social $i",
  "nombre_contacto": "Contacto $i",
  "email": "proveedor example com",
  "direccion_fiscal": "Direccion Fiscal $i",
  "tipo_servicio": "Servicio $i",
  "criticidad": "Alta"
}
EOF
  )
  echo -e 
  RESPONSE=$(make_curl_request "PUT" "$ENDPOINT/proveedores" "$PROVEEDOR_DATA" "$TOKEN")
    echo "Response from creating proveedor $i: $RESPONSE"
done

# Perform a search for proveedores
SEARCH_RESPONSE=$(make_curl_request "GET" "$ENDPOINT/proveedores/busca?nombre=Proveedor" "" "$TOKEN")

echo "Search response: $SEARCH_RESPONSE"
