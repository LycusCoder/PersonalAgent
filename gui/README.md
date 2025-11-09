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
