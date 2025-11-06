# 🏆 Golden Rules - Agent Pribadi (AG)

Dokumen ini berisi **aturan emas** yang WAJIB diikuti oleh semua developer (termasuk AI Agent) yang berkontribusi pada proyek Agent Pribadi ini. Pelanggaran terhadap aturan ini dapat menyebabkan instabilitas sistem atau ketidakcocokan lintas platform.

---

## 🎯 Misi Utama Proyek

**"Menciptakan Personal Agent yang 100% Rule-Based, Stabil, Akurat, dan Universal (Cross-Platform)"**

### Core Values:
1. **Stabilitas > Fleksibilitas** - Rule-based lebih diprioritaskan daripada AI/LLM
2. **Akurasi > Kecepatan** - Data yang benar lebih penting dari response time
3. **Portabilitas > Convenience** - Harus jalan di Windows, Linux, VPS, lokal
4. **Konsistensi > Kreativitas** - Persona dan format response harus predictable

---

## ❌ LARANGAN MUTLAK (DO NOT)

### 🚫 1. JANGAN Hardcode Path Absolut
**SALAH ❌:**
```python
# Ini akan gagal di sistem lain!
LOG_PATH = "/app/logs/agent.log"
CONFIG_PATH = "/home/affif/config.json"
DATA_DIR = "C:\\Users\\Affif\\data"
```

**BENAR ✅:**
```python
import os
from pathlib import Path

# Gunakan project_root yang dinamis
PROJECT_ROOT = Path(__file__).parent.parent  # Relatif terhadap file
LOG_PATH = PROJECT_ROOT / "logs" / "agent.log"
CONFIG_PATH = PROJECT_ROOT / "config" / "settings.json"
DATA_DIR = PROJECT_ROOT / "data"
```

**Alasan:** Hardcoded path seperti `/app/` atau `C:\Users\` hanya jalan di sistem tertentu. Ketika dipindah ke VPS, Windows, atau folder lain, aplikasi akan crash.

---

### 🚫 2. JANGAN Gunakan LLM untuk Core Logic
**SALAH ❌:**
```python
# Ini melanggar prinsip rule-based
response = openai.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": user_input}]
)
```

**BENAR ✅:**
```python
# Gunakan if-elif-else atau dictionary mapping
def process_command(user_input):
    user_input = user_input.lower().strip()
    
    if "cek ram" in user_input or "status ram" in user_input:
        return get_ram_status()
    elif "cek cpu" in user_input:
        return get_cpu_status()
    elif "cek gpu" in user_input:
        return get_gpu_status()
    else:
        return "Maaf Tuan, perintah tidak dikenali."
```

**Alasan:** LLM tidak deterministik (output berbeda untuk input sama), mahal, dan memerlukan internet. Rule-based menjamin stabilitas 100%.

---

### 🚫 3. JANGAN Lupakan Error Handling
**SALAH ❌:**
```python
def get_gpu_temp():
    # Langsung assume nvidia-smi ada
    output = subprocess.check_output(['nvidia-smi', '--query-gpu=temperature.gpu', '--format=csv,noheader,nounits'])
    return int(output.decode().strip())
```

**BENAR ✅:**
```python
def get_gpu_temp():
    try:
        output = subprocess.check_output(
            ['nvidia-smi', '--query-gpu=temperature.gpu', '--format=csv,noheader,nounits'],
            stderr=subprocess.DEVNULL,
            timeout=5
        )
        return int(output.decode().strip())
    except FileNotFoundError:
        return "GPU driver tidak terdeteksi"
    except subprocess.TimeoutExpired:
        return "Timeout saat mengecek GPU"
    except Exception as e:
        return f"Error: {str(e)}"
```

**Alasan:** nvidia-smi tidak selalu tersedia (Windows tanpa GPU, VM cloud, dll). Crash tanpa error handling akan membuat seluruh agent down.

---

### 🚫 4. JANGAN Hardcode Port atau Host
**SALAH ❌:**
```python
app.run(host='127.0.0.1', port=5000)
```

**BENAR ✅:**
```python
from config.settings import SERVER_HOST, SERVER_PORT

app.run(host=SERVER_HOST, port=SERVER_PORT)
```

**Alasan:** Port bisa conflict dengan aplikasi lain. Host `127.0.0.1` tidak bisa diakses dari luar (VPS). Harus configurable.

---

### 🚫 5. JANGAN Abaikan Cross-Platform Compatibility
**SALAH ❌:**
```bash
# Shell script yang hanya jalan di Linux
#!/bin/bash
espeak "$1"  # espeak tidak ada di Windows/macOS
```

**BENAR ✅:**
```python
import platform
import subprocess

def speak(text):
    system = platform.system()
    try:
        if system == "Linux":
            subprocess.run(['espeak', text], check=False)
        elif system == "Windows":
            subprocess.run(['powershell', '-Command', f'Add-Type -AssemblyName System.Speech; (New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak("{text}")'], check=False)
        elif system == "Darwin":  # macOS
            subprocess.run(['say', text], check=False)
    except Exception:
        pass  # Silent fail jika TTS tidak tersedia
