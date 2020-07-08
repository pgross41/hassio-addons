import argparse
import base64
import dropbox
import email
import logging
import io
import re
import sys

from datetime import datetime
from shared import get_logger

####################################################################################################
#
# Parse image from dvr163 email and upload it to dropbox
#
####################################################################################################

# Read arguments
parser = argparse.ArgumentParser(description='Upload dvr163 images to Dropbox')
parser.add_argument(
    'infile',
    nargs='?',
    type=argparse.FileType('r'),
    default=sys.stdin, 
    help='MIME-encoded email file(if empty, stdin will be used)')
parser.add_argument(
    '--access_token',
    required=True)
parser.add_argument(
    '--log_level',
    default='40',
    help='10=debug 20=info 30=warning 40=error',
    type=int)
args = parser.parse_args()

# Configure logging
logger = get_logger(args.log_level)
logger.debug(args)

# Initialize Dropbox client
dbx = dropbox.Dropbox(args.access_token)

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
date = text_parts[1][5:15]
time = re.sub(r'[-:]', '.', text_parts[1][16:])

# Read the image
image_part = msg.get_payload(1).get_payload()
file_name = date + '/' + time + '.jpg'
file = io.BytesIO(base64.b64decode(image_part.encode('ascii'))).read()

# Upload
logger.debug('Uploading ' + file_name)
file_data = dbx.files_upload(file, '/ch' + channel_number + '/' + file_name, mute=True)

logger.info('Successfully uploaded ' + file_name + ' to Dropbox')
