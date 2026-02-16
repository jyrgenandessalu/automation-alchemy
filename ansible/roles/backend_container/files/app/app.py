from flask import Flask, jsonify
import socket, os, psutil

app = Flask(__name__)

@app.route("/")
def home():
    role = os.getenv("ROLE", "unknown")
    # Prefer VM hostname if passed in as ENV variable
    host = os.getenv("HOST_VM", socket.gethostname())
    return f"Hello from {role} on {host}! (containerized) ✅ Updated via CI/CD!"

@app.route("/metrics")
def metrics():
    mem = psutil.virtual_memory()
    cpu = psutil.cpu_percent(interval=0.2)
    # Prefer VM hostname if passed in as ENV variable
    return jsonify({
        "hostname": os.getenv("HOST_VM", socket.gethostname()),
        "role": os.getenv("ROLE", "unknown"),
        "cpu_percent": cpu,
        "memory_percent": mem.percent
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
