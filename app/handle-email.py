import base64
import dropbox
import email
import io
import logging
import os
import re
import smtplib
import sys

###############################################################################
# Configuration
###############################################################################

# General 
log_level = int(os.environ.get('log_level', 10))

# Dropbox
dropbox_enabled = bool(os.environ.get('dropbox_enabled', False))
dropbox_access_token = os.environ.get('dropbox_access_token', None)

# Email
email_enabled = bool(os.environ.get('email_enabled', False))
email_host = os.environ.get('email_host', 'smtp.gmail.com')
email_port = os.environ.get('email_port', 587)
email_username = os.environ.get('email_username', None)
email_password = os.environ.get('email_password', None)
email_from_addr = os.environ.get('email_from_addr', None)
email_to_addr = os.environ.get('email_to_addr', None)

###############################################################################
# Destinations
###############################################################################

# Parse email and upload to dropbox
def to_dropbox(msg):

    # Initialize Dropbox client
    dbx = dropbox.Dropbox(dropbox_access_token)
    
    # Parse out the html text
    # TODO: Simplify with this? https://www.crummy.com/software/BeautifulSoup/bs4/doc/ 
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
    file_path = '/ch' + channel_number + '/' + file_name
    logger.debug('Uploading ' + file_path)
    file_data = dbx.files_upload(file, file_path, mute=True)

    logger.info('Uploaded ' + file_path + ' to Dropbox')  

# Forward email somewhere else
def to_email(msg_data):
    server = smtplib.SMTP(email_host, email_port)
    server.starttls()
    server.login(email_username, email_password)
    server.sendmail(email_from_addr, email_to_addr, msg_data)
    server.quit()
    logger.info("Email sent")

###############################################################################
# Main
###############################################################################

# Log to stdout
logger = logging.getLogger(__name__)
logger.setLevel(log_level) 
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
logger.addHandler(handler) 
logger.info('Starting')

# Accept a file name, otherwise read from stdin
email_data=""
if(sys.argv[1]):  # Todo: This is throwing index out of range
    f = open(sys.argv[1], "r")
    email_data = f.read() 
    f.close()
else:
    email_data = sys.stdin.read()
    sys.stdin.close()
logger.debug('email_data:\n' + email_data)
msg = email.message_from_string(email_data)    

# Do things with the email
if(not(dropbox_enabled) and not(email_enabled)): 
    logger.error("Message received but no desitnations enabled!")
    sys.exit()

if(dropbox_enabled): 
    try: 
        to_dropbox(msg)
    except:
        logger.error( "Error uploading to dropbox: " + sys.exc_info()[0] )

if(email_enabled): 
    try: 
        to_email(email_data)
    except: 
        logger.error( "Error forwarding email: " + sys.exc_info()[0] )

