# Run manually:
# > set OPTIONS_PATH=%cd%\dvr163\app\dev\env\options.json
# > python3 stream.py | ffplay -i pipe:

from shared import options, logger
import socket
import time
import datetime
import sys


def main(channel_number=0, stream=0):

    if sys.version_info.major < 3:
        sys.exit("Python 3 is required.\n")

    TCP_IP = options["nvr"]["ip"]
    TCP_PORT = options["nvr"]["port"]

    pad = lambda string, length: string.ljust(length, b'\0')
    pre = b'\xaa\x00\x00\x00'

    # Initialize socket connection
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2)
    s.setblocking(1)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.connect((TCP_IP, TCP_PORT))

    # Request the stream... Uhh... No password is required ¯\_(ツ)_/¯
    unknownByte = bytes([1])
    s.send(pre + pad(b'\x00\x0a', 6) + pad(bytes([channel_number]), 4) +
           pad(bytes([stream]), 4) + pad(unknownByte, 8))
    s.setblocking(0)

    logger.info("Connected")

    try:
        while True:
            try:
                yield s.recv(16)
            except BlockingIOError:
                time.sleep(.1)
                pass

    # https://docs.python.org/2/howto/sockets.html#disconnecting
    except BrokenPipeError:
        logger.info("Shutting down - Broken pipe")
        s.shutdown(1)
        s.close()
    except KeyboardInterrupt:
        logger.info("Shutting down - Keyboard interrupt")
        stdout.close()
        s.shutdown(1)
        s.close()


# Support directly calling from command line with a file path containing the email_data
if __name__ == "__main__":
    stdout = sys.stdout.buffer
    generator = main(0, 0)
    while True:
        stdout.write(next(generator))
