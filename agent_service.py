"""Agent Service - Flask Server untuk Agent Pribadi (AG)

Menyediakan API endpoints:
- POST /api/chat - Main chat endpoint
- GET /health - Health check
- GET /api/status - System status summary
- GET /api/history - Command history
- GET / - Web dashboard
"""

from flask import Flask, request, jsonify, render_template_string
from datetime import datetime
import logging
from pathlib import Path

# Import konfigurasi
from config.settings import (
    SERVER_HOST,
    SERVER_PORT,
    DEBUG_MODE,
    LOG_FILE,
    LOG_LEVEL,
    API_PREFIX,
    PROJECT_ROOT
)

# Import core modules
from core.chat_rules import process_command
from core.system_monitor import get_system_summary
from storage.db import get_db

# Setup logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Inisialisasi Flask app
app = Flask(__name__)
db = get_db()


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'Agent Pribadi (AG)',
        'timestamp': datetime.now().isoformat()
    })


@app.route(f'{API_PREFIX}/chat', methods=['POST'])
def chat():
    """Main chat endpoint untuk memproses command.
    
    Request Body:
        {
            "message": "user command"
        }
    
    Response:
        {
            "success": bool,
            "message": str,
            "data": dict (optional),
            "command_type": str,
            "timestamp": str
        }
    """
    try:
        # Parse request
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({
                'success': False,
                'message': 'Invalid request. Field "message" required.',
                'timestamp': datetime.now().isoformat()
            }), 400
        
        user_message = data['message']
        logger.info(f"Processing command: {user_message}")
        
        # Process command dengan chat_rules
        result = process_command(user_message)
        
        # Tambahkan timestamp
        result['timestamp'] = datetime.now().isoformat()
        
        # Save ke database
        db.add_command_history(
            command=user_message,
            command_type=result.get('command_type', 'unknown'),
            success=result.get('success', False),
            response_preview=result.get('message', ''),
            data=result.get('data', None)
        )
        
        logger.info(f"Command processed: {result['command_type']}, success: {result['success']}")
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error processing chat: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'message': f'Internal server error: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500


