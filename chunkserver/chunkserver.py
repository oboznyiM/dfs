import requests
import threading
import os
from time import sleep
from flask import Flask, request
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
DATA_DIR = "/data"

HEARTBEAT_INTERVAL = int(os.getenv("HEARTBEAT_INTERVAL", 5))
MASTER_URL = os.getenv("MASTER_URL")
SELF_URL = os.getenv("SELF_URL")


def send_heartbeat():
    while True:
        requests.post(f"{MASTER_URL}/heartbeat", data={"chunkserver_url": SELF_URL})
        sleep(HEARTBEAT_INTERVAL)


heartbeat_thread = threading.Thread(target=send_heartbeat)
heartbeat_thread.start()


@app.route("/chunk", methods=["POST"])
def create_chunk():
    chunk_uuid = request.json.get("uuid")
    data = request.json.get("data")
    logger.info(f"SAVING chunk {chunk_uuid}")
    with open(os.path.join(DATA_DIR, chunk_uuid), "w") as file:
        file.write(data)
    return {"status": "Chunk created"}


@app.route("/chunk", methods=["GET"])
def read_chunk():
    chunk_uuid = request.args.get("uuid")
    with open(os.path.join(DATA_DIR, chunk_uuid), "r") as file:
        data = file.read()
    logger.info(f"SENDING chunk {chunk_uuid} to the client")
    return {"data": data}


@app.route("/chunk", methods=["DELETE"])
def delete_chunk():
    chunk_uuid = request.args.get("chunk_uuid")

    if not os.path.isfile(os.path.join(DATA_DIR, chunk_uuid)):
        return {"status": "Chunk not found"}, 404

    os.remove(os.path.join(DATA_DIR, chunk_uuid))

    return {"status": "Chunk deleted"}


@app.route("/chunk/size", methods=["GET"])
def get_chunk_size():
    chunk_uuid = request.args.get("chunk_uuid")

    if not os.path.isfile(os.path.join(DATA_DIR, chunk_uuid)):
        return {"status": "Chunk not found"}, 404

    size = os.path.getsize(os.path.join(DATA_DIR, chunk_uuid))

    return {"size": size}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
