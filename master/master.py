from flask import Flask, request
import os

app = Flask(__name__)

file_to_chunkserver = {}
chunkservers = os.getenv("CHUNKSERVERS").split(",")
print(chunkservers)
lastChunkserver = 0


@app.route("/file", methods=["GET"])
def get_file():
    filename = request.args.get("filename")
    if filename not in file_to_chunkserver:
        global lastChunkserver
        lastChunkserver = (lastChunkserver + 1) % len(chunkservers)
        file_to_chunkserver[filename] = chunkservers[lastChunkserver]
    return {"url": file_to_chunkserver[filename]}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
