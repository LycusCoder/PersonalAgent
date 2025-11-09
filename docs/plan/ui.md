Wireframe Planning: Personal Agent (Chat-First UI)

Ini adalah dekonstruksi visual untuk UI baru, menggunakan komponen React yang sudah ada (gui/src/components/).

Wireframe 1: Halaman Utama (Default State)

Ini adalah tampilan default saat app dibuka. Fokus 100% pada interaksi.

+-------------------------------------------------------------------------+
| [=] (Menu)                                                              | <- Tombol buka/tutup Sidebar.tsx
|                                                                         |
|                                                                         |
|                 (Area ini adalah <Character.tsx>                         |
|                  dengan gambar karakter sebagai                         |
|                  background, diberi vignette gelap)                     |
|                                                                         |
|                                                                         |
|  [Agent]: Halo Lycus, ada yang bisa dibantu?                             | <- Ini adalah <Chat.tsx> (History view)
|                                                                         |
|  [User]: Tampilkan status sistem.                                       |
|                                                                         |
|                                                                         |
|                                                                         |
|                                                                         |
+-------------------------------------------------------------------------+
| [ Ketik pesan di sini...                                          ] [Send] | <- Ini adalah <Chat.tsx> (Input bar)
+-------------------------------------------------------------------------+


Komponen Terpakai:

App.tsx (Shell): Mengatur state utama (apakah modal terbuka, apakah sidebar terbuka).

Character.tsx: Dipakai sebagai background full-screen (Layer 1).

Chat.tsx: Dipakai 2 kali atau di-split:

Untuk area history (transparan di atas karakter, Layer 2).

Untuk input bar (nempel di bawah, Layer 2).

Wireframe 2: Halaman Utama + Menu (Off-Canvas)

Ini adalah tampilan saat user mengklik tombol menu [=].

+--------------------+----------------------------------------------------+
| [<] (Close)        | [=]                                                |
| **Menu Perintah** |                                                    |
| (Render dari      |                                                    |
| <Sidebar.tsx>)     |   (Area <Character.tsx>... )                       |
|                    |                                                    |
| [>] Tampilkan      |                                                    |
|     Status Sistem  |   [Agent]: Halo Lycus...                           |
|                    |                                                    |
| [>] Buka Tool      |   [User]: Tampilkan status...                      |
|     Management     |                                                    |
|                    |                                                    |
| [>] Ganti Tema     |                                                    |
|     (Dark/Light)   |                                                    |
|                    |                                                    |
+--------------------+----------------------------------------------------+
| [ Ketik pesan di sini...                                          ] [Send] |
+-------------------------------------------------------------------------+


Komponen Terpakai:

Sidebar.tsx: Komponen ini kita reuse. Tapi isinya BUKAN link navigasi, melainkan "Prompt Suggestions".

Flow:

User klik tombol [=].

App.tsx mengubah state isSidebarOpen = true.

<Sidebar.tsx> muncul (slide dari kiri).

User mengklik [>] Tampilkan Status Sistem.

Aksi: Sidebar.tsx ditutup (isSidebarOpen = false) DAN perintah "Tampilkan Status Sistem" otomatis dikirim ke chat.

Wireframe 3: Halaman Utama + Modal (Summoned UI)

Ini adalah tampilan SETELAH user mengirim perintah (baik via ketik atau klik menu) dan agent merespons dengan command untuk buka UI.

+-------------------------------------------------------------------------+
| [=]                                                                     |
|                                                                         |
|                                                                         |
|    (Area <Character.tsx>... SEKARANG DIBUAT BLUR / DIMMED)              |
|                                                                         |
|       +-----------------------------------------------------------+     |
|       | **System Monitor** (Render <Dashboard.tsx>)           [X] |     | <- Tombol Close Modal
|       +-----------------------------------------------------------+     |
|       |                                                           |     |
|       |  +-----------------+ +-----------------+ +--------------+ |     |
|       |  | <SystemCard.tsx>| | <SystemCard.tsx>| | <Widget.tsx> | |     |
|       |  |  CPU: 80%       | |  RAM: 60%       | |  Tool...     | |     |
|       |  +-----------------+ +-----------------+ +--------------+ |     |
|       |                                                           |     |
|       |  (Sisa konten dari <Dashboard.tsx>...)                    |     |
|       |                                                           |     |
|       +-----------------------------------------------------------+     |
|                                                                         |
|                                                                         |
+-------------------------------------------------------------------------+
| [ Ketik pesan di sini...  (Disabled/Blur saat modal terbuka) ] [Send] |
+-------------------------------------------------------------------------+


Komponen Terpakai:

Dashboard.tsx: Di-render di dalam container Modal.

SystemCard.tsx: Dipakai oleh Dashboard.tsx seperti biasa.

Widget.tsx: Dipakai oleh Dashboard.tsx seperti biasa.

Flow:

User mengirim perintah "Tampilkan status sistem".

Backend merespons, misal: { "type": "MODAL", "view": "DASHBOARD" }.

App.tsx menangkap ini, mengubah state currentModal = 'DASHBOARD'.

