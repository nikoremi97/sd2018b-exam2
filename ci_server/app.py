from flask import Flask
import os
import socket


app = Flask(__name__)

@app.route("/")
def hello():
    html = "<h3>Hello!</h3>"
    return html

@app.route("/abc/exam2/api/v1/images", methods=["POST"])
def build_image():
    html = "<h3>Hello biatch!</h3>"
    return html

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)