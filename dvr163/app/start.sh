#!/usr/bin/with-contenv bashio

# Run dovecot
echo Starting dovecot
dovecot

# Run postfix 
echo Starting postfix
postfix start

# Start python web server in the foreground
echo Starting python server
gunicorn --bind 0.0.0.0:8080 main:app
