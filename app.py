from flask import Flask, request, jsonify, make_response
import os
# pip install ping3
from ping3 import ping
import subprocess
import socket

app = Flask(__name__)


def icmp_ping(host):
    try:
        
        result = ping(host, timeout=3)
        if result is not None and result is not False:
            return True, round(result * 1000, 2) 
        else:
            return False, None
    except Exception as e:
        print(f"Error using ping3: {e}")
        
        try:
            
            if not socket.inet_aton(host) and not all(c.isalnum() or c in '.-:[]' for c in host):
                return False, None
            result = subprocess.run(
                ["ping", "-c", "1", "-W", "3", str(host)], 
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=5
            )
            if result.returncode == 0:
               
                return True, "N/A (subprocess)"
            else:
                return False, None
        except subprocess.TimeoutExpired:
            print("Ping subprocess timed out")
            return False, None
        except Exception as e2:
            print(f"Error using subprocess: {e2}")
            return False, None


@app.route('/ping')
def check():
   
    target = request.args.get('target') or request.args.get('host')

    if not target:
        response = make_response(jsonify({"error": "Missing 'target' or 'host' parameter"}), 400)
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response

    
    if not all(c.isalnum() or c in '.-:[]_' for c in target):
        response = make_response(jsonify({"error": "Invalid 'target' format"}), 400)
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response

    alive, time_ms = icmp_ping(target)

    response_data = {
        "target": target,
        "alive": alive
    }
    if time_ms is not None:
        response_data["time_ms"] = time_ms

    response = make_response(jsonify(response_data), 200)
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response


@app.route('/')
def index():
    response = make_response(jsonify({"message": "ICMP Ping Server is running"}), 200)
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
