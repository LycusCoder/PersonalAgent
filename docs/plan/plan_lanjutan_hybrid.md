# 📑 Plan Lanjutan Agent Pribadi (AG) - Hybrid Reverse Proxy

Dokumen ini merinci implementasi arsitektur **Hybrid Docker** untuk menghilangkan port `:7777` dalam akses web (`komputerku.nour`), dengan penekanan pada **Kontrol Versi Binary Nginx secara Manual** yang diminta oleh Lycus.

---

## 1. 🎯 Tujuan Implementasi Hybrid

- **Menghilangkan Port**:  
  Mengalihkan traffic dari **Port 80 (HTTP default)** pada Host ke **Port 7777** tempat Agent Service berjalan.

- **Kontrol Versi Nginx**:  
  Menyimpan binary Nginx versi spesifik di `/bin/nginx/1.xx.x/` **(dalam konteks Docker build)**, bukan menggunakan image Docker Nginx standar dari Docker Hub.

- **Mempertahankan Stabilitas**:  
  Agent Service inti (`agent_service.py`) tetap berjalan di **Host VENV** untuk menjamin akurasi pembacaan data hardware lokal (misalnya suhu, RAM, GPU).

---

## 2. 🏛️ Struktur Direktori Baru (Dengan Penambahan Binary)

Kita perlu menambahkan direktori untuk menyimpan binary Nginx yang diunduh dan dikelola secara manual:

```
PersonalAgent/
├── bin/
│   └── nginx/
│       └── 1.25.4/               # Contoh versi Nginx
│           ├── nginx             # Binary Nginx (hasil unzip/compile)
│           └── conf/             # File konfigurasi pendukung (jika diperlukan)
├── nginx/
│   └── agent.conf                # Konfigurasi Reverse Proxy (sudah ada)
├── docker-compose.yml            # Orchestration service (Nginx container + jaringan)
└── Dockerfile.nginx              # DOCKERFILE BARU: untuk build image Nginx lokal berbasis binary custom
```

> 💡 **Catatan**:  
> Binary Nginx di `bin/nginx/1.25.4/` akan disalin ke dalam image Docker melalui `Dockerfile.nginx`, memastikan versi dan integritas binary tetap terkendali.
