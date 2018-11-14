from flask import Flask, request
import docker
import os
import socket


app = Flask(__name__)

client = docker.from_env()

@app.route("/")
def hello():
    html = "<h3>Hello!</h3>"
    return html

@app.route("/abueno/exam2/api/v1/images", methods=['POST'])
def build_image():
    return request.get_data()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)