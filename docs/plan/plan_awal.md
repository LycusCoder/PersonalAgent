# 📑 Plan Awal Setup Agent Pribadi (AG) [✅**COMPLETED**✅]

Dokumen ini merangkum tujuan, arsitektur, dan langkah-langkah setup awal untuk Agent Pribadi Tuan Affif, sebuah sistem Rule-Based yang stabil dan akurat.

## 1. 🎯 Tujuan Proyek

1.  **Stabilitas Tertinggi:** Menciptakan Agent Pribadi yang 100% *rule-based* untuk menjamin konsistensi dan kepatuhan absolut (menghindari ketidakpastian LLM).
2.  **Akurasi Data Sistem:** Menyediakan laporan *real-time* yang akurat mengenai status *hardware* Zorin OS (RAM 32GB, RTX 4060, CPU, Suhu).
3.  **Akses Fleksibel:** Agent harus dapat diakses melalui Terminal Command Line Interface (CLI) menggunakan `ag`, Web Dashboard, dan API.
4.  **Persona Konsisten:** Mengimplementasikan persona Sekretaris Sarah dengan gaya bicara formal, profesional, dan hangat (memanggil Tuan Affif).

## 2. 🏛️ Arsitektur Sistem

Proyek ini menggunakan arsitektur **Client-Server Ringan** berbasis Python Flask, memisahkan logika utama (Core) dari antarmuka (Service/CLI).

| Komponen | Lokasi File | Fungsi Utama |
| :--- | :--- | :--- |
| **Server Inti** | `agent_service.py` | Menjalankan *web server* Flask dan menyediakan API (`/api/chat`). |
| **Logic Inti** | `core/chat_rules.py` | Otak Rule-Based. Menerjemahkan *prompt* ke fungsi sistem/persona yang tepat. |
| **System Calls** | `core/system_monitor.py` | Mengumpulkan data *real-time* dari OS (via `psutil`, `nvidia-smi`, `subprocess`). |
| **Persona** | `core/persona.py` | Menjaga konsistensi gaya bicara dan format respons (`Tuan Affif`, sapaan waktu). |
| **Akses CLI** | `cli/ag_launcher.sh` | Skrip *shell* yang mengirim *prompt* CLI ke API Flask menggunakan `curl` dan mengintegrasikan **TTS (`espeak`)**. |

## 3. 📦 Setup Awal dan Dependensi

### 3.1. Instalasi Pustaka Python

Semua dependensi Python wajib diinstal menggunakan `pip`.

```bash
# Isi file requirements.txt
echo "Flask" > requirements.txt
echo "psutil" >> requirements.txt

# Instalasi
pip install -r requirements.txt
````

### 3.2. Instalasi Utility Linux

Pastikan *tool* berikut tersedia di Zorin OS (sebagian besar sudah ada, `espeak` mungkin perlu diinstal).

```bash
# Untuk fitur Text-to-Speech
sudo apt update && sudo apt install espeak

# Untuk monitoring GPU (Jika belum terinstal)
sudo apt install nvidia-smi
```

### 3.3. Konfigurasi Host Lokal (Opsional, untuk Web Access)

Untuk mengakses Agent Dashboard dari `http://komputerku.nour`, edit file `/etc/hosts` Anda:

```bash
sudo nano /etc/hosts
# Tambahkan baris berikut di akhir file:
127.0.0.1    komputerku.nour
```

## 4\. 🚀 Langkah Awal Run

Setelah semua file (`.py` dan `.sh`) terisi dan dependensi terinstal:

1.  **Jalankan Server Inti (Background):**
    ```bash
    python3 agent_service.py &
    ```
2.  **Konfigurasi Command Global `ag`:**
      * Pastikan `cli/ag_launcher.sh` berisi fungsi yang mengirim `curl` ke Flask API.
      * Buat fungsi *shell* `ag` di `.zshrc` atau `.bashrc` yang memanggil skrip *launcher*.
    <!-- end list -->
    ```bash
    source ~/.zshrc  # Muat ulang shell
    ```
3.  **Uji Coba:**
    ```bash
    ag bantu cek jam berapa
    ```

## 5\. ✅ Target Selesai Tahap Awal

  * `core/persona.py`: Fungsi sapaan waktu (`get_greeting_time`) sudah siap.
  * `core/system_monitor.py`: Fungsi pengambilan data RAM dan CPU (`get_ram_status`, `get_cpu_status`) sudah siap.
  * *Server* Flask berhasil dijalankan dan merespons `curl` dari terminal.
