#!/usr/bin/with-contenv bashio

# Run dovecot
echo Starting dovecot
dovecot

# Run postfix 
echo Starting postfix
postfix start

# Start python web server in the foreground
echo Starting python server
python -m http.server 8080
echo Listening on port 8080
