ARG BUILD_FROM=ubuntu:20.04
FROM $BUILD_FROM
ENV LANG=C.UTF-8
ENV DEBIAN_FRONTEND=noninteractive
LABEL io.hass.version="VERSION" io.hass.type="addon" io.hass.arch="armhf|aarch64|i386|amd64"

# Dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-setuptools \
    postfix \
    dovecot-common \
    dovecot-imapd \
    unzip \
    wget 
RUN pip3 install --force-reinstall dropbox==10.2.0
# RUN wget https://github.com/dropbox/dropbox-sdk-python/archive/master.zip -O dropbox-sdk-python-master.zip && \
#     unzip dropbox-sdk-python-master.zip && \
#     rm dropbox-sdk-python-master.zip && \
#     cd dropbox-sdk-python-master && \
#     python3 setup.py install

# Configuration
RUN true && \
    # Tell Postfix to use Dovecot for SASL authentication
    echo "smtpd_sasl_type = dovecot" >> /etc/postfix/main.cf && \
    echo "smtpd_sasl_path = private/auth" >> /etc/postfix/main.cf && \
    echo "smtpd_sasl_auth_enable = yes" >> /etc/postfix/main.cf && \
    # Tell Dovecot to listen for SASL authentication requests from Postfix
    echo " \
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
    echo "maillog_file = /dev/stdout" >> /etc/postfix/main.cf

# Create mail user
ARG USERNAME=hass
ARG PASSWORD=hass
RUN useradd -p $(openssl passwd -1 $PASSWORD) $USERNAME && \
    mkdir /home/${USERNAME}

# Copy source files 
COPY root /
RUN chmod +x /start.sh && \ 
    chmod +x /data/handle_email.sh && \
    chmod 777 /data/handle_email_input_buffer

# Add mail alias script to handle mail
RUN echo "${USERNAME}: |/data/handle_email.sh" >> /etc/aliases && \
    newaliases 

# Run the app
CMD ["/start.sh"]