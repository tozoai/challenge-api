#!/bin/bash

if [ -z "$1" ]; then
  echo "Usage: $0 <endpoint>"
  exit 1
fi

ENDPOINT="http://$1/"
USERNAME="username"
PASSWORD="password"

# CREATE FIRST USER
RESPONSE=$(curl -s -X PUT "$ENDPOINT/auth" \
    -H "Content-Type: application/json" \
    -d "{\"username\":\"$USERNAME\", \"password\":\"$PASSWORD\"}")

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

# Use the JWT token for a subsequent request
curl -s -X GET "$ENDPOINT/proveedores" \
    -H "Authorization: Bearer $TOKEN"
