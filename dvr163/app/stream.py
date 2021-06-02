# Set OPTIONS_PATH and view output via: python3 stream.py | ffplay -i pipe:
# or write to file
write_to_files = False
from shared import options, logger
import socket
import time
import datetime
import sys

def main(channel_number = 0, stream = 0):

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
    s.send(pre + pad(b'\x00\x0a', 6) + pad(bytes([channel_number]), 4) + pad(bytes([stream]), 4) + pad(unknownByte, 8))
    s.setblocking(0)
    if write_to_files:
        logger.info("Connected")
        timestamp = datetime.datetime.now().isoformat().replace(":", "-")
        dump = open(timestamp + '-socket.dump', 'wb')
        # os.mkfifo(timestamp + '-socket.h264')
        h264 = open(timestamp + '-socket.h264', 'wb')
        g711 = open(timestamp + '-socket.g711', 'wb')
    else:
        dump = None
        g711 = None
        h264 = sys.stdout.buffer

    g711_prelude = b'\xaa\x00\x00\x00'
    # decode with ```sox --channels 1 --type raw --rate 8000 -e a-law ~/Downloads/audio.g711 output.wav``` then write as http://en.wikipedia.org/wiki/Au_file_format
    h264_prelude = b'\x00\x00\x00\x01'
    in_h264 = False

    try:
        while True:
            try:
                data = s.recv(16)
                before_data = None
                dump.write(data) if write_to_files else None

                if g711_prelude in data:
                    idx = data.index(g711_prelude)
                    logger.info("g711 @ " + str(idx))
                    before_data = data[:idx]
                    data = data[idx:]
                    if in_h264:
                        h264.write(before_data)
                    else:
                        g711.write(before_data) if write_to_files else None

                    h264.flush()
                    g711.flush() if write_to_files else None
                    in_h264 = False
                if h264_prelude in data:
                    idx = data.index(h264_prelude)
                    logger.info("h264 @ " + str(idx))
                    before_data = data[:idx]
                    data = data[idx:]
                    if in_h264:
                        h264.write(before_data)
                    else:
                        g711.write(before_data) if write_to_files else None

                    h264.flush()
                    g711.flush() if write_to_files else None
                    in_h264 = True

                if in_h264:
                    h264.write(data)
                else:
                    g711.write(data) if write_to_files else None
            except BlockingIOError:
                time.sleep(.1)
                pass

    # https://docs.python.org/2/howto/sockets.html#disconnecting
    except BrokenPipeError:
        logger.info("Shutting down - Broken pipe") if write_to_files else None
        s.shutdown(1)
        s.close()
    except KeyboardInterrupt:
        logger.info("Shutting down - Keyboard interrupt") if write_to_files else None
        h264.close()
        g711.close() if write_to_files else None
        dump.close() if write_to_files else None
        s.shutdown(1)
        s.close()


# Support directly calling from command line with a file path containing the email_data
if __name__ == "__main__":
    main(0, 0)
