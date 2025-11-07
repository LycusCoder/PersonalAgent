# 🐳 Docker Hybrid Setup Guide

Panduan lengkap untuk menggunakan fitur Docker Hybrid di Agent Pribadi (AG).

---

## 📋 Apa itu Docker Hybrid?

Docker Hybrid adalah fitur yang memungkinkan Anda menjalankan Agent Service dengan:
- **Web Server** (Nginx/Apache2) sebagai reverse proxy
- **Database** (MySQL/PostgreSQL/MongoDB) untuk storage
- **Flask Service** sebagai backend API

Semua komponen dijalankan dalam Docker container untuk isolasi dan portabilitas yang lebih baik.

---

## 🚀 Quick Start

### 1. Verifikasi Docker

```bash
./agent.sh verify-docker
```

Command ini akan mengecek:
- ✅ Docker installation & version
- ✅ Docker Compose availability
- ✅ Nginx/Apache2 di `/bin/{app}/{version}/`
- ✅ Database di `/bin/{db}/{version}/`
- ✅ Docker images status

### 2. Setup Docker Hybrid

```bash
./agent.sh setup-docker
```

Interactive setup yang akan:
1. Menanyakan pilihan **Web Server** (Nginx recommended / Apache2)
2. Menanyakan pilihan **Database** (MySQL / PostgreSQL / MongoDB / Skip)
3. Download dari `config/tools/packages.yaml`
4. Validasi file existing (skip jika valid)
5. Extract ke `bin/{app}/{version}/`
6. Generate `Dockerfile.hybrid`
7. Build Docker image

### 3. Start dengan Docker

```bash
./agent.sh start
```

Pilih **[Y]** saat ditanya "Gunakan Docker Agent?"

---

## 📂 Struktur File

Setelah setup, struktur akan seperti ini:

```
/app/
├── bin/
│   ├── nginx/
│   │   └── 1.26.0/          # Nginx binary & config
│   ├── mysql/
│   │   └── 8.4.6/           # MySQL binary & data
│   └── ...
├── Dockerfile.hybrid         # Auto-generated Dockerfile
├── docker-agent.sh           # Docker management script
└── agent.sh                  # Main CLI manager
```

---

## 🎯 Available Commands

### Verification Commands

```bash
# Verify system dependencies (Python, pip, packages, etc.)
./agent.sh verify

# Verify Docker & hybrid setup
./agent.sh verify-docker
```

### Setup Commands

```bash
# Setup system (install deps, register ag command)
./agent.sh setup

# Setup Docker hybrid (Nginx/Apache + MySQL/PostgreSQL/MongoDB)
./agent.sh setup-docker

# Setup custom host (komputerku.nour)
./agent.sh setup-host
```

### Service Management

```bash
# Start service (interactive mode)
./agent.sh start
# Pilih:
#   [Y] Dengan Docker Agent (Flask + Nginx)
#   [N] Native saja (Flask only)

# Stop all services (Flask + Docker if running)
./agent.sh stop

# Restart with last used mode
./agent.sh restart

# Check service status & mode
./agent.sh status

# View service logs
./agent.sh logs
```

---

## 🔧 How It Works

### 1. Download & Validation

Script `cli/docker_setup_hybrid.sh` akan:
- Parse `config/tools/packages.yaml` untuk mendapatkan URL download
- Download file ke `/tmp/agent_docker_setup/`
- Validasi integrity file (cek corrupt atau tidak)
- Extract ke `bin/{app}/{version}/`

**Smart Skip:**
- Jika file sudah ada di `bin/`, akan divalidasi dulu
- Skip download & extract jika file valid
- Re-download jika file corrupt

### 2. Dockerfile Generation

Auto-generate `Dockerfile.hybrid` berdasarkan pilihan:

