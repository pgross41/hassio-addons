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
# https://wiki2.dovecot.org/HowTo/PostfixAndDovecotSASL
ARG USERNAME=hass
ARG PASSWORD=hass
RUN true && \
    #
    # Write postfix/dovecot logging to Docker output (i.e. /proc/1/fd/1)
    # Useful for development but comment out for production as it is too cluttered
    echo "postlog   unix-dgram n  -       n       -       1       postlogd" >> /etc/postfix/master.cf && \
    echo "maillog_file_prefixes = /proc" >> /etc/postfix/main.cf && \
    echo "maillog_file = /proc/1/fd/1" >> /etc/postfix/main.cf && \ 
    echo "auth_verbose = yes" >> /etc/dovecot/conf.d/10-logging.conf && \
    echo "log_path = /proc/1/fd/1" >> /etc/dovecot/conf.d/10-auth.conf && \
    echo "info_log_path = /proc/1/fd/1" >> /etc/dovecot/conf.d/10-auth.conf && \
    echo "debug_log_path = /proc/1/fd/1" >> /etc/dovecot/conf.d/10-auth.conf && \
    #
    # Enable plaintext logins and add user to dovecot user database
    echo "disable_plaintext_auth = no" >> /etc/dovecot/conf.d/10-auth.conf && \
    echo "auth_mechanisms = plain login" >> /etc/dovecot/conf.d/10-auth.conf && \
    sed -i 's/scheme=CRYPT/scheme=PLAIN/g' /etc/dovecot/conf.d/auth-passwdfile.conf.ext  && \
    echo "${USERNAME}:{PLAIN}${PASSWORD}::::::" >> /etc/dovecot/users && \
    #
    # Assure /var/spool/postfix/private/auth gets created
    # https://www.howtoforge.com/postfix-dovecot-warning-sasl-connect-to-private-auth-failed-no-such-file-or-directory
    printf "\n \
    \nclient { \
    \n   path = /var/spool/postfix/private/auth \
    \n   mode = 0660 \
    \n   user = postfix \
    \n   group = postfix \
    \n}" >> /etc/dovecot/conf.d/10-master.conf && \
    #
    # Tell Dovecot to listen for SASL authentication requests from Postfix
    printf " \
    \nservice auth { \
    \n    unix_listener /var/spool/postfix/private/auth { \
    \n        mode = 0660 \
    \n        user = postfix \
    \n        group = postfix \
    \n    } \
    \n}" > /etc/dovecot/conf.d/10-master.conf && \
    #
    # Tell Postfix to use Dovecot for SASL authentication
    echo "smtpd_sasl_type = dovecot" >> /etc/postfix/main.cf && \
    echo "smtpd_sasl_path = private/auth" >> /etc/postfix/main.cf && \
    echo "smtpd_sasl_auth_enable = yes" >> /etc/postfix/main.cf && \
    #
    # Fix postfix error in log: warning: master_wakeup_timer_event: service pickup(public/pickup): Connection refused
    # More info: https://talk.plesk.com/threads/postfix-master-connection-refused.303699/
    sed -i 's/pickup    unix/pickup    fifo/g' /etc/postfix/master.cf && \
    sed -i 's/qmgr      unix/qmgr      fifo/g' /etc/postfix/master.cf && \
    #
    # Pipe mail into POST request so we can handle it in Python
    # More info: https://thecodingmachine.io/triggering-a-php-script-when-your-postfix-server-receives-a-mail
    echo "myhook unix - n n - - pipe" >> /etc/postfix/master.cf && \
    echo "  flags=F user=${USERNAME} argv=curl -H {Content-Type: text/plain} --data-binary @- http://localhost:8080/api/email" >> /etc/postfix/master.cf && \
    echo "smtp      inet  n       -       -       -       -       smtpd" >> /etc/postfix/master.cf && \
    echo "    -o content_filter=myhook:dummy" >> /etc/postfix/master.cf && \
    echo "pickup    fifo  n       -       -       60      1       pickup" >> /etc/postfix/master.cf && \
    echo "    -o content_filter=myhook:dummy" >> /etc/postfix/master.cf && \
    #
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
