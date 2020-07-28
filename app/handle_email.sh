#!/bin/bash
cat > "/app/email"
echo "-----------------HANDLING EMAIL-----------------"
# curl -H 'Content-Type: text/plain' -d @- http://localhost:8080/api/email
curl -H 'Content-Type: text/plain' -d "@/app/email" http://localhost:8080/api/email