```dockerfile
FROM ubuntu:22.04

# Install dependencies
RUN apt-get update && apt-get install -y ...

# Copy binaries from host
COPY bin/nginx/1.26.0 /opt/nginx
COPY bin/mysql/8.4.6 /opt/mysql

# Setup & compile (if source)
RUN if [ -f "configure" ]; then ./configure && make && make install; fi

EXPOSE 80 443

# Start service
CMD ["/opt/nginx/sbin/nginx", "-g", "daemon off;"]
```

### 3. Docker Image Build

```bash
docker build -f Dockerfile.hybrid -t agent_nginx_hybrid:latest .
```

### 4. Runtime

Saat `./agent.sh start` dengan mode Docker:
1. Start Flask service (port 7777)
2. Start Docker container (Nginx reverse proxy)
3. Nginx forward requests ke Flask

**URL Akses:**
- `http://localhost:7777` → Direct ke Flask
- `http://komputerku.nour` → Melalui Nginx

---

## 📦 Supported Packages

Dari `config/tools/packages.yaml`:

### Web Servers
- **Nginx**: 1.26.0, 1.25.4, 1.24.0
- **Apache**: 2.4.65, 2.4.57

### Databases
- **MySQL**: 9.4.0, 8.4.6, 8.0.40
- **PostgreSQL**: 18.0, 17.2, 16.6
- **MongoDB**: 8.0.4, 7.0.14

### Other Tools
- **PHP**: 8.4, 8.3, 8.2, 8.1
- **Node.js**: 24.9.0, 23.11.0, 22.14.0, 20.18.0
- **Go**: 1.24.1, 1.23.4
- **Pocketbase**: 0.25.9

---

## 🐛 Troubleshooting

### Docker not installed?

```bash
# Install Docker
curl -fsSL https://get.docker.com | sh

# Start Docker daemon
sudo systemctl start docker

# Enable Docker on boot
sudo systemctl enable docker
```

### Docker daemon not running?

```bash
sudo systemctl start docker
```

### Downloaded file corrupt?

Script akan auto-detect dan re-download jika file corrupt.

Jika masih error, hapus cache manual:

```bash
rm -rf /tmp/agent_docker_setup/
```

### Port 7777 already in use?

```bash
# Stop service first
./agent.sh stop

# Check port usage
sudo lsof -ti:7777

# Kill process if needed
sudo lsof -ti:7777 | xargs kill -9
```

---

## 🎓 Advanced Usage

### Custom Nginx Config

Edit file `nginx/agent.conf` sebelum build:

```nginx
server {
    listen 80;
    server_name komputerku.nour;
    
    location / {
        proxy_pass http://host.docker.internal:7777;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Manual Docker Build

```bash
# Build custom image
docker build -f Dockerfile.hybrid -t my_custom_agent:v1 .

# Run container
docker run -d --name my_agent \
    -p 80:80 \
    --add-host=host.docker.internal:host-gateway \
    my_custom_agent:v1
```

### Multi-Version Setup

Install multiple versions:

```bash
# Setup Nginx 1.26.0
./agent.sh setup-docker
# Pilih Nginx → version 1.26.0

# Setup Nginx 1.25.4 (manual)
cd /app
bash cli/docker_setup_hybrid.sh
# Pilih Nginx → version 1.25.4
```

---

## 📚 References

- **Main Script**: `agent.sh`
- **Hybrid Setup**: `cli/docker_setup_hybrid.sh`
- **Package Config**: `config/tools/packages.yaml`
- **Docker Script**: `docker-agent.sh`
- **Golden Rules**: `docs/rules/golden_rules.md`

---

## 💡 Tips

1. **Gunakan Nginx** untuk production (lebih ringan & cepat)
2. **Gunakan Apache** jika butuh kompatibilitas .htaccess
3. **Skip database** jika hanya butuh web server
4. **Validation otomatis** akan skip download jika file sudah valid
5. **Mode tersimpan** otomatis, tidak perlu input ulang saat restart

---

**Last Updated**: 2025-08-XX  
**Maintainer**: Agent Pribadi Team  
**Version**: 1.0.0
