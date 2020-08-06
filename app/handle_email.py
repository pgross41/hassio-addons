import base64
from shared import options, logger
import dropbox
import email
import io
import re
import smtplib
import sys

# Parse email and upload to dropbox
def to_dropbox(msg):

    # Initialize Dropbox client
    dbx = dropbox.Dropbox(options["dropbox"]["access_token"])

    # Parse out the html text
    # TODO: Simplify with this? https://www.crummy.com/software/BeautifulSoup/bs4/doc/
    html_part = msg.get_payload(0).get_payload()
    # Remove style tags
    clean_html = re.sub(r"(?is)<(script|style).*?>.*?(</\1>)", "", html_part.strip())
    # Get text content
    html_text = re.sub(r"(?s)<.*?>", " ", clean_html).strip()
    text_parts = html_text.split("; ")
    logger.debug("Found HTML text: " + html_text)
    channel_number = text_parts[0][-1:]
    date = text_parts[1][5:15]
    time = re.sub(r"[-:]", ".", text_parts[1][16:])

    # Read the image
    image_part = msg.get_payload(1).get_payload()
    file_name = date + "/" + time + ".jpg"
    file = io.BytesIO(base64.b64decode(image_part.encode("ascii"))).read()

    # Upload
    file_path = "/ch" + channel_number + "/" + file_name
    logger.debug("Uploading " + file_path)
    file_data = dbx.files_upload(file, file_path, mute=True)

    logger.info("Uploaded " + file_path + " to Dropbox")


# Forward email somewhere else
def to_email(msg_data):
    username = options["email"]["username"]
    server = smtplib.SMTP(options["email"]["host"], options["email"]["port"])
    server.starttls()
    server.login(username, options["email"]["password"])
    # Ues the username as the from and to
    server.sendmail(username, username, msg_data)
    server.quit()
    logger.info("Email forwarded to " + username)


###############################################################################
# Main
###############################################################################


def main(email_data):

    # Parse email data into an email
    logger.debug("email_data:\n" + email_data)
    msg = email.message_from_string(email_data)

    # Do things with the email
    dropbox_enabled = options["dropbox"]["enabled"]
    email_enabled = options["email"]["enabled"]

    if not (dropbox_enabled) and not (email_enabled):
        logger.error("Message received but no destinations enabled!")
        sys.exit()

    if dropbox_enabled:
        try:
            to_dropbox(msg)
        except:
            logger.error("Error uploading to dropbox: " + str(sys.exc_info()))

    if email_enabled:
        try:
            to_email(email_data)
        except:
            logger.error("Error forwarding email: " + str(sys.exc_info()))


# Support directly calling from command line with a file path containing the email_data
if __name__ == "__main__":
    f = open(sys.argv[1], "r")
    email_data = f.read()
    f.close()
    main(email_data)
