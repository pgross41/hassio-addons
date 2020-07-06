import argparse
import logging
import smtplib
import sys

from shared import get_logger, init_exception_handler


####################################################################################################
#
# Forward a raw email via SMTP
#
####################################################################################################

# Read arguments
parser = argparse.ArgumentParser(description='Forward messages via SMTP')
parser.add_argument(
    'infile',
    nargs='?',
    type=argparse.FileType('r'),
    default=sys.stdin,
    help='MIME-encoded email file(if empty, stdin will be used)')
parser.add_argument('--username', required=True)
parser.add_argument('--password', required=True)
parser.add_argument('--from_addr', required=True)
parser.add_argument('--to_addr', required=True)
parser.add_argument('--host', default='smtp.gmail.com')
parser.add_argument('--port', default='587', type=int)
parser.add_argument('--log_level', default='40', help='10=debug 20=info 30=warning 40=error', type=int)
parser.add_argument('--log_file', default='email2email.log', help='Log file location', type=str)
args = parser.parse_args() 

# Configure logging
logger = get_logger(args.log_level, args.log_file)
logger.debug(args)

# Log exceptions
init_exception_handler(logger)   

# Read infile (is stdin if no arg)
stdin_data = args.infile.read()
args.infile.close()

# Send the message
server = smtplib.SMTP(args.host, args.port)
server.starttls()
server.login(args.username, args.password)
server.sendmail(args.from_addr, args.to_addr, stdin_data)
server.quit()
logger.debug("Sent")
