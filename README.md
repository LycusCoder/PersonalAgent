# 🤖 Agent Pribadi (AG) - Personal Assistant

**Sekretaris Sarah** - Agent pribadi berbasis rule-based yang stabil, akurat, dan universal (cross-platform).

## 🎯 Fitur Utama

- ✅ **100% Rule-Based** - Tidak menggunakan LLM, menjamin stabilitas dan konsistensi
- 📊 **Real-time System Monitoring** - RAM, CPU, GPU (RTX 4060), Temperature
- 💬 **Multi-Interface** - CLI, Web Dashboard, REST API
- 🎭 **Persona Konsisten** - Sekretaris Sarah yang formal dan profesional
- 🗄️ **Command History** - SQLite database untuk tracking
- 🌍 **Cross-Platform** - Linux, Windows, macOS, VPS

## 🏗️ Arsitektur

```
/app/
├── agent_service.py       # Flask server (port 7777)
├── config/
│   └── settings.py        # Konfigurasi (PROJECT_ROOT, ports, dll)
├── core/
│   ├── persona.py         # Persona Sarah (greeting, formatting)
│   ├── system_monitor.py  # Monitoring sistem (psutil, nvidia-smi)
│   └── chat_rules.py      # Rule-based command processor
├── storage/
│   └── db.py              # SQLite database manager
├── cli/
│   └── ag_launcher.sh     # CLI launcher dengan TTS support
├── docs/
│   ├── plan/
│   │   └── plan_awal.md   # Rencana awal project
│   └── rules/
│       └── golden_rules.md # Aturan development
└── logs/                   # Log files
```

## 📦 Instalasi

### 1. Install Dependencies

```bash
# Python dependencies
pip install -r requirements.txt

# TTS (Optional - untuk CLI dengan voice)
sudo apt install espeak  # Linux
# macOS sudah built-in 'say'
# Windows sudah built-in PowerShell Speech
```

### 2. Jalankan Server

```bash
python agent_service.py
```

Server akan berjalan di `http://localhost:7777`

### 3. Setup CLI Command (Optional)

Untuk menggunakan command `ag` di terminal:

```bash
# Tambahkan alias ke .bashrc atau .zshrc
echo 'alias ag="bash /path/to/app/cli/ag_launcher.sh"' >> ~/.bashrc
source ~/.bashrc
```

Ganti `/path/to/app` dengan path absolut ke project.

## 🚀 Cara Penggunaan

### 1. Web Dashboard

Buka browser dan akses:
```
http://localhost:7777
```

Dashboard akan menampilkan:
- Status RAM real-time
- Status CPU real-time
- Status GPU real-time
- Auto-refresh setiap 5 detik

### 2. CLI Command

```bash
# Tanpa TTS
ag cek ram
ag cek cpu
ag cek gpu
ag cek sistem
ag jam berapa
ag bantuan

# Dengan TTS (voice)
ag -v cek ram
ag -v cek sistem
```

### 3. REST API

#### POST `/api/chat` - Main Chat Endpoint

```bash
curl -X POST http://localhost:7777/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "cek ram"}'
```

Response:
```json
{
  "success": true,
  "message": "Selamat pagi, Tuan Affif. Status RAM saat ini:\n• Total: 32.0 GB\n• Digunakan: 12.5 GB\n• Tersedia: 19.5 GB\n• Penggunaan: 39.1%",
  "data": {
    "total_gb": 32.0,
    "used_gb": 12.5,
    "available_gb": 19.5,
    "percent": 39.1,
    "status": "ok"
  },
  "command_type": "ram_status",
  "timestamp": "2025-08-XX..."
}
```

#### GET `/api/status` - System Summary

```bash
curl http://localhost:7777/api/status
```

#### GET `/api/history` - Command History

```bash
curl http://localhost:7777/api/history?limit=10
```

#### GET `/health` - Health Check

```bash
curl http://localhost:7777/health
```

## 📝 Perintah yang Tersedia

| Perintah | Deskripsi | Contoh |
|----------|-----------|--------|
| `cek ram` / `status ram` | Melihat status RAM | `ag cek ram` |
| `cek cpu` / `status cpu` | Melihat status CPU | `ag cek cpu` |
| `cek gpu` / `status gpu` | Melihat status GPU | `ag cek gpu` |
| `cek sistem` / `ringkasan` | Ringkasan lengkap | `ag cek sistem` |
| `jam berapa` / `waktu` | Waktu saat ini | `ag jam berapa` |
| `bantuan` / `help` | Daftar perintah | `ag bantuan` |
| `halo` / `hai` | Sapaan | `ag halo` |

## ⚙️ Konfigurasi

Edit `config/settings.py` untuk mengubah:

```python
# Server
SERVER_PORT = 7777
SERVER_HOST = '0.0.0.0'

# Monitoring
MONITOR_CACHE_SECONDS = 2
GPU_ENABLED = True  # Set False jika tidak ada GPU

# Persona
MASTER_NAME = "Tuan Affif"
PERSONA_NAME = "Sarah"

# Database
MAX_COMMAND_HISTORY = 100
```

Atau gunakan environment variables:
```bash
export AG_PORT=8888
export AG_HOST=0.0.0.0
export AG_DEBUG=True
```

## 📊 Database

Database SQLite disimpan di `storage/agent.db` dengan tabel:

- `command_history` - History semua command
- `reminders` - Reminders (future feature)

Max history: 100 entries (configurable)

## 🔧 Development

### Golden Rules

Baca `docs/rules/golden_rules.md` untuk aturan development yang WAJIB diikuti:

- ❌ JANGAN hardcode path absolut (gunakan PROJECT_ROOT)
- ❌ JANGAN gunakan LLM untuk core logic
- ❌ JANGAN lupakan error handling
- ✅ WAJIB cross-platform compatibility
- ✅ WAJIB logging untuk debugging
- ✅ WAJIB type hints dan docstrings

### Testing

```bash
# Test server health
curl http://localhost:7777/health

# Test chat endpoint
curl -X POST http://localhost:7777/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "cek sistem"}'

# Test CLI
bash cli/ag_launcher.sh "cek ram"
```

## 🐛 Troubleshooting

### Server tidak bisa start

1. Cek apakah port 7777 sudah digunakan:
   ```bash
   lsof -i :7777
   ```

2. Cek logs:
   ```bash
   tail -f logs/agent.log
   ```

### GPU monitoring tidak bekerja

1. Pastikan nvidia-smi terinstall:
   ```bash
   nvidia-smi
   ```

2. Jika tidak ada GPU, set `GPU_ENABLED = False` di `config/settings.py`

### CLI tidak bisa connect

1. Pastikan server berjalan:
   ```bash
   curl http://localhost:7777/health
   ```

2. Cek URL di `cli/ag_launcher.sh` (default: `http://localhost:7777/api/chat`)

## 📚 Dokumentasi

- [Plan Awal](docs/plan/plan_awal.md) - Rencana dan arsitektur project
- [Golden Rules](docs/rules/golden_rules.md) - Aturan development

## 🙏 Credits

**Maintainer**: Tuan Affif  
**Agent Persona**: Sekretaris Sarah  
**Architecture**: Rule-Based (No LLM)  

---

> *"Stabilitas dan akurasi adalah prioritas utama."*
