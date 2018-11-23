# sd2018b-exam2  
**Icesi University**  
**Course:** Distributed Systems  
**Professor:** Daniel Barragán  
**Subject:** Artifact building for Continous Delivery  
**email:** nicolas.recalde at outloook.com  
**Student:** Nicolás Recalde Miranda  
**Student ID:** A00065888  
**Git URL:** https://github.com/nikoremi97/sd2018b-exam2.git  

## Objectives  
* Develop artifact automatic building for Continous Delivery  
* Use libraries of programming languages to perform specific tasks  
* Diagnose and execute the needed actions to achieve a stable infrastructure  

## Technologies applied  
* Docker
* CentOS7
* Github
* Python3
* Python3 libraries: Flask, Fabric
* Ngrok  

## Description  

For the artifact building for Continous Delivery, was taken into account the following:

* Create a Fork of the sd2018b-exam2 repository and add the sources of a microservice using best practices.  

* To lodge in its fork an archive Dockerfile of coupling for the construction of a Docker type device from the sources of its microservice.  

The deployed infrastructure had the following components:

* CI Server (Python:3.6-slim docker image): that receives as input the name of a service, version and type (Docker - AMI) and its logic in the construction of a Docker image whose name must be service_name: version and must be published in the local registry. The endpoint has the following logic:
  * A Webhook attached to a Pull Request triggers the endpoint.  
  * The endpoint reads the Pull Request content and validates if the PR is merged.  
  * If the pull request is merged, via the Docker Python SDK, the endpoint runs the required commands to build the Docker Artifact and push it to the local registry.


* Ngrok (wernight/ngrok docker image): this CT creates a temporary public domain name to expose the CI Server's endpoint using the handlers of its microservice. Ngrok is used to attach the microservice to a Github webhook.  

* Registry (registry docker image): for the storage of Docker images. Use the DockerHub image: https://hub.docker.com/_/registry/. And it's hoped to prove that it is possible to download the generated image from a computer belonging to the network.  

The architecture diagram is presented as follows:  
![][1]
**Figure 1.** Architecture diagram.  

## Solution   
### docker-compose

To deploy various containers (CT), is necesary  not only a Dockerfile but a docker-compose.yaml. This file describes the docker image to use for the container, ports mapped to it, enviroments, and links to another CT.  
The *docker-compose.yaml* contains three services described above:  

The *ci_server* service, use the Dockerfile located at /ci_server to build the CT. It has a volume related to the Docker Machine's docker.sock to run the docker commands inside the endpoint.
```
ci_server:
    build: ci_server
    container_name: ci_server
    environment:
      - 'CI_SERVER_HTTP_ADDR=0.0.0.0:8080'
    volumes:
      - //var/run/docker.sock:/var/run/docker.sock
    ports:
        - '8080:8080'
```  
This is the Ngrok service. It uses the wernight/ngrok Docker image, attached to the 4040 port and it's linked to ci_server in its 80 port to expose the CI Server's endpoint. As it was described, the ngrok allows to expose the local service running on the CI_SERVER to the webhook on Github.
```
ngrok:
    image: wernight/ngrok
    ports:
        - 0.0.0.0:4040:4040
    links:
        - ci_server
    environment:
        NGROK_PORT: ci_server:8080
```  
This service refers to the private local Registry. It uses the registry Docker image, attached to the 5000 port. It also has two self-signed SSL certificates created with OpenSSL. These certificates are located at ./certs.
```
registry-exam2.icesi.edu.co:
    image: registry:2
    container_name: registry-exam2.icesi.edu.co
    environment:
      REGISTRY_HTTP_ADDR: 0.0.0.0:5000
      REGISTRY_HTTP_TLS_CERTIFICATE: ./certs/domain.crt
      REGISTRY_HTTP_TLS_KEY: ./certs/domain.key
    volumes:
      - ./certs:/certs
      - ./data:/data
    ports:
        - '443:443
```
### ci_server  
In the /ci_server there are 3 elements:  
One is the **Dockerfile** necesary to build the CT.  

```
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
ENV NAME World
#Run the app.py
CMD ["python", "app.py"]
```
Two, **requirements.txt** contains the required python3 modules to make the microservice.
```
docker
flask
```

