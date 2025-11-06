"""Modul System Monitor untuk Agent Pribadi (AG)

Mengumpulkan data real-time dari sistem operasi:
- RAM (psutil)
- CPU (psutil)
- GPU (nvidia-smi)
- Temperature (sensors/nvidia-smi)
"""

import psutil
import subprocess
import platform
from typing import Dict, Union
from datetime import datetime, timedelta
from config.settings import MONITOR_CACHE_SECONDS, GPU_ENABLED

# Cache untuk menghindari overhead monitoring yang terlalu sering
_cache = {}
_cache_timestamp = {}


def _is_cache_valid(key: str) -> bool:
    """Cek apakah cache masih valid.
    
    Args:
        key: Key cache yang akan dicek
    
    Returns:
        bool: True jika cache masih valid
    """
    if key not in _cache_timestamp:
        return False
    
    elapsed = (datetime.now() - _cache_timestamp[key]).total_seconds()
    return elapsed < MONITOR_CACHE_SECONDS


def _set_cache(key: str, value: any) -> None:
    """Set nilai cache.
    
    Args:
        key: Key cache
        value: Nilai yang akan di-cache
    """
    _cache[key] = value
    _cache_timestamp[key] = datetime.now()


def get_ram_status() -> Dict[str, Union[float, str]]:
    """Mengambil status RAM sistem saat ini.
    
    Returns:
        dict: {
            'total_gb': float,
            'used_gb': float,
            'available_gb': float,
            'percent': float,
            'status': str
        }
    """
    cache_key = 'ram_status'
    if _is_cache_valid(cache_key):
        return _cache[cache_key]
    
    try:
        mem = psutil.virtual_memory()
        result = {
            'total_gb': round(mem.total / (1024**3), 2),
            'used_gb': round(mem.used / (1024**3), 2),
            'available_gb': round(mem.available / (1024**3), 2),
            'percent': round(mem.percent, 1),
            'status': 'ok'
        }
        _set_cache(cache_key, result)
        return result
    except Exception as e:
        return {
            'total_gb': 0,
            'used_gb': 0,
            'available_gb': 0,
            'percent': 0,
            'status': f'error: {str(e)}'
        }


def get_cpu_status() -> Dict[str, Union[float, int, str]]:
    """Mengambil status CPU sistem saat ini.
    
    Returns:
        dict: {
            'percent': float,
            'cores_physical': int,
            'cores_logical': int,
            'freq_current_mhz': float,
            'status': str
        }
    """
    cache_key = 'cpu_status'
    if _is_cache_valid(cache_key):
        return _cache[cache_key]
    
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_freq = psutil.cpu_freq()
        
        result = {
            'percent': round(cpu_percent, 1),
            'cores_physical': psutil.cpu_count(logical=False),
            'cores_logical': psutil.cpu_count(logical=True),
            'freq_current_mhz': round(cpu_freq.current, 0) if cpu_freq else 0,
            'status': 'ok'
        }
        _set_cache(cache_key, result)
        return result
    except Exception as e:
        return {
            'percent': 0,
            'cores_physical': 0,
            'cores_logical': 0,
            'freq_current_mhz': 0,
            'status': f'error: {str(e)}'
        }


def get_gpu_status() -> Dict[str, Union[float, str]]:
    """Mengambil status GPU menggunakan nvidia-smi.
    
    Returns:
        dict: {
            'name': str,
            'temperature_c': float,
            'utilization_percent': float,
            'memory_used_mb': float,
            'memory_total_mb': float,
            'status': str
        }
    """
    cache_key = 'gpu_status'
    if _is_cache_valid(cache_key):
        return _cache[cache_key]
    
    if not GPU_ENABLED:
        return {
            'name': 'N/A',
            'temperature_c': 0,
            'utilization_percent': 0,
            'memory_used_mb': 0,
            'memory_total_mb': 0,
            'status': 'disabled'
        }
    
    try:
        # Query nvidia-smi untuk data GPU
        cmd = [
            'nvidia-smi',
            '--query-gpu=name,temperature.gpu,utilization.gpu,memory.used,memory.total',
            '--format=csv,noheader,nounits'
        ]
        
        output = subprocess.check_output(
            cmd,
            stderr=subprocess.DEVNULL,
            timeout=5
        ).decode('utf-8').strip()
        
        # Parse output
        parts = [p.strip() for p in output.split(',')]
        
        result = {
            'name': parts[0] if len(parts) > 0 else 'Unknown',
            'temperature_c': float(parts[1]) if len(parts) > 1 else 0,
            'utilization_percent': float(parts[2]) if len(parts) > 2 else 0,
            'memory_used_mb': float(parts[3]) if len(parts) > 3 else 0,
            'memory_total_mb': float(parts[4]) if len(parts) > 4 else 0,
            'status': 'ok'
        }
        _set_cache(cache_key, result)
        return result
        
    except FileNotFoundError:
        return {
            'name': 'N/A',
            'temperature_c': 0,
            'utilization_percent': 0,
            'memory_used_mb': 0,
            'memory_total_mb': 0,
            'status': 'nvidia-smi not found'
        }
    except subprocess.TimeoutExpired:
        return {
            'name': 'N/A',
            'temperature_c': 0,
            'utilization_percent': 0,
            'memory_used_mb': 0,
            'memory_total_mb': 0,
            'status': 'timeout'
        }
    except Exception as e:
        return {
            'name': 'N/A',
            'temperature_c': 0,
            'utilization_percent': 0,
            'memory_used_mb': 0,
            'memory_total_mb': 0,
            'status': f'error: {str(e)}'
        }


def get_system_summary() -> Dict[str, any]:
    """Mengambil ringkasan lengkap status sistem.
    
    Returns:
        dict: {
            'platform': str,
            'ram': dict,
            'cpu': dict,
            'gpu': dict,
            'timestamp': str
        }
    """
    return {
        'platform': platform.system(),
        'ram': get_ram_status(),
        'cpu': get_cpu_status(),
        'gpu': get_gpu_status(),
        'timestamp': datetime.now().isoformat()
    }
