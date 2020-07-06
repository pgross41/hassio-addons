import argparse
import datetime
import dropbox
import email
import json
import logging
import io
import re
import requests
import sys

from datetime import datetime
from shared import get_logger, init_exception_handler


####################################################################################################
#
# Parse a dvr163 email and POST the info to an HTTP endpoint
# Note: this only sends the metadata (channel number, timestamp, etc.)
#
# To use with Home Assistant:
#   Use email2file to write the file to disk and configure home assistant to use that file
#
####################################################################################################

# Read arguments
parser = argparse.ArgumentParser(description='Send dvr163 messages to Home Asistant')
parser.add_argument(
    'infile',
    nargs='?',
    type=argparse.FileType('r'),
    default=sys.stdin,
    help='MIME-encoded email file(if empty, stdin will be used)')
parser.add_argument('--url', required=True, help='the endpoint of the home assistant API to POST to')
parser.add_argument('--auth_header', help='Authorization header for http request')
parser.add_argument('--log_level', default='40', help='10=debug 20=info 30=warning 40=error', type=int)
parser.add_argument('--log_file', default='email2http.log', help='Log file location', type=str)
args = parser.parse_args()

# Configure logging
logger = get_logger(args.log_level, args.log_file)
logger.debug(args)

# Log exceptions
init_exception_handler(logger)

# Read infile (is stdin if no arg)
stdin_data = args.infile.read()
args.infile.close()
logger.debug('in:\n' + stdin_data)
msg = email.message_from_string(stdin_data)

# Parse out the html text
html_part = msg.get_payload(0).get_payload()
clean_html = re.sub(r'(?is)<(script|style).*?>.*?(</\1>)', '', html_part.strip()) # Remove style tags
html_text = re.sub(r'(?s)<.*?>', ' ', clean_html).strip() # Get text content
text_parts = html_text.split("; ")
logger.debug('Found HTML text: ' + html_text)
channel_number = text_parts[0][-1:]
message = text_parts[0][6:]
file_name = re.sub(r' ', '_', re.sub(r'[-:]', '', text_parts[1][5:]))
file_name_formatted = datetime.strptime(text_parts[1][5:], '%Y-%m-%d %H:%M:%S').strftime("%a %b %d, %I:%M:%S %p")
timestamp = datetime.now().strftime("%a %b %d, %I:%M:%S %p")

# Send
logger.debug('Sending POST request')

data = {
    "channel_number": channel_number,
    "file_name": file_name,
    "message": message,
    "timestamp": timestamp,
}
headers = {
    "Authorization": args.auth_header,
    "Content-Type": "application/json",
}
response = requests.post(args.url, data=json.dumps(data), headers=headers)

logger.info('Success')
