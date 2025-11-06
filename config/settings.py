"""Configuration settings untuk Agent Pribadi (AG)"""
import os
from pathlib import Path

# PROJECT_ROOT - Universal path yang cross-platform
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Server Configuration
SERVER_HOST = os.getenv('AG_HOST', '0.0.0.0')  # 0.0.0.0 agar bisa diakses dari luar (VPS)
SERVER_PORT = int(os.getenv('AG_PORT', 7777))
DEBUG_MODE = os.getenv('AG_DEBUG', 'False').lower() == 'true'

# Database Configuration
DB_PATH = PROJECT_ROOT / 'storage' / 'agent.db'

# Logging Configuration
LOG_DIR = PROJECT_ROOT / 'logs'
LOG_FILE = LOG_DIR / 'agent.log'
LOG_LEVEL = os.getenv('AG_LOG_LEVEL', 'INFO')

# Persona Configuration
PERSONA_NAME = "Sarah"
PERSONA_ROLE = "Sekretaris Pribadi"
MASTER_NAME = "Tuan Affif"

# System Monitoring Configuration
MONITOR_CACHE_SECONDS = 2  # Cache data monitoring selama 2 detik
GPU_ENABLED = True  # Set False jika tidak ada GPU

# TTS Configuration
TTS_DEFAULT_ENABLED = False  # Default TTS off, bisa diaktifkan via -v flag

# API Configuration
API_PREFIX = '/api'
MAX_COMMAND_HISTORY = 100  # Maksimal history yang disimpan

# Create necessary directories
LOG_DIR.mkdir(parents=True, exist_ok=True)
(PROJECT_ROOT / 'storage').mkdir(parents=True, exist_ok=True)
