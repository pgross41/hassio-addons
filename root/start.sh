#!/bin/bash

echo Starting SMTP and web servers 

# Run dovecot
service dovecot start

# Run postfix in the foreground
postfix start-fg
