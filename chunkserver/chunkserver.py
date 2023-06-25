from flask import Flask, request
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

files = {}


@app.route("/file", methods=["POST"])
def create_file():
    filename = request.json.get("filename")
    data = request.json.get("data")
    logger.info(f"SAVING file {filename}")
    files[filename] = data
    return {"status": "File stored"}


@app.route("/file", methods=["GET"])
def read_file():
    filename = request.args.get("filename")
    logger.info(f"SENDING content of the file {filename}")
    return {"data": files.get(filename)}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
