from datetime import datetime
from flask import Flask, render_template, request
from . import app
import json

@app.route("/")
def home():
    return "Maybe a GUI someday"

@app.route('/api/email', methods=['POST'])
def email():
    return request.data