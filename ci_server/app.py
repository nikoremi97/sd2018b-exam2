#imported modules in requirements.txt
from flask import Flask, request, json
import requests
import docker
import os
import socket

app = Flask(__name__)

@app.route("/")
def hello():
    html = "<h3>Hello world!</h3>"
    return html

@app.route("/nrecalde/exam2/api/v1/images", methods=['POST'])
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
        image=json.load(imageResponse.content)
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


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
