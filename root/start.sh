#!/bin/bash

echo Starting SMTP and web servers 

service dovecot start
postfix start-fg

# Uhhhh todo
python3 -m http.server 8080
