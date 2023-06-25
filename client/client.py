from flask import Flask, request
import requests
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
app = Flask(__name__)

MASTER_URL = os.getenv("MASTER_URL")


@app.route("/file", methods=["PUT"])
def create_file():
    filename = request.json.get("filename")
    data = request.json.get("data")
    logger.info(f"Request to WRITE file {filename}")
    logger.info(f"The content of the file is {data}")
    chunkserver_url = requests.get(
        f"{MASTER_URL}/file", params={"filename": filename}
    ).json()["url"]
    logger.info(f"WRITING file {filename} to chunkserver {chunkserver_url}")
    requests.post(f"{chunkserver_url}/file", json={"filename": filename, "data": data})
    return {"status": "File created"}


@app.route("/file", methods=["GET"])
def read_file():
    filename = request.args.get("filename")
    logger.info(f"Request to READ file {filename}")
    chunkserver_url = requests.get(
        f"{MASTER_URL}/file", params={"filename": filename}
    ).json()["url"]

    logger.info(f"READING file {filename} from chunkserver {chunkserver_url}")
    file_data = requests.get(
        f"{chunkserver_url}/file", params={"filename": filename}
    ).json()["data"]
    return {"data": file_data}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
