"""Agent Service - Flask Server untuk Agent Pribadi (AG)

Menyediakan API endpoints:
- POST /api/chat - Main chat endpoint
- GET /health - Health check
- GET /api/status - System status summary
- GET /api/history - Command history
- GET / - Web dashboard
"""

from flask import Flask, request, jsonify, render_template
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
    # Serve React-based dashboard when available. Keep legacy dashboard.html as fallback.
    try:
        return render_template('dashboard.react.html')
    except Exception:
        return render_template('dashboard.html')


if __name__ == '__main__':
    logger.info(f"Starting Agent Service on {SERVER_HOST}:{SERVER_PORT}")
    logger.info(f"Debug mode: {DEBUG_MODE}")
    logger.info(f"Project root: {PROJECT_ROOT}")
    
    app.run(
        host=SERVER_HOST,
        port=SERVER_PORT,
        debug=DEBUG_MODE
    )
