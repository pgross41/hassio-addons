import base64
import dropbox
import email
import io
import logging
import re
import smtplib
import sys

# Configuration
# TODO: Make configurable
log_level = "10"
dropbox_access_token = None
email_host = 'smtp.gmail.com'
email_port = 587
email_username = None
email_password = None
email_from_addr = None
email_to_addr = None


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
    logger.debug('Uploading ' + file_name)
    # file_data = dbx.files_upload(file, '/ch' + channel_number + '/' + file_name, mute=True)
    file_data = dbx.files_upload(file, '/ch' + '0' + '/' + file_name, mute=True)

    logger.info('Successfully uploaded ' + file_name + ' to Dropbox')  


def to_email(msg_data):
    server = smtplib.SMTP(email_host, email_port)
    server.starttls()
    server.login(email_username, email_password)
    server.sendmail(email_from_addr, email_to_addr, msg_data)
    server.quit()
    logger.debug("Sent")


# Log to stdout
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG) 
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
logger.addHandler(handler) 
logger.info('Ready!')

# Accept a file name, otherwise read from stdin
email_data=""
if(sys.argv[1]): 
    f = open(sys.argv[1], "r")
    email_data = f.read() 
    f.close()
else:
    email_data = sys.stdin.read()
    sys.stdin.close()

logger.debug('in:\n' + email_data)
msg = email.message_from_string(email_data)    

# Do things with the email
# TODO: Run only ones that are configured
to_dropbox(msg)
to_email(email_data)