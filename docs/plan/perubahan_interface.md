## Perubahan Interface — Ringkasan Perubahan (React + TypeScript, Tailwind, Jarvis UI)

Tanggal: 2025-11-09

Ini dokumen ringkas yang menjelaskan perubahan interface yang telah dan akan dilakukan pada proyek *PersonalAgent*. Ditujukan untuk developer dan operator yang perlu mengetahui pengaruh perubahan UI terhadap build, deployment, dan integrasi backend.

### Tujuan
- Migrasi dashboard monolit lama ke single-page app modern menggunakan React + TypeScript.
- Berikan tampilan "Jarvis-like" (karakter interaktif + chat assistant) agar pengguna dapat berinteraksi (tanya jawab) untuk memeriksa status komputer.
- Pertahankan integrasi backend (Flask) dan asset statis yang disajikan oleh Flask di `/static/gui`.

### Ringkasan teknis perubahan
- Frontend baru ditempatkan di folder `gui/` (Vite, React 18, TypeScript).
- Styling: Tailwind CSS (postcss + autoprefixer) + beberapa utilitas CSS khusus.
- Komponen utama yang ditambahkan:
  - `Character.tsx` — avatar / karakter Jarvis (ringkasan status, visual idle/speaking).
  - `Chat.tsx` — UI chat (history sederhana + input) yang memanggil endpoint backend `/api/chat`.
  - `Dashboard.tsx` — layout baru: area karakter/chat + panel system cards (RAM/CPU/GPU).
- Service API baru: `gui/src/services/chat.ts` (POST /api/chat). Frontend masih menggunakan `gui/src/services/api.ts` untuk `/api/status`.
- Build Vite dikonfigurasi untuk output ke `static/gui` (base `/static/gui/`). Template Flask `templates/dashboard.html` telah diupdate untuk mem-mount React app dan backup lama disimpan di `templates/dashboard.legacy.html`.
- CLI: `agent.sh` + `cli/*_launcher.sh` diperbarui supaya ada perintah/flag `open-ui`/`--ui` untuk membuka dashboard.

### Kontrak API (ringkas)
- GET /api/status
  - Response: { success: boolean, data: { ram, cpu, gpu } }
  - Frontend: `getStatus()` di `gui/src/services/api.ts` dipanggil setiap 5s untuk refresh.
- POST /api/chat
  - Request: { message: string }
  - Response yang diharapkan: { success: boolean, reply: string } (frontend membaca `reply` atau `message` fallback)

### Perubahan file penting
- `gui/` — seluruh frontend React+TS, config Tailwind, postcss. Build menghasilkan `static/gui/index.html` dan `static/gui/assets/*`.
- `templates/dashboard.html` — diganti dengan mountpoint React (`<div id="root"></div>`) yang memuat `index.js`.
- `templates/dashboard.legacy.html` — backup dari UI lama.
- `cli/ag_launcher.sh`, `cli/agt_launcher.sh`, `agent.sh` — dukungan open-ui ditambahkan.

### Cara build & verifikasi (local)
1) Pasang dependensi frontend (dari root repo):

```bash
cd gui
npm install
```

2) Build frontend (produksi -> hasil ke `static/gui`):

```bash
npm run build
```

3) Pastikan Flask berjalan (contoh):

```bash
nohup python3 agent_service.py > logs/agent_run.log 2>&1 &
```

4) Verifikasi asset tersedia:

```bash
curl -sS http://localhost:7777/static/gui/assets/index.js | head -n 5
curl -sS http://localhost:7777/ | sed -n '1,120p'
```

5) Buka UI (lokal):

```bash
./agent.sh open-ui
# atau langsung buka http://localhost:7777
```

### Edge cases & perhatian
- Nama file build dapat berubah jika Vite diatur untuk hashing asset — saat ini template merujuk pada `/static/gui/assets/index.js` karena build default (lihat `index.html` di `static/gui`). Jika konfigurasi berubah gunakan mekanisme manifest atau serve `static/gui/index.html` langsung.
- CORS tidak menjadi masalah saat Flask dan Vite berada di host yang sama saat produksi (assets dilayani oleh Flask). Saat dev, Vite dev server mem-proxy `/api` ke Flask.
- Pastikan endpoint `/api/chat` aman (rate limit / input sanitization) jika akan diekspos lebih luas.

### Rollback plan
1. Kembalikan `templates/dashboard.html` dari `templates/dashboard.legacy.html` jika versi lama diperlukan.
2. Hapus atau abaikan `static/gui` (atau ganti index.html ke file lama) dan restart Flask.

### Tes minimal yang sudah dilakukan
- TypeScript checked (tsc --noEmit)
- Unit test: Vitest (satu test untuk SystemCard) — ditambahkan sebelumnya.
- Build Vite berhasil dan menghasilkan `static/gui/assets/index.js` dan `index.css`.

### Next steps / rekomendasi
1. Lengkapi UX chat: streaming responses, visual typing indicator.
2. Tambahkan e2e quick smoke test (Playwright) yang membuka `http://localhost:7777`, memastikan `#root` mount dan elemen Chat muncul.
3. Dokumentasi deploy: tambahkan step di README root untuk build frontend selama CI (npm ci && npm run build) dan deploy step pada Dockerfile jika perlu.
4. Perbaiki dan perluas unit tests (Chat, Character) serta lint CI.

Jika setuju, saya bisa:
- Menambahkan file README singkat `gui/README.md` berisi dev/build/deploy commands, atau
- Lanjut polish (avatar animation, suara, keyboard shortcuts), atau
- Membuat PR branch khusus untuk fitur Jarvis.
