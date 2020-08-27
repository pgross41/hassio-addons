import json
import logging
import os
import sys


# Read config from options.json
options_path = os.environ.get("OPTIONS_PATH", "/data/options.json")
with open(options_path) as f:
    options = json.load(f)


# Log to stdout
logger = logging.getLogger(__name__)
logger.setLevel(options["log_level"])
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
logger.addHandler(handler)
