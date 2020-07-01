ARG BUILD_FROM=homeassistant/amd64-base:latest
FROM $BUILD_FROM

ENV LANG C.UTF-8
LABEL io.hass.version="VERSION" io.hass.type="addon" io.hass.arch="armhf|aarch64|i386|amd64"

# Dependencies
RUN apk add --no-cache python3

# Copy source files 
COPY start.sh /
RUN chmod a+x start.sh

# Run the app
WORKDIR /data
CMD ["/start.sh"]