And three, the microservice **app.py**.  
First, the app.py script imports the python modules required to achive microservice goals:  
```
#imported modules in requirements.txt
from flask import Flask, request, json
import requests
import docker
import os
import socket
```
Then, it creates Flask application and defines its routes (/). And it defines the methods in the app.
```  
app = Flask(__name__)

@app.route("/")
def hello():
    html = "<h3>Hello world!</h3>"
    return html

@app.route("/nrecalde/exam2/api/v1/images", methods=['POST'])
def build_image_in_registry():
``````
The *build_image_in_registry()* method is designed to build the artifact into the Registry CT. First, the method takes the HTPP request content and decode into JSON format. Next, it verifies that the pull request is already merged or not. If it was merged, it takes the pull request ID and get the 'image' docker type and the version of it in the json. Then it concatenates the image and version to open a Dockerfile that has the necesary things to build the new artifact. Finally, a Docker Client build the artifact and push it to the Registry CT.
```
def build_image_in_registry():
    #gets the payload from the http request
    content=request.get_data()
    contentString=str(content, 'utf-8')
    #gets the json from the payload
    jsonFile=json.loads(contentString)
    #gets the pull_request and merged values alocated at the json from payload
    merged=jsonFile["pull_request"]["merged"]
    #use the domain defined on the docker-compose.yaml file for the Registry CT
    domain = 'registry-exam2.icesi.edu.co:5000'

    if merged:
        #gets the pull_request ID from jsonFile
        pull_id=jsonFile["pull_request"]["head"]["sha"]

        #gets docker image type from json
        imageUrl="https://raw.githubusercontent.com/nikoremi97/sd2018b-exam2/"+pull_id+"/image.json"
        imageResponse=requests.get(imageUrl)
        image=json.loads(imageResponse.content)

        #gets dockerfile asociated with that image
        dockerfileUrl="https://raw.githubusercontent.com/nikoremi97/sd2018b-exam2/"+pull_id+"/Dockerfile"
        dockerfileResponse=requests.get(dockerfileUrl)
        file = open("Dockerfile","w")
        file.write(str(dockerfileResponse.content, 'utf-8'))
        file.close()

        #tags the docker image and service version to push into the Registry
        tag=domain+"/"+image["service_name"]+":"+image["version"]
        client = docker.DockerClient(base_url='unix://var/run/docker.sock')
        #build the artifact into Registry
        client.images.build(path="./", tag=tag)
        #push the artifact into Registry
        client.images.push(tag)
        client.images.remove(image=tag, force=True)
        return tag
    else:
        return "Pull request is not merged"

```
Finally, the flask application runs int the port 80 and listens to any IP address.
```
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
```
## Deployment
To deploy the Artifact building for Continous Delivery, run the following command:
```
sudo docker-compose up --build
```
This command first, makes a docker pull and build the artifacts for the three services described in the docker-compose.yaml file. Once it was pulled, extracted and build, the output is as follows:  
![][2]  
**Figure 2.** Built successful.  

Now, access to the ngrok service via WebBrowser *typing 0.0.0.0:4040*. And this is the way we obtain a public domain for the microservice deployed on the ci_server. The view in the WebBrowser should be as follows:  
![][3]  
**Figure 3.** Ngrok public domain.      
This public domain is what must be attached onto the github webhook. And select application/json in the content type box. As follows:    
![][4]  
**Figure 4.** Github webook.  
Now, we make a new pull request to verify if the webhook is listening to the service. As follows:
![][5]  
**Figure 5.** New pull request.  
On the webhook, check if its listened by itself.
![][6]  
**Figure 6.** Not merged payload.
![][7]  
Now let's close the pull request so the app can build the new artifacts.
![][7]
**Figure 7.** Pull request closed.  

## Issues
I have some Issues that didn't allow me to check the correct function of the microservice. The FLASK_ENV=development did not change at all when I tried to set the debug mode to ON. So I couldn't see which error was taking cause in the end of the Deployment. I had an 500 HTTP response when I closed the pull request.
![][8]
**Figure 7.** Pull request closed.  


## References  
* https://developer.github.com/v3/guides/building-a-ci-server/
* https://developer.github.com/v3/repos/statuses/
* https://developer.github.com/webhooks/configuring/#using-ngrok
* https://ngrok.com/docs
* https://docs.chef.io/
* https://connexion.readthedocs.io/en/latest/
* http://flask.pocoo.org/docs/1.0/quickstart/
* https://github.com/ICESI/so-microservices-python-part1/tree/master/03_intro_swagger  

[1]: images/delivery.png
[2]: images/build-ok.png
[3]: images/tunel-ngrok.png
[4]: images/github-webhook.png
[5]: images/merge-pull-request.png
[6]: images/not-merged.png
[7]: images/merged-pull-request.png
[8]: images/closed-pr-error.png
