from datetime import datetime
from flask import Flask, render_template, request
import handle_email
import json
from shared import logger
from main import app


@app.route("/")
def home():
    logger.info("get home got")  # TODO: Testing, remove
    return "Maybe a GUI someday"


@app.route("/api/email", methods=["POST"])
def email():
    data = request.data.decode("utf-8") 
    logger.info("You've got mail")
    handle_email.main(data)
    return "Thanks"
