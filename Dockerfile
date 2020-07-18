ARG BUILD_FROM=homeassistant/amd64-base:latest
FROM $BUILD_FROM

ENV LANG=C.UTF-8
ENV DEBIAN_FRONTEND=noninteractive

LABEL io.hass.version="VERSION" io.hass.type="addon" io.hass.arch="armhf|aarch64|i386|amd64" name=dvr163-hass Version=0.0.1

EXPOSE 25 
EXPOSE 8080

# Dependencies
RUN apk update && apk add \
    python3 \
    py3-pip \
    postfix \
    dovecot && \
    pip3 install dropbox==10.2.0

# Server Configuration
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
    echo "${USERNAME}:${PASSWORD}" | chpasswd && \
    # Add mail alias script to handcatle mail
    echo "${USERNAME}: \"|python3 /app/handle-email.py\"" >> /etc/aliases && \
    newaliases     

# Copy source files 
COPY app /app
RUN chmod -R 777 /app

# Run the app
CMD ["/app/start.sh"]
