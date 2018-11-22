FROM python:3.6
RUN pip3.6 install --upgrade pip
RUN pip3.6 install connexion[swagger-ui]
RUN pip3.6 install --trusted-host pypi.python.org  docker[tls]
COPY ./endpoint /endpoint
WORKDIR /endpoint
CMD ./deploy.sh
