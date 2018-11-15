# sd2018b-exam2
**Icesi University**  
**Course:** Distributed Systems   
**Professor:** Daniel Barragán C.  
**Subject:** Artifact building for Continous Delivery  
**Email:** daniel.barragan at correo.icesi.edu.co  
**Student:** Alejandro Bueno C.  
**Student ID:** A00335472  
**Git URL:** https://github.com/abc1196/sd2018b-exam2.git  

### Expected results
* Develop artifact automatic building for Continous Delivery  
* Use libraries of programming languages to perform specific tasks   
* Diagnose and execute the needed actions to achieve a stable infrastructure  

### Used technologies
* Docker  
* CentOS7 Box
* Github Repository
* Python3
* Python3 Libraries: Flask, Fabric
* Ngrok  

### Infrastructure diagram  
The desired infrastructure to deploy consists in three Docker Containers and one Docker Client with the following settings:

* Python:3.6-slim CI Server: this CT has a Flask application with and endpoint using RESTful architecture best practices. The endpoint has the following logic:   
  * A Webhook attached to a Pull Request triggers the endpoint.  
  * The endpoint reads the Pull Request content and validates if the PR is mergedd  
  * If merged, via the Docker Python SDK, the endpoint runs the required commands to build the Docker Artifact and push it to the local registry.  
* wernight/ngrok Ngrok: this CT creates a temporary public domain name to expose the CI Server's endpoint.  
* registry Registry: this CT is a private local registry where the created artifacts will be pushed.  
* Windows 10 Home Docker Client: this Docker Client will be used to pull the private registry's artifacts. 


![][1]  
**Figure 1**. Deploy Diagram  

### Introduction  

The current branch contains two key elements to deploy the infrastructure. The first one is the docker-compose.yml. This file contains the provisioning required for each CT. The second one is the ci_server folder that contains the Dockerfile and python script to build the CI Server Docker image.  

#### docker-compose.yml  
 To start, the docker-compose.yml contains three services, briefly described above

```
 ngrok:
    image: wernight/ngrok
    ports:
      - 0.0.0.0:4040:4040
    links:
      - ci_server
    environment:
      NGROK_PORT: ci_server:80
```
This rervices refers to the Ngrok service. It uses the wernight/ngrok Docker image, attached to the 4040 port and it's linked to ci_server in its 80 port to expose the CI Server's endpoint.  

```
  ci_server:
    build: ./ci_server
    ports:
      - 80:80
    volumes:
      - //var/run/docker.sock:/var/run/docker.sock
```
This service refers to the CI Server service. It uses the Dockerfile (explained later) located at ./ci_server to build the image. It has a volume related to the Docker Machine's docker.sock to run the docker commands inside the endpoint.  

```
 registry:
    restart: always
    image: registry:2
    ports:
      - 5000:5000
    environment:
      REGISTRY_HTTP_ADDR: 0.0.0.0:5000
      REGISTRY_HTTP_TLS_CERTIFICATE: ./certs/domain.crt
      REGISTRY_HTTP_TLS_KEY: ./certs/domain.key
    volumes:
      - ./certs:/certs
      - ./data:/data
```  
This service refers to the private local Registry. It uses the registry Docker image, attached to the 5000 port. It also has two self-signed SSL certificates created with OpenSSL. These certificates are located at ./certs.  

#### CI Server 

The ci_server contains two key components to deploy the CI Server. First, it has the Dockerfile to build the proper image.  

```
# Use an official Python runtime as a parent image
FROM python:3.6-slim

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --trusted-host pypi.python.org -r requirements.txt

# Make port 80 available to the world outside this container
EXPOSE 80

# Define environment variable
ENV NAME World

# Run app.py when the container launches
CMD ["python", "app.py"]
```
This Dockerfile uses a python image (based on Debian) as a parent image. Copies the folder's content to the /app folder in the CT. The image install the required libraries from the requirements.txt file. Exposes the server in the port 80 and finally, runs the app.py script.  

```
from flask import Flask, request, json
import requests
import docker
import os
import socket
```  
To begin, the app.py script. It begins importing the required libraries like docker and flask.  

```
app = Flask(__name__)

@app.route("/")
def hello():
    html = "<h3>Hello!</h3>"
    return html

@app.route("/abueno/exam2/api/v1/images", methods=['POST'])
def build_image():
```
Next, the script creates the Flask app and defines some routes. The important one is build_image(). This one is the endpoint to build the artifacts from te Github repository.  

