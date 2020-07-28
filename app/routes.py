from datetime import datetime
from flask import Flask, render_template, request
from main import app
import json

@app.route("/")
def home():
    print("get home got") # TODO: Testing, remove
    return "Maybe a GUI someday"

@app.route('/api/email', methods=['POST'])
def email():
    print("You've got mail:")
    print(request.data)
    return request.data
