from flask import Flask, request
import requests
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
app = Flask(__name__)

MASTER_URL = os.getenv("MASTER_URL")
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE"))


@app.route("/file", methods=["PUT"])
def create_file():
    filename = request.json.get("filename")
    data = request.json.get("data")
    logger.info(f"Request to WRITE file {filename}")
    chunks = [data[i : i + CHUNK_SIZE] for i in range(0, len(data), CHUNK_SIZE)]
    for chunk in chunks:
        response = requests.post(
            f"{MASTER_URL}/chunk", json={"filename": filename}
        ).json()
        chunk_uuid = response["uuid"]
        chunk_server_url = response["url"]
        logger.info(
            f"SENDING chunk {chunk_uuid} of file {filename} to chunkserver {chunk_server_url}"
        )
        requests.post(
            f"{chunk_server_url}/chunk", json={"uuid": chunk_uuid, "data": chunk}
        )
    return {"status": "File created"}


@app.route("/file", methods=["GET"])
def read_file():
    filename = request.args.get("filename")
    logger.info(f"Request to READ file {filename}")
    file_data = ""
    chunk_index = 0
    while True:
        response = requests.get(
            f"{MASTER_URL}/chunk",
            params={"filename": filename, "chunk_index": chunk_index},
        )
        if response.status_code == 404:
            break

        response = response.json()
        chunk_uuid = response["uuid"]
        chunk_server_url = response["url"]
        logger.info(
            f"SENDING chunk {chunk_uuid} of file {filename} to chunkserver {chunk_server_url}"
        )
        chunk_data = requests.get(
            f"{chunk_server_url}/chunk", params={"uuid": chunk_uuid}
        ).json()["data"]
        file_data += chunk_data
        chunk_index += 1

    return {"data": file_data}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
