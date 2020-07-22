# Python web server

ARG BUILD_FROM=homeassistant/amd64-base:latest
FROM $BUILD_FROM

ENV LANG=C.UTF-8
ENV DEBIAN_FRONTEND=noninteractive

LABEL io.hass.version="VERSION" io.hass.type="addon" io.hass.arch="armhf|aarch64|i386|amd64" name=dvr163-hass Version=0.0.1

EXPOSE 8080

# Dependencies
RUN apk update && apk add \
    python3 \
    py3-pip && \
    pip3 install dropbox==10.2.0

# Use python3 
RUN ln -s /usr/bin/python3 /usr/bin/python

# Copy source files
COPY app /app
RUN chmod -R 777 /app

# Python 3 HTTP Server serves the current working dir
# So let's set it to our add-on persistent data directory.
WORKDIR /app

# Run the app
CMD ["python3", "-m", "http.server", "8080"]
