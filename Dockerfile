ARG BUILD_FROM=homeassistant/amd64-base:latest
FROM $BUILD_FROM

ENV LANG=C.UTF-8
ENV DEBIAN_FRONTEND=noninteractive

LABEL \
    io.hass.version="VERSION" \
    io.hass.type="addon" \
    io.hass.arch="armhf|aarch64|i386|amd64" \
    name=dvr163-hass \
    Version=0.0.1

EXPOSE 25 
EXPOSE 8080

# Dependencies
RUN apk update && apk add \
    postfix \
    dovecot \ 
    python3 \
    py3-pip && \
    pip3 install dropbox==10.2.0    

# Use python3 
RUN ln -s /usr/bin/python3 /usr/bin/python    

# SMTP Configuration
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
    # Write logginng to stdout
    echo "postlog   unix-dgram n  -       n       -       1       postlogd" >> /etc/postfix/master.cf && \
    echo "maillog_file = /dev/stdout" >> /etc/postfix/main.cf && \
    # Create mail user
    adduser ${USERNAME} -D && \
    addgroup ${USERNAME} root && \
    echo "${USERNAME}:${PASSWORD}" | chpasswd && \
    # Send mail to shell script per https://thecodingmachine.io/triggering-a-php-script-when-your-postfix-server-receives-a-mail
    echo "myhook unix - n n - - pipe" >> /etc/postfix/master.cf && \
    echo "  flags=F user=${USERNAME} argv=python3 -u /app/handle-email.py >> /proc/1/fd/1" >> /etc/postfix/master.cf && \
    echo "smtp      inet  n       -       -       -       -       smtpd" >> /etc/postfix/master.cf && \
    echo "    -o content_filter=myhook:dummy" >> /etc/postfix/master.cf && \
    echo "pickup    fifo  n       -       -       60      1       pickup" >> /etc/postfix/master.cf && \
    echo "    -o content_filter=myhook:dummy" >> /etc/postfix/master.cf && \
    # Add mail alias script to handle mail
    newaliases 

# Copy source files
COPY app /app
RUN chmod -R 777 /app

# Python 3 HTTP Server serves the current working dir
WORKDIR /app

# Run the app
CMD ["/app/start.sh"]