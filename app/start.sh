#!/usr/bin/with-contenv bashio
set -e

###############################################################################
# Copy config to environment variables
###############################################################################
export log_level="$(bashio::config 'log_level')"
export dropbox_enabled="$(bashio::config 'dropbox.enabled')"
export dropbox_access_token="$(bashio::config 'dropbox.access_token')"
export email_enabled="$(bashio::config 'email.enabled')"
export email_host="$(bashio::config 'email.host')"
export email_port="$(bashio::config 'email.port')"
export email_username="$(bashio::config 'email.username')"
export email_password="$(bashio::config 'email.password')"
export email_from_addr="$(bashio::config 'email.from_addr')"
export email_to_addr="$(bashio::config 'email.to_addr')"

# Run dovecot
echo Starting dovecot
dovecot

# Run postfix in the foreground
echo Starting postfix
postfix start-fg
