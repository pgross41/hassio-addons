import argparse
import email
import logging
import io
import re
import sys

from datetime import datetime
from shared import get_logger, init_exception_handler


####################################################################################################
#
# Parse image from a raw email and save it to disk
# This is super specific to uploading the image from dvr163 emails
#
####################################################################################################

# Read arguments
parser = argparse.ArgumentParser(description='Save images from email')
parser.add_argument(
    'infile',
    nargs='?',
    type=argparse.FileType('r'),
    default=sys.stdin,
    help='MIME-encoded email file(if empty, stdin will be used)')
parser.add_argument('--out_directory', required=True)
parser.add_argument('--log_level', default='40', help='10=debug 20-info 30=warning 40=error', type=int)
parser.add_argument('--log_file', default='email2file.log', help='Log file location', type=str)
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
timestamp = re.sub(r' ', '_', re.sub(r'[-:]', '', text_parts[1][5:]))

# Read the image
image_part = msg.get_payload(1).get_payload()
file_name = timestamp + '.jpg'
file = io.BytesIO(image_part.decode('base64')).read()

# Save
out_path = args.out_directory + '/snapshot_cam_' + channel_number + '.jpg'
logger.debug('Saving ' + out_path)
out_file = open(out_path, "w")
out_file.write(file)
out_file.close()

logger.info('Saved ' + file_name)
