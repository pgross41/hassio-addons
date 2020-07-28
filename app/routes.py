from datetime import datetime
from flask import Flask, render_template, request
from main import app
import json

print("!!!! begin web server")

@app.route("/")
def home():
    print("get home got") # TODO: Testing, remove
    return "Maybe a GUI someday"

@app.route('/api/email', methods=['POST'])
def email():
    print("!!!! we have received a POST to /api/email")
    print(request.data)
    return request.data
