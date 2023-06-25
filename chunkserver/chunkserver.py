from flask import Flask, request
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
DATA_DIR = "/data"


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


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
