import psutil
import platform
from flask import Flask, render_template_string
import threading

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>System Monitor</title>
    <meta http-equiv="refresh" content="5">
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; padding: 20px; }
        h1 { color: #333; }
        .info { background: #f4f4f4; padding: 10px; margin-bottom: 10px; border-radius: 5px; }
    </style>
</head>
<body>
    <h1>System Monitor</h1>
    <div class="info">
        <h2>Device Information</h2>
        <p>System: {{ system }}</p>
        <p>Node Name: {{ node_name }}</p>
        <p>Release: {{ release }}</p>
        <p>Version: {{ version }}</p>
        <p>Machine: {{ machine }}</p>
        <p>Processor: {{ processor }}</p>
    </div>
    <div class="info">
        <h2>CPU Usage</h2>
        <p>{{ cpu_usage }}%</p>
    </div>
    <div class="info">
        <h2>Memory Usage</h2>
        <p>Total: {{ memory.total }} GB</p>
        <p>Available: {{ memory.available }} GB</p>
        <p>Used: {{ memory.used }} GB ({{ memory.percent }}%)</p>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    cpu_usage = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    return render_template_string(HTML_TEMPLATE,
        system=platform.system(),
        node_name=platform.node(),
        release=platform.release(),
        version=platform.version(),
        machine=platform.machine(),
        processor=platform.processor(),
        cpu_usage=cpu_usage,
        memory={
            'total': round(memory.total / (1024.0 ** 3), 2),
            'available': round(memory.available / (1024.0 ** 3), 2),
            'used': round(memory.used / (1024.0 ** 3), 2),
            'percent': memory.percent
        }
    )

def run_flask():
    app.run(host='0.0.0.0', port=5000)

if __name__ == '__main__':
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()
    flask_thread.join()