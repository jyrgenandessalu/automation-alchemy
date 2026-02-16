from flask import Flask, jsonify, render_template_string
import socket, os, psutil

app = Flask(__name__)

@app.route("/")
def home():
    role = os.getenv("ROLE", "unknown")
    # Prefer VM hostname if passed in as ENV variable
    host = os.getenv("HOST_VM", socket.gethostname())
    return f"Hello from {role} on {host}! (containerized) ✅ Updated via CI/CD! REVIEW TEST!!!"

@app.route("/metrics")
def metrics():
    mem = psutil.virtual_memory()
    cpu = psutil.cpu_percent(interval=0.2)
    disk = psutil.disk_usage('/')
    # Prefer VM hostname if passed in as ENV variable
    hostname = os.getenv("HOST_VM", socket.gethostname())
    role = os.getenv("ROLE", "unknown")
    
    metrics_data = {
        "hostname": hostname,
        "role": role,
        "cpu_percent": round(cpu, 2),
        "memory_percent": round(mem.percent, 2),
        "memory_used_gb": round(mem.used / (1024**3), 2),
        "memory_total_gb": round(mem.total / (1024**3), 2),
        "disk_percent": round(disk.percent, 2),
        "disk_used_gb": round(disk.used / (1024**3), 2),
        "disk_total_gb": round(disk.total / (1024**3), 2)
    }
    
    # Return JSON for API calls
    return jsonify(metrics_data)

@app.route("/dashboard")
def dashboard():
    """HTML dashboard displaying infrastructure metrics"""
    mem = psutil.virtual_memory()
    cpu = psutil.cpu_percent(interval=0.2)
    disk = psutil.disk_usage('/')
    hostname = os.getenv("HOST_VM", socket.gethostname())
    role = os.getenv("ROLE", "unknown")
    
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Infrastructure Metrics - {{ hostname }}</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            h1 { color: #333; }
            .metric { margin: 15px 0; padding: 15px; background: #f9f9f9; border-left: 4px solid #4CAF50; }
            .metric-label { font-weight: bold; color: #666; }
            .metric-value { font-size: 24px; color: #333; margin-top: 5px; }
            .bar { background: #e0e0e0; height: 30px; border-radius: 15px; margin-top: 10px; overflow: hidden; }
            .bar-fill { height: 100%; background: linear-gradient(90deg, #4CAF50, #8BC34A); transition: width 0.3s; }
            .warning { border-left-color: #ff9800; }
            .critical { border-left-color: #f44336; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🖥️ Infrastructure Metrics Dashboard</h1>
            <div class="metric">
                <div class="metric-label">Server Hostname</div>
                <div class="metric-value">{{ hostname }}</div>
            </div>
            <div class="metric">
                <div class="metric-label">Server Role</div>
                <div class="metric-value">{{ role }}</div>
            </div>
            <div class="metric {{ 'warning' if cpu > 70 else '' }} {{ 'critical' if cpu > 90 else '' }}">
                <div class="metric-label">CPU Usage</div>
                <div class="metric-value">{{ cpu }}%</div>
                <div class="bar">
                    <div class="bar-fill" style="width: {{ cpu }}%"></div>
                </div>
            </div>
            <div class="metric {{ 'warning' if mem.percent > 70 else '' }} {{ 'critical' if mem.percent > 90 else '' }}">
                <div class="metric-label">Memory Usage</div>
                <div class="metric-value">{{ mem.percent }}% ({{ mem.used_gb }} GB / {{ mem.total_gb }} GB)</div>
                <div class="bar">
                    <div class="bar-fill" style="width: {{ mem.percent }}%"></div>
                </div>
            </div>
            <div class="metric {{ 'warning' if disk.percent > 70 else '' }} {{ 'critical' if disk.percent > 90 else '' }}">
                <div class="metric-label">Disk Usage</div>
                <div class="metric-value">{{ disk.percent }}% ({{ disk.used_gb }} GB / {{ disk.total_gb }} GB)</div>
                <div class="bar">
                    <div class="bar-fill" style="width: {{ disk.percent }}%"></div>
                </div>
            </div>
            <p style="margin-top: 20px; color: #666; font-size: 12px;">
                <strong>Significance:</strong> These metrics help monitor server health, resource utilization, 
                and capacity planning. CPU and memory usage indicate current load, while disk usage helps 
                prevent storage issues. Monitoring these metrics is essential for maintaining infrastructure 
                reliability and performance.
            </p>
        </div>
    </body>
    </html>
    """
    
    return render_template_string(html_template,
        hostname=hostname,
        role=role,
        cpu=round(cpu, 2),
        mem={
            'percent': round(mem.percent, 2),
            'used_gb': round(mem.used / (1024**3), 2),
            'total_gb': round(mem.total / (1024**3), 2)
        },
        disk={
            'percent': round(disk.percent, 2),
            'used_gb': round(disk.used / (1024**3), 2),
            'total_gb': round(disk.total / (1024**3), 2)
        }
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