```
def build_image():
    content=request.get_data()
    contentString=str(content, 'utf-8')
    jsonFile=json.loads(contentString)
    merged=jsonFile["pull_request"]["merged"]
    if merged:
        sha=jsonFile["pull_request"]["head"]["sha"]
        imageUrl="https://raw.githubusercontent.com/abc1196/sd2018b-exam2/"+sha+"/image.json"
        imageResponse=requests.get(imageUrl)
        image=json.loads(imageResponse.content)

        dockerfileUrl="https://raw.githubusercontent.com/abc1196/sd2018b-exam2/"+sha+"/Dockerfile"
        dockerfileResponse=requests.get(dockerfileUrl)
        file = open("Dockerfile","w")
        file.write(str(dockerfileResponse.content, 'utf-8')) 
        file.close()
        tag="192.168.99.100:5000/"+image["service_name"]+":"+image["version"]

        client = docker.DockerClient(base_url='unix://var/run/docker.sock')
        client.images.build(path="./", tag=tag)
        client.images.push(tag)
        client.images.remove(image=tag, force=True)
        return tag
    else:
        return "Pull request is not merged"
```
First of all, the method begins by taking the HTTP Request content in a JSON format. Next, it checks if the PR comes from a merged PR (merged variable). If it's not merged, the method returns that the PR is not merged. Otherwise, the image.json and Dockerfile from the Github repository are downloaded to the CT; Then, a tag for the artifact is created; Finally, the Docker Client is created to use the Docker commands and the image is created, pushed to the private registry and then removed from the Docker Host.  

```
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)
```
Finally, the flask application runs int the port 80 and listens to any IP address.  

### Deployment  

Run the following command in the repository folder:
```
docker-compose up -d
```
This command will start the build of each of the services specified previously. It has the -d parameter to run in background. When the services are deployed, you will get an output like this:  

![][2]  
**Figure 2**. Docker Containers created      

Run this command to check if the services are running:  
```
docker ps
```
The output will be like this:  

![][3]  
**Figure 3**. Docker services running  

After that, go to the Ngrok Web UI via browser. To do this, go to localhost:4040. If you are using Windows, put the Docker Machine's port and the 4040 port. To know the Docker Machine's IP, run *docker-machine env*.  

![][4]  
**Figure 4**. Ngrok running  

Finally, let's create the Github webhook. In the repository, go to *Settings -> Webhooks*. Add a webhook and put in the Payload URL the URL that ngrok provides with the endpoint. The application endpoint is located at */abueno/exam2/api/v1/images*. So, for example, the resulting Payload URL will look like this:  

```
http://XXXXXXXX.ngrok.io/abueno/exam2/api/v1/images
```
Where XXXXXXXX is the URL ngrok provides. Last, check the *Let me select individual events* and check *Pull requests*.  

![][5]  
**Figure 5**. Github Webhook with Ngrok   

### Demonstration  

The repository must have a develop branch. Then, create a new branch. In this example, it would be develop-postgresql. This branch has a Dockerfile with the required components to create a postgresql image. It also has an image.json with the service name, the version and the type (Docker or AMI). Edit the image.json and change the version field.
```
{
    "service_name": "postgresql",
    "version": "1.4",
    "type": "Docker"
}
```
Commit changes and Compare & pull request. Make base the *develop* branch and compare *develop-postgresql*. Create the Pull Request. Via *Settings -> Webhooks* you can check the PR Webhook. It will look like this:  

![][6]  
**Figure 6**. First Webhook 

Since the PR was not a merge, the endpoint returned *Pull request is not merged*.  

Let's merge the PR. Go to the PR and click *Merge pull request*. Run *docker ps* and you can see a new process. This one is creating the artifact with the Dockerfile in the branch.  

![][7]  
**Figure 7**. Docker creating the artifact    

![][8]  
**Figure 8**. Merged Pull Request 

Finally, to check if the artifact was pushed to the registry, use the Host Machine as the Docker Client. In this case, a Windows 10 Home PC. First, go to the certs folder and install the ***domain.crt*** file to be able to use the registry. Then,open the terminal and run:  
```
docker pull 192.168.99.100:5000/postgresql:1.4
```  

![][9]  
**Figure 9**. Registry with the created artifact 

As you can see, the newer artifact was pushed to the registry (192.168.99.100:5000) and the Docker Client could pull it. 

### Issues  
There were two major issues developing the infrastructure. First of all, this exam was developed using Windows, so it was neccesary to install Docker Toolbox for Windows 10. Then, the Docker machine had problems regarding its DNS Server, so the Docker machine, the DNS Server was changed in the */etc/resolv.conf* file with the 8.8.8.8 DNS. Second of all, to be able to use a registry server, SSL certificates had to be created, so OpenSSL was installed to create them.  Then, the Docker clients that would use the registry, had to install the certificates (Windows) or place them in a proper folder (Linux Based OS).  

### References  
* https://hub.docker.com/_/registry/
* https://hub.docker.com/_/docker/
* https://docker-py.readthedocs.io/en/stable/index.html
* https://developer.github.com/v3/guides/building-a-ci-server/
* http://flask.pocoo.org/
* https://connexion.readthedocs.io/en/latest/  
* https://docs.docker.com/toolbox/toolbox_install_windows/  


[1]: images/deploy_diagram.png  
[2]: images/01_docker_compose_up.PNG	
[3]: images/02_docker_ps.PNG  
[4]: images/03_ngrok.PNG  
[5]: images/04_webhook.PNG	
[6]: images/05_pr_not_valid.PNG 
[7]: images/06_docker_ps_pr.PNG 
[8]: images/07_merge.PNG  
[9]: images/09_registry_ok.PNG
