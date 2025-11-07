from flask import Flask, request, jsonify
import socket
import os

app = Flask(__name__)

@app.route('/check')
def check():
    host = request.args.get('host')
    port = request.args.get('port', '80')

    if not host:
        return jsonify({"error": "Missing 'host' parameter"}), 400

    try:
        port = int(port)
        if not (1 <= port <= 65535):
            raise ValueError("Invalid port")
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid 'port' parameter"}), 400

    try:
        sock = socket.create_connection((host, port), timeout=5)
        sock.close()
        alive = True
    except:
        alive = False

    return jsonify({
        "host": host,
