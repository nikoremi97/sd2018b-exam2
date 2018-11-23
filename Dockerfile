FROM alpine
LABEL mail: daniel.barragan@correo.icesi.edu.co

RUN apk add --update \
    python \
    python-dev \
    py-pip \
    build-base \
  && rm -rf /var/cache/apk/*

COPY . /app
RUN pip install -r flask==0.12.2

EXPOSE 8080
CMD ["/usr/bin/python", "/app/sources/microservice_a.py"]

