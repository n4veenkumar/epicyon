FROM debian:buster-slim
ENV DOMAIN=localhost
RUN apt-get update && \
    apt-get -y install \
    imagemagick \
    python3-crypto \
    python3-dateutil \
    python3-idna \
    python3-numpy \
    python3-pil.imagetk \
    python3-pip \
    python3-setuptools \
    python3-socks \
    tor && \
    pip3 install requests beautifulsoup4 pycryptodome
RUN adduser --system --home=/opt/epicyon --group epicyon
COPY --chown=epicyon:epicyon . /app
EXPOSE 80 7156
CMD /usr/bin/python3 \
    /app/epicyon.py \
    --port 80 \
    --proxy 7156 \
    --registration open \
    --domain $DOMAIN \
    --path /app