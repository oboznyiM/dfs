from flask import Flask, request
import os
import logging
import uuid

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

chunkservers = os.getenv("CHUNKSERVERS").split(",")
lastChunkserver = 0
file_mappings = {}
chunk_mappings = {}


def select_chunk_server():
    global lastChunkserver
    lastChunkserver = (lastChunkserver + 1) % len(chunkservers)
    return chunkservers[lastChunkserver]


@app.route("/chunk", methods=["POST"])
def create_chunk_mapping():
    filename = request.json.get("filename")
    chunk_uuid = str(uuid.uuid4())
    chunk_server = select_chunk_server()
    if filename not in file_mappings:
        file_mappings[filename] = []
    file_mappings[filename].append(chunk_uuid)
    chunk_mappings[chunk_uuid] = chunk_server
    logger.info(
        f"Assigned chunkserver {chunk_server} to chunk index {len(file_mappings) - 1} from file {filename}"
    )
    return {"url": chunk_server, "uuid": chunk_uuid}


@app.route("/chunk", methods=["GET"])
def get_chunk_mapping():
    filename = request.args.get("filename")
    chunk_index = int(request.args.get("chunk_index"))
    if chunk_index >= len(file_mappings.get(filename, [])):
        return {"status": "Chunk not found"}, 404
    chunk_uuid = file_mappings[filename][chunk_index]
    chunk_server = chunk_mappings[chunk_uuid]
    logger.debug(
        f"Found chunk index {chunk_index} from file {filename} on chunkserver {chunk_server}"
    )
    return {"url": chunk_server, "uuid": chunk_uuid}


@app.route("/chunk", methods=["DELETE"])
def delete_chunk_mapping():
    filename = request.args.get("filename")
    logger.info(f"Request to DELETE chunk mapping for file {filename}")

    if filename not in file_mappings or len(file_mappings[filename]) == 0:
        return {"status": "File not found"}, 404

    chunk_uuid = file_mappings[filename].pop(0)
    logger.debug(
        f"Found and deleted chunk index {chunk_uuid} from file {filename} on chunkserver {chunk_mappings[chunk_uuid]}"
    )
    if len(file_mappings[filename]) == 0:
        del file_mappings[filename]

    return {"chunk_uuid": chunk_uuid, "chunkserver_url": chunk_mappings[chunk_uuid]}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
