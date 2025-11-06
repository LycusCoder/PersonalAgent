# 🌐 Implementasi Nginx Reverse Proxy - Agent Pribadi

## 📋 Ringkasan

Dokumen ini menjelaskan implementasi nginx reverse proxy untuk menghilangkan kebutuhan port `:7777` saat mengakses Agent Pribadi melalui custom domain `komputerku.nour`.

---

## 🎯 Tujuan

1. **Akses Tanpa Port**: User bisa akses via `http://komputerku.nour` tanpa `:7777`
2. **Virtual Host**: Mendukung multiple domain/subdomain di masa depan
3. **Hybrid Architecture**: Nginx di Docker (port 80) + Flask di Host (port 7777)
4. **Maintainability**: Mudah di-update dan di-monitor

---

## 🏛️ Arsitektur

```
┌─────────────────────────────────────────────────────────────┐
│                         CLIENT                              │
│  (Browser / curl / ag command)                              │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ http://komputerku.nour:80
                     │ http://localhost:80
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              NGINX REVERSE PROXY (Docker)                   │
│                  Container: agent_nginx                     │
│                      Port: 80                               │
│                                                              │
│  • Virtual Host: komputerku.nour                            │
│  • Proxy to: host.docker.internal:7777                      │
│  • Logging: /var/log/nginx/                                 │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ proxy_pass
                     ▼
┌─────────────────────────────────────────────────────────────┐
│          FLASK AGENT SERVICE (Host VENV)                    │
│              File: agent_service.py                         │
│                 Port: 7777                                  │
│                                                              │
│  • Core Logic (Rule-based)                                  │
│  • System Monitoring (psutil, nvidia-smi)                   │
│  • Database (SQLite)                                        │
│  • Direct Hardware Access                                   │
└─────────────────────────────────────────────────────────────┘
```

---

## 📁 File Structure

```
/app/
├── nginx/
│   └── agent.conf              # Nginx reverse proxy config
├── Dockerfile.nginx            # Dockerfile untuk nginx image
├── docker-compose.yml          # Orchestration (nginx + health check)
├── .dockerignore               # Exclude files dari build context
├── docker-agent.sh             # Management script untuk docker
└── logs/
    └── nginx/                  # Nginx logs (mounted dari container)
```

---

## ⚙️ Konfigurasi

### 1. Nginx Configuration (`nginx/agent.conf`)

**Highlights**:
- Upstream: `host.docker.internal:7777` (akses Flask di host)
- Virtual host: `komputerku.nour` dan `localhost`
- Proxy headers: X-Real-IP, X-Forwarded-For, dll
- WebSocket support (untuk future real-time features)
- Health check endpoint: `/health`
- Nginx status: `/nginx_status` (internal only)

### 2. Dockerfile (`Dockerfile.nginx`)

**Base Image**: `nginx:1.25.4-alpine`  
**Alasan**: Alpine-based = kecil (40MB), stable, official image

**Features**:
- Custom config dari `nginx/agent.conf`
- Health check built-in
- Logs di `/var/log/nginx/`

### 3. Docker Compose (`docker-compose.yml`)

**Services**:
1. **nginx**: Main reverse proxy service
   - Port mapping: `80:80`
   - Network: `agent_network` (bridge)
   - Extra hosts: `host.docker.internal` untuk akses Flask di host
   - Logs volume: mounted ke `./logs/nginx`

2. **agent_health_check**: Pre-check service
   - Memastikan Flask service (port 7777) sudah running
   - Nginx hanya start jika health check pass
   - Auto-remove setelah selesai

**Network**: Custom bridge `agent_network`

---

## 🚀 Cara Penggunaan

### Setup Awal (Sekali Saja)

```bash
# 1. Pastikan custom host sudah dikonfigurasi
./agent.sh setup-host

# 2. Build nginx image
./docker-agent.sh build
```

### Menjalankan Sistem

```bash
# 1. Start Flask Agent Service dulu
./agent.sh start

# 2. Start Nginx Reverse Proxy
./docker-agent.sh start

# 3. Cek status
./docker-agent.sh status
```

### Testing

