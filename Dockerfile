FROM dduportal/docker-compose:1.7.1

COPY . /dvr163-hass

WORKDIR /dvr163-hass

CMD ["up"]
