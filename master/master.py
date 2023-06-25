from flask import Flask, request

app = Flask(__name__)

file_to_chunkserver = {}


@app.route("/file", methods=["GET"])
def get_file():
    filename = request.args.get("filename")
    if filename not in file_to_chunkserver:
        # Hardcoded for now, in real scenario should be load balanced
        file_to_chunkserver[filename] = "http://chunkserver:5000"
    return {"url": file_to_chunkserver[filename]}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
