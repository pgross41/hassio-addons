from datetime import datetime
from flask import Flask, render_template, request
import handle_email
import stream
import json
from shared import logger
from main import app


@app.route("/")
def home():
    logger.info("Streaming")
    stream.main()
    return "Maybe a GUI somedayyy"


@app.route("/api/email", methods=["POST"])
def email():
    data = request.data.decode("utf-8") 
    logger.info("You've got mail")
    handle_email.main(data)
    return "Thanks"
