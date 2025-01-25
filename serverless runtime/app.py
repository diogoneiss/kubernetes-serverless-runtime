import datetime
import json
import logging
import os
import time
from dataclasses import field, dataclass
from importlib.util import find_spec
from pathlib import Path

from dotenv import load_dotenv


import redis
import usermodule as lf

load_dotenv()


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("runtime.log", mode='w+'),
        logging.StreamHandler()
    ]
)

SERVERLESS_FILE_PATH = Path("./") / "usermodule.py"

@dataclass
class Context:
    host: str
    port: int
    input_key: str
    output_key: str
    function_getmtime: str = field(init=False)
    last_execution: datetime.datetime = field(default=None)
    env: dict = field(default_factory=dict)

    def __post_init__(self):
        tmp = os.path.getmtime(SERVERLESS_FILE_PATH)
        self.function_getmtime = datetime.datetime.fromtimestamp(tmp).strftime('%Y-%m-%d %H:%M:%S')

    def after_execution(self):
        self.last_execution = datetime.datetime.now()

def get_env_variable(key, default=None, required=False):
    value = os.environ.get(key, default)
    if required and not value:
        logging.error(f"Environment variable `{key}` is required but not set.")
        exit(1)
    return value

REDIS_HOST = get_env_variable("REDIS_HOST", default="localhost")
REDIS_PORT = int(get_env_variable("REDIS_PORT", default=6379))
REDIS_INPUT_KEY = get_env_variable("REDIS_INPUT_KEY", required=True)
REDIS_OUTPUT_KEY = get_env_variable("REDIS_OUTPUT_KEY")
INTERVAL_TIME = int(get_env_variable("INTERVAL", default=5))

logging.info(f"Redis Host: {REDIS_HOST}")
logging.info(f"Redis Port: {REDIS_PORT}")
logging.info(f"Input Key: {REDIS_INPUT_KEY}")
logging.info(f"Output Key: {REDIS_OUTPUT_KEY}")
logging.info(f"Interval Time: {INTERVAL_TIME}")

redis_conn = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, charset="utf-8", decode_responses=True)

def fetch_data(redis_conn: redis.client.Redis, key: str):
    try:
        return redis_conn.get(key)
    except Exception:
        logging.exception("Runtime data still not available, please wait")
        return None

def process_data(data):
    try:
        return json.loads(data)
    except Exception:
        logging.exception("Error deserializing data. Ensure the input is valid JSON.")
        return None

def handle_function(data, context, lf):

    try:
        return lf.handler(data, context)
    except Exception:
        logging.exception("Error in Serverless function. Check your `handler` method in usermodule.py.")
        return None

def save_output(redis_conn:  redis.client.Redis, output, key, context: Context):
    try:
        if output and key:
            redis_conn.set(key, json.dumps(output))
        context.after_execution()
    except Exception:
        logging.exception("Error while trying to save result")

def main():

    logging.info("Starting serverless execution...")

    context = Context(host=REDIS_HOST, port=REDIS_PORT,
                      input_key=REDIS_INPUT_KEY, output_key=REDIS_OUTPUT_KEY)

    while True:
        data = fetch_data(redis_conn, REDIS_INPUT_KEY)

        if data:
            parsed_data = process_data(data)

            if parsed_data:
                output = handle_function(parsed_data, context, lf)

                save_output(redis_conn, output, REDIS_OUTPUT_KEY, context)

        time.sleep(INTERVAL_TIME)

if __name__ == "__main__":
    load_dotenv(override=True)

    serverless_script = find_spec(SERVERLESS_FILE_PATH.stem)

    if serverless_script is None:
        logging.error("serverless script from configmap file not found! Check deployment config")
        exit(1)

    main()
