# Set OPTIONS_PATH and view output via: python3 stream.py | ffplay -i pipe:
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
    stdout = sys.stdout.buffer

    g711_prelude = b'\xaa\x00\x00\x00'
    h264_prelude = b'\x00\x00\x00\x01'
    in_h264 = False

    try:
        while True:
            try:
                data = s.recv(16)
                before_data = None

                if g711_prelude in data:
                    idx = data.index(g711_prelude)
                    before_data = data[:idx]
                    data = data[idx:]
                    if in_h264:
                        stdout.write(before_data)
                    stdout.flush()
                    in_h264 = False
                if h264_prelude in data:
                    idx = data.index(h264_prelude)
                    before_data = data[:idx]
                    data = data[idx:]
                    if in_h264:
                        stdout.write(before_data)

                    stdout.flush()
                    in_h264 = True

                if in_h264:
                    stdout.write(data)
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
    main(0, 0)
