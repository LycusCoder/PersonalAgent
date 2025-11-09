# GUI (React + TypeScript) — PersonalAgent

Frontend SPA yang dibangun dengan Vite + React + TypeScript. Output produksi dibangun ke `static/gui` dan dilayani oleh Flask backend.

## Quick start (development)

1. Masuk ke folder `gui/`:

```bash
cd gui
```

2. Pasang dependencies (hanya sekali):

```bash
npm install
```

3. Jalankan dev server (Vite) — otomatis proxy `/api` ke backend di `http://localhost:7777` saat dev:

```bash
npm run dev
```

Buka http://localhost:5173 (atau port yang Vite tampilkan).

## Build produksi (untuk disajikan oleh Flask)

Build akan menaruh file statis ke `../static/gui` sesuai konfigurasi Vite.

```bash
cd gui
npm run build
```

Setelah build, restart Flask jika perlu, lalu buka `http://localhost:7777` untuk melihat dashboard.

## Scripts

- `npm run dev` — jalankan Vite dev server (proxy `/api` ke Flask via `vite.config.ts`).
- `npm run build` — produksi, output ke `static/gui`.
- `npm run preview` — preview build lokal (Vite preview).
- `npm run typecheck` — TypeScript typecheck.
- `npm run test` — jalankan unit tests (Vitest).
- `npm run lint` / `npm run format` — lint / format project.

## Struktur penting

- `src/main.tsx` — entry point
- `src/App.tsx` — root App
- `src/components/` — komponen React (Character, Chat, Dashboard, SystemCard, dll.)
- `src/services/` — client API untuk berkomunikasi dengan backend (`/api/status`, `/api/chat`)
- `src/styles/global.css` — Tailwind directives + override kustom
- `tailwind.config.cjs`, `postcss.config.cjs` — konfigurasi Tailwind/PostCSS

## Backend contract (ringkasan)

- GET `/api/status` — mengembalikan status sistem (RAM/CPU/GPU)
- POST `/api/chat` — mengirim pesan chat; respon diharapkan memiliki field `reply` (string)

## Notes & troubleshooting

- Jangan commit `node_modules/` — sudah ditambahkan ke `.gitignore`.
- Jika build produksi tidak muncul di `static/gui`, cek `vite.config.ts` dan jalankan `npm run build` dari dalam `gui/`.
- Dev server Vite menggunakan proxy untuk menghindari CORS; pastikan Flask berjalan di `http://localhost:7777` saat melakukan pengembangan fitur yang memanggil API.

## Dokumentasi desain

Lihat `docs/plan/perubahan_interface.md` untuk ringkasan tujuan desain, kontrak API, dan langkah rollout.

## Want to contribute

- Buat branch baru dari `dev` (contoh: `feat/jarvis-typing`) lalu push PR ke `dev`.
- Jalankan test & lint sebelum membuat PR.
# GUI (React + TypeScript)

This folder contains a small Vite + React + TypeScript GUI for the Agent Pribadi dashboard.

Quick start (from repository root):

```bash
cd gui
npm install
npm run dev    # development server, proxies /api to http://localhost:7777
npm run build  # build production files into ./static/gui
```

Notes:
- Dev server proxies `/api` to `http://localhost:7777` (Flask default in this repo).
- Production build outputs to `static/gui` and is served at `/static/gui/`.
- Example Flask template: `templates/dashboard.react.html` (added for reference).