```bash
# Test via localhost
curl http://localhost/health

# Test via virtual host
curl http://komputerku.nour/health

# Test API endpoint
curl -X POST http://komputerku.nour/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"cek ram"}'

# Test dengan ag command (otomatis gunakan localhost:7777)
ag cek cpu

# Test dengan browser
# Buka: http://komputerku.nour
```

### Monitoring

```bash
# Lihat nginx logs
./docker-agent.sh logs

# Lihat Flask logs
./agent.sh logs

# Cek container status
docker ps | grep agent

# Test nginx config
./docker-agent.sh test
```

### Stopping Services

```bash
# Stop nginx
./docker-agent.sh stop

# Stop Flask
./agent.sh stop
```

---

## 🔧 Troubleshooting

### 1. Nginx tidak bisa connect ke Flask

**Gejala**: `502 Bad Gateway`

**Solusi**:
```bash
# Cek apakah Flask running
curl http://localhost:7777/health

# Jika tidak, start Flask dulu
./agent.sh start

# Restart nginx
./docker-agent.sh restart
```

### 2. Virtual host tidak bisa diakses

**Gejala**: `curl: (6) Could not resolve host: komputerku.nour`

**Solusi**:
```bash
# Cek /etc/hosts
grep komputerku.nour /etc/hosts

# Jika tidak ada, jalankan setup
./agent.sh setup-host

# Atau manual:
echo "127.0.0.1  komputerku.nour" | sudo tee -a /etc/hosts
```

### 3. Port 80 sudah digunakan

**Gejala**: `Error starting userland proxy: listen tcp4 0.0.0.0:80: bind: address already in use`

**Solusi**:
```bash
# Cek proses yang pakai port 80
sudo lsof -i :80

# Stop service yang conflict (contoh: Apache)
sudo systemctl stop apache2
# atau
sudo systemctl stop httpd

# Atau ubah port di docker-compose.yml
# ports:
#   - "8080:80"  # Ubah 80 jadi 8080
```

### 4. Nginx config error

**Gejala**: Container langsung exit

**Solusi**:
```bash
# Test config
./docker-agent.sh test

# Lihat logs
./docker-agent.sh logs

# Jika ada syntax error, edit nginx/agent.conf
# Lalu rebuild
./docker-agent.sh build
./docker-agent.sh start
```

---

## 📊 Monitoring & Logs

### Nginx Logs

```bash
# Access logs
tail -f logs/nginx/agent_access.log

# Error logs
tail -f logs/nginx/agent_error.log

# Via Docker
docker logs -f agent_nginx
```

### Flask Logs

```bash
tail -f logs/agent.log
```

### Nginx Status

```bash
# Internal status endpoint (dari dalam container)
curl http://localhost/nginx_status
```

---

## 🔒 Security Considerations

1. **Port Exposure**:
   - Nginx hanya expose port 80 (HTTP)
   - Flask port 7777 tetap internal (tidak exposed)
   - Untuk production, tambahkan HTTPS (port 443)

2. **Headers**:
   - X-Real-IP dan X-Forwarded-For di-forward ke Flask
   - Bisa digunakan untuk rate limiting / IP blocking

3. **File Permissions**:
   - Nginx logs di-mount dengan permission yang tepat
   - Sensitive files (.env, db) tidak termasuk dalam Docker context (`.dockerignore`)

---

## 🚀 Production Ready Checklist

- [x] Nginx reverse proxy configured
- [x] Health checks implemented
- [x] Logging configured
- [x] Docker orchestration (compose)
- [ ] HTTPS/SSL certificate (Let's Encrypt)
- [ ] Rate limiting (nginx limit_req)
- [ ] Firewall rules (ufw/iptables)
- [ ] Auto-restart on failure (systemd)
- [ ] Backup strategy (logs, database)
- [ ] Monitoring/alerting (Prometheus/Grafana)

---

## 📚 Referensi

- **Nginx Docs**: https://nginx.org/en/docs/
- **Docker Compose**: https://docs.docker.com/compose/
- **Flask Behind Proxy**: https://flask.palletsprojects.com/en/latest/deploying/proxy_fix/

---

**Status**: ✅ Implemented  
**Tanggal**: 2025-08-XX  
**Maintainer**: Agent Pribadi Team