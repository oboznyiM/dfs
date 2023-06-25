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
        print(response)
        chunk_uuid = response["uuid"]
        chunk_server_url = response["url"]
        logger.info(
            f"READING chunk {chunk_uuid} of file {filename} from chunkserver {chunk_server_url}"
        )
        chunk_data = requests.get(
            f"{chunk_server_url}/chunk", params={"uuid": chunk_uuid}
        ).json()["data"]
        file_data += chunk_data
        chunk_index += 1

    return {"data": file_data}


@app.route("/file", methods=["DELETE"])
def delete_file():
    filename = request.args.get("filename")
    logger.info(f"Request to DELETE file {filename}")

    while True:
        chunk_info = requests.delete(
            f"{MASTER_URL}/chunk", params={"filename": filename}
        ).json()

        if "status" in chunk_info and chunk_info["status"] == "File not found":
            break
        logger.info(
            f"DELETING chunk {chunk_info['chunk_uuid']} of file {filename} from chunkserver {chunk_info['chunkserver_url']}"
        )
        requests.delete(
            f"{chunk_info['chunkserver_url']}/chunk",
            params={"chunk_uuid": chunk_info["chunk_uuid"]},
        )

    return {"status": "File deleted"}


@app.route("/file/size", methods=["GET"])
def get_file_size():
    filename = request.args.get("filename")
    logger.info(f"Request to get size of file {filename}")

    size_info = requests.get(
        f"{MASTER_URL}/file/size_info", params={"filename": filename}
    ).json()
    num_chunks = size_info["num_chunks"]
    logger.info(f"RECEIVED INFO ABOUT FILE: {size_info}")

    if num_chunks == 0:
        return {"size": 0}

    last_chunk_size = requests.get(
        f"{size_info['last_chunk_url']}/chunk/size",
        params={"chunk_uuid": size_info["last_chunk_uuid"]},
    ).json()["size"]

    size = CHUNK_SIZE * (num_chunks - 1) + last_chunk_size

    return {"size": size}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
