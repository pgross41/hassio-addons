ARG BUILD_FROM=homeassistant/amd64-base:latest
FROM $BUILD_FROM

# Computer UTF-8
ENV LANG=C.UTF-8

# Silence configuration prompts
ENV DEBIAN_FRONTEND=noninteractive

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE 1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED 1

# Labels, some are for Home Assistant
LABEL \
    io.hass.version="VERSION" \
    io.hass.type="addon" \
    io.hass.arch="armhf|aarch64|i386|amd64" \
    name=dvr163-hass \
    Version=0.0.1

# Postix SMTP server
EXPOSE 25 

# Python web server
EXPOSE 8080

# Install container dependencies
RUN apk update && apk add --no-cache \
    postfix \
    dovecot \ 
    python3 \
    py3-pip  

# Configure postfix/dovecot
ARG USERNAME=hass
ARG PASSWORD=hass
RUN true && \
    # Tell Postfix to use Dovecot for SASL authentication
    echo "smtpd_sasl_type = dovecot" >> /etc/postfix/main.cf && \
    echo "smtpd_sasl_path = private/auth" >> /etc/postfix/main.cf && \
    echo "smtpd_sasl_auth_enable = yes" >> /etc/postfix/main.cf && \
    # Tell Dovecot to listen for SASL authentication requests from Postfix
    printf " \
    \nservice auth { \
    \n    unix_listener /var/spool/postfix/private/auth { \
    \n        mode = 0660 \
    \n        user = postfix \
    \n        group = postfix \
    \n    } \
    \n}" > /etc/dovecot/conf.d/10-master.conf && \
    # Enable plaintext logins
    echo "disable_plaintext_auth = no" >> /etc/dovecot/conf.d/10-auth.conf && \
    echo "auth_mechanisms = plain login" >> /etc/dovecot/conf.d/10-auth.conf && \
    # Write logginng to /proc/1/fd/1 (Docker output)
    echo "postlog   unix-dgram n  -       n       -       1       postlogd" >> /etc/postfix/master.cf && \
    echo "maillog_file_prefixes = /proc" >> /etc/postfix/main.cf && \
    echo "maillog_file = /proc/1/fd/1" >> /etc/postfix/main.cf && \
    # Create mail user
    adduser ${USERNAME} -D && \
    addgroup ${USERNAME} root && \
    echo "${USERNAME}:${PASSWORD}" | chpasswd && \
    # Send mail to shell script per https://thecodingmachine.io/triggering-a-php-script-when-your-postfix-server-receives-a-mail
    echo "myhook unix - n n - - pipe" >> /etc/postfix/master.cf && \
    # echo "  flags=F user=${USERNAME} argv=curl -H 'Content-Type: text/plain' -d @- http://localhost:8080/api/email" >> /etc/postfix/master.cf && \
    # echo "  flags=F user=${USERNAME} argv=curl -H 'Content-Type: text/plain' -d dumbbbb http://localhost:8080/api/email" >> /etc/postfix/master.cf && \
    echo "  flags=F user=${USERNAME} argv=/app/handle_email.sh" >> /etc/postfix/master.cf && \
    echo "smtp      inet  n       -       -       -       -       smtpd" >> /etc/postfix/master.cf && \
    echo "    -o content_filter=myhook:dummy" >> /etc/postfix/master.cf && \
    echo "pickup    fifo  n       -       -       60      1       pickup" >> /etc/postfix/master.cf && \
    echo "    -o content_filter=myhook:dummy" >> /etc/postfix/master.cf && \
    # Add mail alias script to handle mail
    newaliases 


# Configure Python
COPY requirements.txt /app/
WORKDIR /app
RUN pip install -r requirements.txt && \
    ln -s /usr/bin/python3 /usr/bin/python

# Copy source code
COPY app /app
RUN chmod -R 777 /app 

# Run the app
CMD ["/app/start.sh"]