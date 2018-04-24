#!/bin/bash
echo "Enter server IP for 'server FQDN' field"
openssl req -newkey rsa:2048 -sha256 -nodes -keyout key.pem -x509 -days 3650 -out cert.pem
cat key.pem cert.pem > key_cert.pem
