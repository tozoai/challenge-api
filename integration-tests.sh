#!/bin/bash


AUTH_URL="$1"
PROVEEDORES="$1"
USERNAME="username"
PASSWORD="password"

echo "$AUTH_URL"
echo "$PROVEEDORES"

pause(){
	read -p "Press [Enter] key to continue..."
}   

# CREATE FIRST USER
TOKEN=$(curl -s -X PUT "$AUTH_URL" \
    -H "Content-Type: application/json" \
    -d "{\"username\":\"$USERNAME\", \"password\":\"$PASSWORD\"}")

# Perform authentication 
TOKEN=$(curl -s -X POST "$AUTH_URL" \
    -H "Content-Type: application/json" \
    -d "{\"username\":\"$USERNAME\", \"password\":\"$PASSWORD\"}" \
    | jq -r '.access_token')

# Check if the token was successfully extracted
if [ "$TOKEN" == "null" ] || [ -z "$TOKEN" ]; then
    echo "Authentication failed."
    exit 1
fi

echo "Authentication successful. 

# Use the JWT token for a subsequent request
curl -s -X GET "$PROVEEDORES" \
    -H "Authorization: Bearer $TOKEN"

