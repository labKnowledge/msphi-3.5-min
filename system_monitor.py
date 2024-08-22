import psutil
import platform
from flask import Flask, render_template_string
import threading
import time

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Enhanced Real-time System Monitor</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/3.7.0/chart.min.js"></script>
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            padding: 20px;
            background-color: #f0f0f0;
        }
        h1, h2 {
            color: #333;
            text-align: center;
        }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }
        .card {
            background: #fff;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .card h3 {
            margin-top: 0;
            font-size: 18px;
            color: #555;
        }
        .card p {
            font-size: 24px;
            font-weight: bold;
            margin: 10px 0;
        }
        .card .subtitle {
            font-size: 14px;
            color: #888;
        }
        .cpu { background-color: #FFD700; }
        .memory { background-color: #87CEEB; }
        .disk { background-color: #90EE90; }
        .network { background-color: #D3D3D3; }
        #deviceInfo {
            background-color: #ffffff;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        #deviceInfo p {
            margin: 5px 0;
        }
        #updateTime {
            text-align: center;
            font-style: italic;
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <h1>Enhanced Real-time System Monitor</h1>
    
    <div id="deviceInfo">
        <h2>Device Information</h2>
        <p><strong>System:</strong> {{ system }}</p>
        <p><strong>Node Name:</strong> {{ node_name }}</p>
        <p><strong>Release:</strong> {{ release }}</p>
        <p><strong>Version:</strong> {{ version }}</p>
        <p><strong>Machine:</strong> {{ machine }}</p>
        <p><strong>Processor:</strong> {{ processor }}</p>
    </div>
    
    <div class="grid">
        <div class="card cpu">
            <h3>CPU</h3>
            <p id="cpuUsage">{{ cpu_usage }}%</p>
            <div class="subtitle" id="cpuLoad">Load {{ cpu_load }}</div>
            <canvas id="cpuChart"></canvas>
        </div>
        <div class="card memory">
            <h3>Memory</h3>
            <p id="memoryUsage">{{ memory.percent }}%</p>
            <div class="subtitle" id="memoryDetails">{{ memory.used }} MB / {{ memory.total }} MB</div>
        </div>
        <div class="card disk">
            <h3>Disk</h3>
            <p id="diskUsage">{{ disk.percent }}%</p>
            <div class="subtitle" id="diskDetails">{{ disk.used }} GB / {{ disk.total }} GB</div>
        </div>
        <div class="card network">
            <h3>Network</h3>
            <p id="networkUsage">↓ {{ network.bytes_recv }} MB ↑ {{ network.bytes_sent }} MB</p>
        </div>
    </div>
    
    <p id="updateTime">Last updated: <span id="lastUpdateTime"></span></p>

    <script>
        function updateData() {
            fetch('/data')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('cpuUsage').textContent = data.cpu_usage + '%';
                    document.getElementById('cpuLoad').textContent = 'Load ' + data.cpu_load;
                    document.getElementById('memoryUsage').textContent = data.memory.percent + '%';
                    document.getElementById('memoryDetails').textContent = data.memory.used + ' MB / ' + data.memory.total + ' MB';
                    document.getElementById('diskUsage').textContent = data.disk.percent + '%';
                    document.getElementById('diskDetails').textContent = data.disk.used + ' GB / ' + data.disk.total + ' GB';
                    document.getElementById('networkUsage').textContent = '↓ ' + data.network.bytes_recv + ' MB ↑ ' + data.network.bytes_sent + ' MB';
                    document.getElementById('lastUpdateTime').textContent = new Date().toLocaleTimeString();
                    
                    // Update CPU chart
                    cpuChart.data.labels.push(new Date().toLocaleTimeString());
                    cpuChart.data.datasets[0].data.push(data.cpu_usage);
                    if (cpuChart.data.labels.length > 10) {
                        cpuChart.data.labels.shift();
                        cpuChart.data.datasets[0].data.shift();
                    }
                    cpuChart.update();
                });
        }

        setInterval(updateData, 2000);  // Update every 2 seconds

        // Initialize CPU usage chart
        var ctx = document.getElementById('cpuChart').getContext('2d');
        var cpuChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'CPU Usage',
                    data: [],
                    borderColor: 'rgb(75, 192, 192)',
                    tension: 0.1
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100
                    }
                }
            }
        });
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE, **get_system_info())

@app.route('/data')
def data():
    return get_system_info()

def get_system_info():
    cpu_usage = psutil.cpu_percent(interval=1)
    cpu_load = ", ".join([f"{x:.2f}" for x in psutil.getloadavg()])
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    network = psutil.net_io_counters()
    
    return {
        'system': platform.system(),
        'node_name': platform.node(),
        'release': platform.release(),
        'version': platform.version(),
        'machine': platform.machine(),
        'processor': platform.processor(),
        'cpu_usage': cpu_usage,
        'cpu_load': cpu_load,
        'memory': {
            'percent': memory.percent,
            'used': round(memory.used / (1024 * 1024)),
            'total': round(memory.total / (1024 * 1024))
        },
        'disk': {
            'percent': disk.percent,
            'used': round(disk.used / (1024 * 1024 * 1024), 1),
            'total': round(disk.total / (1024 * 1024 * 1024), 1)
        },
        'network': {
            'bytes_recv': round(network.bytes_recv / (1024 * 1024), 2),
            'bytes_sent': round(network.bytes_sent / (1024 * 1024), 2)
        }
    }

def run_flask():
    app.run(host='0.0.0.0', port=5000)

if __name__ == '__main__':
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()
    flask_thread.join()