```

**Alasan:** espeak (Linux only), say (macOS only), Windows Speech API berbeda. Harus detect OS dan fallback gracefully.

---

### 🚫 6. JANGAN Simpan Credentials di Code
**SALAH ❌:**
```python
API_KEY = "sk-1234567890abcdef"  # Hardcoded di code
DB_PASSWORD = "password123"
```

**BENAR ✅:**
```python
import os

API_KEY = os.getenv('AG_API_KEY', None)
DB_PASSWORD = os.getenv('AG_DB_PASSWORD', 'default_dev_password')
```

**Alasan:** Credentials di code akan ter-commit ke git (security risk). Gunakan environment variables atau config file yang di-ignore git.

---

### 🚫 7. JANGAN Modifikasi Persona Tanpa Dokumentasi
**SALAH ❌:**
```python
# Tiba-tiba ubah format tanpa update docs
return "Yo bro! RAM lu udah 80% nih"  # Melanggar persona formal
```

**BENAR ✅:**
```python
# Konsisten dengan persona Sekretaris Sarah
return f"{get_greeting()}, Tuan Affif. Penggunaan RAM saat ini mencapai 80%. Sebaiknya menutup beberapa aplikasi."
```

**Alasan:** Persona adalah identitas agent. Perubahan harus disengaja dan terdokumentasi di `persona.py`.

---

## ✅ WAJIB DILAKUKAN (MUST DO)

### 1. ✅ Selalu Gunakan `PROJECT_ROOT` untuk Path
```python
# Di setiap file Python, define PROJECT_ROOT
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parent.parent  # Adjust sesuai depth

# Atau import dari settings
from config.settings import PROJECT_ROOT
```

### 2. ✅ Logging untuk Setiap Action Penting
```python
import logging

logger = logging.getLogger(__name__)

def process_command(cmd):
    logger.info(f"Processing command: {cmd}")
    result = execute_command(cmd)
    logger.info(f"Command result: {result}")
    return result
```

### 3. ✅ Type Hints dan Docstrings
```python
def get_ram_status() -> dict:
    """
    Mengambil status RAM sistem saat ini.
    
    Returns:
        dict: {
            'total': int (GB),
            'used': int (GB),
            'available': int (GB),
            'percent': float
        }
    """
    pass
```

### 4. ✅ Consistent Response Format
```python
# Semua API response harus JSON dengan struktur:
{
    "success": True/False,
    "data": {...},
    "message": "Human-readable message",
    "timestamp": "2025-08-XX HH:MM:SS"
}
```

### 5. ✅ Test di Multiple OS (Jika Memungkinkan)
- Linux (Zorin OS / Ubuntu)
- Windows 10/11
- macOS (Opsional)
- VPS Cloud (Ubuntu Server)

---

## 📐 Standar Penamaan

### Files:
- Python modules: `snake_case.py` (contoh: `system_monitor.py`)
- Config files: `snake_case.json` / `.yaml` (contoh: `settings.json`)
- Shell scripts: `kebab-case.sh` (contoh: `ag-launcher.sh`)

### Variables:
- Constants: `UPPER_SNAKE_CASE` (contoh: `PROJECT_ROOT`, `MAX_RETRIES`)
- Functions: `snake_case()` (contoh: `get_ram_status()`)
- Classes: `PascalCase` (contoh: `SystemMonitor`, `PersonaManager`)

### API Endpoints:
- RESTful: `/api/resource` (contoh: `/api/status`, `/api/chat`)
- Actions: `/api/resource/action` (contoh: `/api/process/kill`)

---

## 🧪 Testing Requirements

### Before Commit, Test:
1. ✅ Import semua module berhasil (`python -c "import core.system_monitor"`)
2. ✅ Server bisa start tanpa error (`python agent_service.py`)
3. ✅ CLI command minimal 1 berjalan (`bash cli/ag_launcher.sh "cek ram"`)
4. ✅ No hardcoded paths (grep untuk `/app/`, `C:\\`, `/home/`)

---

## 🔄 Update Rules

Jika ada rule baru yang perlu ditambahkan:

1. Diskusikan dengan Tuan Affif terlebih dahulu
2. Update dokumen ini dengan alasan yang jelas
3. Review kode existing untuk compliance
4. Update dokumentasi terkait

---

## 📚 Referensi Penting

- **Plan Awal**: `/docs/plan/plan_awal.md`
- **Architecture**: Lihat section 2 di Plan Awal
- **Persona Guidelines**: `/core/persona.py` (docstring)
- **API Docs**: (Will be generated)

---

**Terakhir Diupdate**: 2025-08-XX  
**Maintainer**: Tuan Affif  
**Enforced by**: All Contributors (Human & AI)

---

> *"Kode yang baik adalah kode yang bisa dipahami dan dijalankan oleh orang lain di sistem yang berbeda, 6 bulan setelah ditulis."*