@app.route(f'{API_PREFIX}/status', methods=['GET'])
def status():
    """System status summary endpoint."""
    try:
        summary = get_system_summary()
        return jsonify({
            'success': True,
            'data': summary,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error getting status: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500


@app.route(f'{API_PREFIX}/history', methods=['GET'])
def history():
    """Command history endpoint."""
    try:
        limit = request.args.get('limit', 20, type=int)
        history_data = db.get_command_history(limit=limit)
        stats = db.get_command_statistics()
        
        return jsonify({
            'success': True,
            'data': {
                'history': history_data,
                'statistics': stats
            },
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error getting history: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500


@app.route('/', methods=['GET'])
def dashboard():
    """Web dashboard sederhana."""
    html_template = '''
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Agent Pribadi (AG) - Dashboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        .header {
            text-align: center;
            color: white;
            margin-bottom: 30px;
        }
        .header h1 {
            font-size: 2.5rem;
            margin-bottom: 10px;
        }
        .header p {
            font-size: 1.1rem;
            opacity: 0.9;
        }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        .card {
            background: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .card h2 {
            color: #667eea;
            margin-bottom: 15px;
            font-size: 1.3rem;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }
        .stat {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px 0;
            border-bottom: 1px solid #eee;
        }
        .stat:last-child {
            border-bottom: none;
        }
        .stat-label {
            color: #666;
            font-weight: 500;
        }
        .stat-value {
            color: #333;
            font-weight: bold;
            font-size: 1.1rem;
        }
        .status-ok {
            color: #10b981;
        }
        .status-warning {
            color: #f59e0b;
        }
        .status-error {
            color: #ef4444;
        }
        .footer {
            text-align: center;
            color: white;
            margin-top: 30px;
            opacity: 0.8;
        }
        .refresh-info {
            text-align: center;
            color: white;
            margin-top: 10px;
            font-size: 0.9rem;
        }
        .loading {
            text-align: center;
            color: white;
            font-size: 1.2rem;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 Agent Pribadi (AG)</h1>
            <p>Dashboard Monitoring Sistem - Sekretaris Sarah</p>
        </div>
        
        <div id="content" class="loading">Memuat data sistem...</div>
        
        <div class="refresh-info">Auto-refresh setiap 5 detik</div>
        
        <div class="footer">
            <p>&copy; 2025 Agent Pribadi - Rule-Based System</p>
        </div>
    </div>

    <script>
        function formatBytes(mb) {
            if (mb >= 1024) {
                return (mb / 1024).toFixed(2) + ' GB';
            }
            return mb.toFixed(2) + ' MB';
        }

        function getStatusClass(percent) {
            if (percent < 60) return 'status-ok';
            if (percent < 85) return 'status-warning';
            return 'status-error';
        }

        async function loadData() {
            try {
                const response = await fetch('/api/status');
                const result = await response.json();
                
                if (!result.success) {
                    throw new Error('Failed to fetch data');
                }
                
                const data = result.data;
                const ram = data.ram;
                const cpu = data.cpu;
                const gpu = data.gpu;
                
                const html = `
                    <div class="grid">
                        <div class="card">
                            <h2>💾 RAM</h2>
                            <div class="stat">
                                <span class="stat-label">Total</span>
                                <span class="stat-value">${ram.total_gb} GB</span>
                            </div>
                            <div class="stat">
                                <span class="stat-label">Digunakan</span>
                                <span class="stat-value">${ram.used_gb} GB</span>
                            </div>
                            <div class="stat">
                                <span class="stat-label">Tersedia</span>
                                <span class="stat-value">${ram.available_gb} GB</span>
                            </div>
                            <div class="stat">
                                <span class="stat-label">Penggunaan</span>
                                <span class="stat-value ${getStatusClass(ram.percent)}">${ram.percent}%</span>
                            </div>
                        </div>
                        
                        <div class="card">
                            <h2>⚙️ CPU</h2>
                            <div class="stat">
                                <span class="stat-label">Penggunaan</span>
                                <span class="stat-value ${getStatusClass(cpu.percent)}">${cpu.percent}%</span>
                            </div>
                            <div class="stat">
                                <span class="stat-label">Core Fisik</span>
                                <span class="stat-value">${cpu.cores_physical}</span>
                            </div>
                            <div class="stat">
                                <span class="stat-label">Core Logical</span>
                                <span class="stat-value">${cpu.cores_logical}</span>
                            </div>
                            <div class="stat">
                                <span class="stat-label">Frekuensi</span>
                                <span class="stat-value">${cpu.freq_current_mhz} MHz</span>
                            </div>
                        </div>
                        
                        <div class="card">
                            <h2>🎮 GPU</h2>
                            <div class="stat">
                                <span class="stat-label">Nama</span>
                                <span class="stat-value" style="font-size: 0.9rem;">${gpu.name}</span>
                            </div>
                            <div class="stat">
                                <span class="stat-label">Suhu</span>
                                <span class="stat-value ${getStatusClass(gpu.temperature_c)}">${gpu.temperature_c}°C</span>
                            </div>
                            <div class="stat">
                                <span class="stat-label">Penggunaan</span>
                                <span class="stat-value ${getStatusClass(gpu.utilization_percent)}">${gpu.utilization_percent}%</span>
                            </div>
                            <div class="stat">
                                <span class="stat-label">Memory</span>
                                <span class="stat-value">${formatBytes(gpu.memory_used_mb)} / ${formatBytes(gpu.memory_total_mb)}</span>
                            </div>
                        </div>
                    </div>
                `;
                
                document.getElementById('content').innerHTML = html;
            } catch (error) {
                console.error('Error loading data:', error);
                document.getElementById('content').innerHTML = '<div class="card" style="text-align: center; color: #ef4444;">Gagal memuat data sistem</div>';
            }
        }

        // Load data pertama kali
        loadData();
        
        // Auto-refresh setiap 5 detik
        setInterval(loadData, 5000);
    </script>
</body>
</html>
    '''
    return render_template_string(html_template)


if __name__ == '__main__':
    logger.info(f"Starting Agent Service on {SERVER_HOST}:{SERVER_PORT}")
    logger.info(f"Debug mode: {DEBUG_MODE}")
    logger.info(f"Project root: {PROJECT_ROOT}")
    
    app.run(
        host=SERVER_HOST,
        port=SERVER_PORT,
        debug=DEBUG_MODE
    )
