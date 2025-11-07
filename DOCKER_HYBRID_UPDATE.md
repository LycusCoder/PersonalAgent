# 🚀 UPDATE AGENT.SH - Docker Hybrid Intelligence

## ✅ Perbaikan yang Sudah Dilakukan

### 📋 Overview
Script `agent.sh` telah diupdate agar **lebih cerdas** dalam mendeteksi dan memilih web server untuk mode Docker Hybrid. Sekarang tidak lagi hardcoded ke "Nginx", melainkan dapat mendeteksi dan memilih antara Nginx atau Apache2.

---

## 🎯 Fitur Baru

### 1. **Smart Web Server Detection**
- ✅ Otomatis scan folder `bin/nginx/` dan `bin/apache/` (atau `bin/apache2/`)
- ✅ Deteksi semua versi web server yang tersedia
- ✅ Menampilkan pilihan yang relevan berdasarkan apa yang ada

### 2. **Interactive Web Server Selection**
Tiga skenario yang ditangani:

#### **Scenario A: Hanya 1 web server tersedia**
```bash
./agent.sh start
# Pilih [Y] untuk Docker
# ✅ Otomatis gunakan web server yang tersedia (tanpa prompt tambahan)
# Contoh: "Mode: Flask + Docker Agent (Nginx)"
```

#### **Scenario B: Kedua web server tersedia (Nginx & Apache)**
```bash
./agent.sh start
# Pilih [Y] untuk Docker
# 
# 📦 Pilih Web Server untuk Docker Hybrid:
#   [1] Nginx
#   [2] Apache2
# 
# Pilih web server [1-2]: _
```

#### **Scenario C: Tidak ada web server di bin/**
```bash
./agent.sh start
# Pilih [Y] untuk Docker
# 
# ❌ Tidak ada web server ditemukan di bin/!
# ℹ️  Jalankan: ./agent.sh setup-docker
# ⚠️  Falling back to native mode (Flask only)...
```

### 3. **Persistent Web Server Choice**
- ✅ Pilihan web server tersimpan di `.agent_webserver.conf`
- ✅ Command `restart` otomatis gunakan web server yang sama
- ✅ Command `stop` otomatis stop container yang benar
- ✅ Command `status` tampilkan web server yang aktif

### 4. **Dynamic Prompt Messages**
Prompt di `./agent.sh start` sekarang dinamis:
- Jika 1 web server: `"Dengan Docker Agent (Nginx Reverse Proxy)"`
- Jika >1 web server: `"Dengan Docker Agent (Pilih Web Server)"`
- Jika 0 web server: `"Dengan Docker Agent (⚠️  Belum setup)"`

---

## 🔧 Fungsi Baru yang Ditambahkan

### `detect_available_webservers()`
```bash
# Scan bin/ untuk nginx dan apache
# Return: "nginx" atau "apache" atau "nginx apache"
available_webservers=$(detect_available_webservers)
```

### `get_webserver_display_name()`
```bash
# Convert internal name ke display name
# "nginx" → "Nginx"
# "apache" → "Apache2"
display_name=$(get_webserver_display_name "nginx")
```

### `select_webserver()`
```bash
# Interactive selection jika multiple web servers
# Auto-select jika hanya 1
# Return error jika 0
selected=$(select_webserver "$available_webservers")
```

---

## 📝 File Configuration

### `.agent_mode.conf`
Menyimpan mode: `docker` atau `native`

### `.agent_webserver.conf` (BARU!)
Menyimpan pilihan web server: `nginx` atau `apache`

---

## 🎯 Command yang Diupdate

### `./agent.sh start`
- ✅ Deteksi web server yang tersedia
- ✅ Tampilkan prompt dinamis
- ✅ Pilih web server (jika >1)
- ✅ Simpan pilihan di `.agent_webserver.conf`
- ✅ Start dengan web server yang dipilih

### `./agent.sh restart`
- ✅ Baca `.agent_webserver.conf`
- ✅ Restart dengan web server yang sama
- ✅ Tampilkan web server di pesan sukses

### `./agent.sh stop`
- ✅ Baca `.agent_webserver.conf`
- ✅ Stop container yang benar (`agent_nginx` atau `agent_apache`)
- ✅ Cleanup semua container `agent_*` (fallback)

### `./agent.sh status`
- ✅ Tampilkan web server yang aktif
- ✅ Check container yang benar

---

## 🧪 Testing Scenarios

### Test 1: Hanya Nginx tersedia
```bash
# Setup
mkdir -p /app/bin/nginx/1.26.0
touch /app/bin/nginx/1.26.0/test

# Test
./agent.sh start
# [Y] → Auto select Nginx (no prompt)
# Expected: "Mode: Flask + Docker Agent (Nginx)"
```

### Test 2: Kedua tersedia
```bash
# Setup
mkdir -p /app/bin/nginx/1.26.0
mkdir -p /app/bin/apache/2.4.52
touch /app/bin/nginx/1.26.0/test
touch /app/bin/apache/2.4.52/test

# Test
./agent.sh start
# [Y] → Prompt pilihan
# Expected: Pilih web server [1-2]
```

### Test 3: Tidak ada web server
```bash
# Setup
rm -rf /app/bin/nginx /app/bin/apache

# Test
./agent.sh start
# [Y] → Fallback ke native
# Expected: Warning + Fallback to native mode
```

---

## 🔄 Integration dengan docker-agent.sh

Script `docker-agent.sh` perlu diupdate untuk:
1. Accept parameter web server: `./docker-agent.sh start nginx` atau `./docker-agent.sh start apache`
2. Build image yang sesuai: `agent_nginx` atau `agent_apache`
3. Start container yang sesuai

**Note:** Ini adalah **task terpisah** yang perlu dilakukan di `docker-agent.sh`.

---

## ✅ Checklist Implementasi

- [x] Fungsi `detect_available_webservers()`
- [x] Fungsi `get_webserver_display_name()`
- [x] Fungsi `select_webserver()`
- [x] Update `cmd_start()` - Dynamic web server selection
- [x] Update `start_docker_agent()` - Accept webserver parameter
- [x] Update `cmd_restart()` - Use saved webserver
- [x] Update `cmd_stop()` - Stop correct container
- [x] Update `cmd_status()` - Show correct webserver
- [x] Update `stop_docker_agent()` - Handle both nginx/apache
- [x] Syntax validation passed
- [ ] Update `docker-agent.sh` (Next task)
- [ ] Test dengan real Nginx installation
- [ ] Test dengan real Apache installation

---

## 📚 Next Steps

### 1. Update `docker-agent.sh`
File `docker-agent.sh` perlu dimodifikasi untuk:
- Accept webserver parameter di semua commands
- Dynamic Dockerfile (pilih Dockerfile.nginx atau Dockerfile.apache)
- Dynamic container names
- Dynamic image names

### 2. Testing
- Test dengan bin/nginx/ terisi
- Test dengan bin/apache/ terisi
- Test dengan keduanya terisi
- Test restart/stop commands

---

## 🎉 Kesimpulan

Script `agent.sh` sekarang **jauh lebih intelligent** dalam menangani Docker Hybrid mode:
- ✅ Tidak lagi hardcoded ke "Nginx"
- ✅ Deteksi otomatis web server yang tersedia
- ✅ Interactive selection jika ada multiple options
- ✅ Persistent choice untuk restart/stop
- ✅ Clear error messages dan fallback

**Status:** ✅ READY TO TEST

**Catatan:** `docker-agent.sh` masih perlu update untuk full support Apache.