Sebuah container modal full-screen muncul (Layer 3).

Di dalam modal itu, kita render <Dashboard.tsx>.

User klik [X], state diubah currentModal = null, modal tertutup.

---

## Status implementasi (ringkasan terbaru)

Catatan: dokumen ini diperbarui pada 2025-11-09 untuk mencerminkan pekerjaan yang sudah dilakukan dan yang masih pending.

### Sudah dikerjakan
- App shell (gui/src/App.tsx) — DI-REFACTOR jadi "chat-first shell":
  - Background karakter full-screen (Layer 1).
  - Chat utama dipindahkan ke layer atas dan menerima aksi dari backend untuk membuka modal.
  - Modal container ditambahkan (render Dashboard saat currentModal === 'DASHBOARD').
- Sidebar off-canvas (gui/src/components/Sidebar.tsx) — sekarang menerima props `isOpen`, `onClose`, `onCommandClick` dan mengirim perintah sebagai "Prompt Suggestions".
- Chat (gui/src/components/Chat.tsx):
  - Exposes forwardRef `sendPrompt` so Sidebar can trigger messages.
  - Now forwards backend `action` objects to App via `onAgentAction` prop.
  - Chat history persistence implemented (localStorage) with helper `gui/src/services/storage.ts` (load/save/clear/export).
  - Added toolbar: Export / Clear / Voice toggle (TTS via Web Speech API).
  - Compact responsive avatar in header (replaces full Character card for better responsiveness).
  - Accessibility improvements: message container has role="log" and aria-live="polite"; input/button have aria-labels; Chat supports `disabled` prop so App can disable input when modal open.
- Dashboard (gui/src/components/Dashboard.tsx): converted to modal-only renderer that fetches system status and renders `SystemCard`s. It no longer renders the main page layout.
- Character (gui/src/components/Character.tsx) & CSS (`gui/src/styles/global.css`): added a small reaction animation and CSS hooks for avatar reaction.
- Backend (core/chat_rules.py): system summary response now includes `action: { type: 'OPEN_MODAL', view: 'DASHBOARD' }` so frontend can open the modal automatically.
- Tests & build:
  - Added unit tests for storage helper (gui/src/services/__tests__/storage.test.ts).
  - Ran vitest and all tests passed locally.
  - Production build (Vite) verified and assets written to `static/gui/assets/`.
  - Flask restarted and serving SPA; API endpoint `/api/chat` returns `action` payload as expected.

### Partially done / minor gaps
- Modal wiring: App renders modal and Dashboard content — visual modal exists and can be opened by backend action. However focus-trap and ESC/keyboard handling for the modal (full accessibility for dialogs) is only partially addressed and remains to be implemented.
- Chat input disabling when modal open: Chat now supports a `disabled` prop; App must pass `disabled={currentModal !== null}` to ensure input is disabled while modal open. This coupling is planned but not yet applied in all places.
- Avatar reaction: CSS exists and Chat toggles a transient `avatarReacting` state; the header avatar now uses the `react` class when reacting. Further polish (blink, SVG micro-expressions) can be added.

### Pending / next major work (recommended priority)
1. M3 — Modal accessibility and behaviour (high):
	- Implement focus-trapping inside modal, handle ESC to close, ensure tab order, and set aria-modal/role=dialog + aria-labelledby.
	- When modal opens, pass `disabled` to `Chat` so input is disabled and visually dimmed.
	- Add tests for modal open/close behaviour.
2. M6 — Accessibility (medium):
	- Add aria-live announcements for history clear/export actions.
	- Improve keyboard focus styles and ensure Sidebar is keyboard-operable.
3. M5 — Responsiveness polish (low/medium):
	- Tweak spacing and truncation for very small screens; optionally convert Sidebar to full-screen sheet on small devices.
4. M7 — Tests (medium):
	- Add Vitest/Testing Library tests for: Sidebar command -> Chat send, App modal open on backend action, and Chat disabled state when modal open.
5. Optional: server-side chat history sync (low):
	- Provide API + DB persistence and opt-in sync to store histories across devices.

## How to reproduce & run locally
1. Build frontend (from repo root):

```bash
cd gui
npm install    # if needed
npm run build
```

2. Restart backend/service so Flask serves updated assets and loads `core/chat_rules.py` changes:

```bash
./agent.sh restart
```

3. Open the app: http://localhost:7777 — the SPA now includes the built CSS/JS and the Chat-first shell.

## Notes & design decisions
- We intentionally kept chat history local by default (localStorage) to avoid introducing server-side persistence and privacy concerns. The storage helper is small and isolated to allow later replacement with server sync.
- The Chat-first model treats the chat as the primary UI; Dashboard is modal-only (summoned by commands), which keeps the landing experience minimal and focused.
- Accessibility and tests are medium-priority and scheduled in the next sprint; core behaviour is in place so these can be implemented incrementally.

If you want, I can now implement the top-priority M3 tasks (focus-trap, ESC, and disabling `Chat` while modal is open). Say "go" and I'll apply those changes, run tests and build, and then restart the Flask service for verification.