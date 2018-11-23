# Docker Image to use
FROM python:3.6-slim
# directory to work on
WORKDIR /app
# copy the current dir content into the CT at /app
COPY . /app
# install the requirements specified on requirements.txt
RUN pip install --trusted-host pypi.python.org -r requirements.txt
#expose the microservice to the 8080 port
EXPOSE 8080
#define an environment variable
ENV NAME development
#Run the app.py
CMD export PYTHONPATH=$PYTHONPATH:`pwd`; export FLASK_ENV=development
CMD ["python", "app.py"]
