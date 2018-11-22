import os
import logging
import requests
import json
import docker
from flask import Flask, request, json

def hello():
    result = {'command_return': 'Hello World'}
    return result

def new_images_on_merged():
    result = ""
    json_data = request.get_data()
    json_Sting = str(json_data, 'utf-8')
    jsonFile = json.loads(json_Sting)
    isMerged = jsonFile["pull_request"]["merged"]
    domain = 'registry-exam2.icesi.edu.co:443'

     if isMerged:
        pull_id  = jsonFile["pull_request"]["head"]["sha"]
        json_image_url     = "https://raw.githubusercontent.com/nikoremi97/sd2018b-exam2/" + pull_id + "/image.json"
        response_image_url = requests.get(json_image_url)
        image_data    =  json.loads(response_image_url.content)

        for service in image_data:
            service_name = service["service_name"]
            image_type = service["type"]
            image_version = service["version"]

            if image_type == 'Docker':
                dockerfile_image_url = "https://raw.githubusercontent.com/nikoremi97/sd2018b-exam2/" + pull_id + "/" + service_name + "/Dockerfile"
                file_response = requests.get(dockerfile_image_url)
                file = open("Dockerfile","w")
                file.write(str(file_response.content, 'utf-8'))
                file.close()
                image_tag  = "registry-exam2.icesi.edu.co:443/" + service_name + ":" + image_version
                client = docker.DockerClient(base_url='unix://var/run/docker.sock')
                client.images.build(path="./", tag=image_tag)
                client.images.push(image_tag)
                client.images.remove(image=image_tag, force=True)
                result = image_tag + " - Image built - " + result

            else:
                out = {'command return' : 'JSON file have an incorrect format'}
        out = {'cammand return' : result}

    else:
        out= {'command_return': 'Pull request was not merged'}

    return out
