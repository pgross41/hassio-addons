from datetime import datetime
from flask import Flask, render_template, request, Response
import handle_email
import stream
import json
from shared import logger
from main import app



@app.route("/api/stream")
def home():
    logger.info("Begin stream")
    return Response(stream.main(), mimetype='audio/mpeg4-generic')


@app.route("/api/email", methods=["POST"])
def email():
    data = request.data.decode("utf-8")
    logger.info("You've got mail")
    handle_email.main(data)
    return "Thanks"
