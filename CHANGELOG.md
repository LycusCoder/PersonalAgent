# Changelog - Agent Pribadi (AG)

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [1.1.0] - 2025-08-XX

### ✨ Added

#### Docker Hybrid Setup System
- **New Command**: `./agent.sh verify-docker`
  - Verifikasi Docker installation & version
  - Check Docker Compose availability
  - Scan web servers (Nginx/Apache) di `/bin/{app}/{version}/`
  - Scan databases (MySQL/PostgreSQL/MongoDB) di `/bin/{db}/{version}/`
  - Check Docker images status

- **New Command**: `./agent.sh setup-docker`
  - Interactive setup untuk Docker Hybrid
  - Pilihan Web Server: Nginx (recommended) / Apache2
  - Pilihan Database: MySQL / PostgreSQL / MongoDB / Skip
  - Smart download dengan validation
  - Auto-skip jika file sudah valid
  - File integrity check (detect corrupt files)
  - Auto-generate `Dockerfile.hybrid`
  - Docker image build integration

- **New Script**: `cli/docker_setup_hybrid.sh`
  - Comprehensive Docker hybrid setup script
  - YAML parser untuk `config/tools/packages.yaml`
  - Download manager dengan progress indicator
  - File validation & integrity check
  - Multi-format archive support (tar.gz, tar.xz, zip)
  - Smart caching (skip re-download if valid)
  - Dockerfile generator
  - Docker image builder

- **New Config**: `config/tools/packages.yaml`
  - Centralized package download configuration
  - Supported packages:
    - Web Servers: Nginx 1.26.0/1.25.4/1.24.0, Apache 2.4.65/2.4.57
    - Databases: MySQL 9.4.0/8.4.6/8.0.40, PostgreSQL 18.0/17.2/16.6, MongoDB 8.0.4/7.0.14
    - Languages: PHP 8.4/8.3/8.2/8.1, Node.js 24.9.0/23.11.0/22.14.0/20.18.0, Go 1.24.1/1.23.4
    - Tools: Pocketbase 0.25.9

- **New Documentation**: `docs/docker_hybrid_guide.md`
  - Complete guide untuk Docker Hybrid setup
  - Quick start tutorial
  - Command reference
  - Troubleshooting guide
  - Advanced usage examples

#### Enhanced Start Command
- **Interactive Mode**: `./agent.sh start`
  - Menampilkan prompt pilihan mode:
    - [Y] Dengan Docker Agent (Flask + Nginx)
    - [N] Native saja (Flask only)
  - Mode otomatis tersimpan di `.agent_mode.conf`
  - Auto-fallback ke native jika Docker tidak tersedia

#### Smart Stop & Restart
- **Enhanced Stop**: `./agent.sh stop`
  - Auto-detect mode (native/docker)
  - Stop Flask service via PID
  - Stop Docker container jika mode docker
  - Multiple fallback methods untuk kill process
  - Port cleanup verification

- **Smart Restart**: `./agent.sh restart`
  - Membaca mode terakhir dari `.agent_mode.conf`
  - Restart semua service sesuai mode
  - Tidak perlu input ulang

### 🔧 Fixed

- **PyYAML Detection Bug** (agent.sh line 90-105)
  - Fixed case-sensitive import issue
  - Added proper package name mapping:
    - `PyYAML` → import `yaml`
    - `Flask` → import `flask`
    - `psutil` → import `psutil`
    - `requests` → import `requests`

- **ag Command Detection** (agent.sh line 147-168)
  - Improved detection logic
  - Better error messages
  - Clear instructions untuk source shell

### 🎨 Improved

- **Help Command**: `./agent.sh help`
  - Added Docker Hybrid commands
  - Added Start Modes explanation
  - Better formatting & examples

- **Status Command**: `./agent.sh status`
  - Show current mode (native/docker)
  - Docker container status (jika mode docker)
  - Enhanced process information

- **Verify Command**: `./agent.sh verify`
  - Better package detection
  - Clearer error messages
  - Improved shell detection

### 📚 Documentation

- Added `docs/docker_hybrid_guide.md` - Complete Docker Hybrid guide
- Added `CHANGELOG.md` - Project changelog
- Updated `README.md` with Docker Hybrid features (jika ada)

---

## [1.0.0] - 2025-08-XX

### 🎉 Initial Release

#### Core Features
- **CLI Manager**: `agent.sh`
  - System verification
  - Setup automation
  - Service management (start/stop/restart)
  - Status monitoring
  - Log viewing

- **ag Command**: CLI shortcut untuk Agent
  - Normal mode: `ag [command]`
  - TTS mode: `agt [command]`
  - Auto-registration ke shell config

- **Agent Service**: Flask backend
  - REST API endpoints
  - Health check endpoint
  - System monitoring
  - Rule-based responses (no LLM)

#### Project Structure
- `/core` - Core modules
- `/config` - Configuration files
- `/cli` - CLI scripts
- `/storage` - Data storage
- `/logs` - Service logs
- `/bin` - Binary installations

#### Documentation
- `docs/rules/golden_rules.md` - Development rules
- `docs/plan/plan_awal.md` - Initial planning (jika ada)

---

## Legend

- ✨ **Added** - New features
- 🔧 **Fixed** - Bug fixes
- 🎨 **Improved** - Enhancements
- 🗑️ **Removed** - Removed features
- 📚 **Documentation** - Documentation changes
- 🔒 **Security** - Security fixes

---

**Note**: This project follows [Semantic Versioning](https://semver.org/).
