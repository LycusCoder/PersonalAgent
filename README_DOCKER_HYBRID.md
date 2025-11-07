# 🚀 Agent Pribadi (AG) - Docker Hybrid Update

## 🎉 What's New?

Update terbaru Agent Pribadi sekarang mendukung **Docker Hybrid Mode**!

### ✨ Fitur Baru

1. **Interactive Start Mode**
   ```bash
   ./agent.sh start
   ```
   - Pilih [Y] untuk Docker + Nginx
   - Pilih [N] untuk Native Flask only
   - Mode tersimpan otomatis!

2. **Docker Hybrid Setup**
   ```bash
   ./agent.sh setup-docker
   ```
   - Download & install Nginx/Apache
   - Download & install MySQL/PostgreSQL/MongoDB
   - Smart validation (skip jika file valid)
   - Auto-generate Dockerfile
   - Build Docker image

3. **Docker Verification**
   ```bash
   ./agent.sh verify-docker
   ```
   - Check Docker installation
   - Check files di `/bin`
   - Check Docker images

### 🎯 Quick Start

```bash
# 1. Verifikasi sistem
./agent.sh verify

# 2. Verifikasi Docker (optional)
./agent.sh verify-docker

# 3. Setup Docker Hybrid (optional)
./agent.sh setup-docker
# Pilih: Nginx + MySQL (recommended)

# 4. Start service
./agent.sh start
# Pilih: [Y] untuk dengan Docker

# 5. Check status
./agent.sh status

# 6. Test
ag bantuan
```

---

## 📊 Comparison: Native vs Docker

| Feature | Native Mode | Docker Mode |
|---------|-------------|-------------|
| **Flask Backend** | ✅ Port 7777 | ✅ Port 7777 |
| **Reverse Proxy** | ❌ | ✅ Nginx/Apache |
| **Custom Domain** | ❌ | ✅ komputerku.nour |
| **Database** | Manual | ✅ Auto-setup |
| **Isolation** | ❌ | ✅ Containerized |
| **Performance** | Fast | Fast |
| **Setup Time** | 1 min | 5-10 min |

---

## 🛠️ Available Commands

### System Commands
```bash
./agent.sh verify          # Verify system dependencies
./agent.sh verify-docker   # Verify Docker & hybrid setup
./agent.sh setup           # One-time system setup
./agent.sh setup-docker    # Docker hybrid setup
```

### Service Commands
```bash
./agent.sh start           # Start with mode selection
./agent.sh stop            # Stop all services
./agent.sh restart         # Restart with last mode
./agent.sh status          # Show status & mode
./agent.sh logs            # View logs
```

---

## 📦 Supported Packages

### Web Servers
- **Nginx**: 1.26.0, 1.25.4, 1.24.0 ⭐ Recommended
- **Apache**: 2.4.65, 2.4.57

### Databases
- **MySQL**: 9.4.0, 8.4.6, 8.0.40 ⭐ Recommended
- **PostgreSQL**: 18.0, 17.2, 16.6
- **MongoDB**: 8.0.4, 7.0.14

### Other Tools
- PHP, Node.js, Go, Pocketbase

Full list: `config/tools/packages.yaml`

---

## 🐛 Bug Fixes

- ✅ Fixed PyYAML detection di `verify` command
- ✅ Improved ag command registration detection
- ✅ Enhanced stop command (auto-cleanup)
- ✅ Better error messages

---

## 📚 Documentation

- **Complete Guide**: [docs/docker_hybrid_guide.md](docs/docker_hybrid_guide.md)
- **Changelog**: [CHANGELOG.md](CHANGELOG.md)
- **Golden Rules**: [docs/rules/golden_rules.md](docs/rules/golden_rules.md)

---

## 🎓 Example Usage

### Scenario 1: Quick Start (Native)
```bash
./agent.sh verify
./agent.sh setup
./agent.sh start
# Pilih [N] untuk native mode
ag "cek ram"
```

### Scenario 2: Production Setup (Docker)
```bash
# Install Docker (if not installed)
curl -fsSL https://get.docker.com | sh
sudo systemctl start docker

# Verify Docker
./agent.sh verify-docker

# Setup hybrid
./agent.sh setup-docker
# Pilih: [1] Nginx → version 1.26.0
# Pilih: [1] MySQL → version 8.4.6

# Start with Docker
./agent.sh start
# Pilih [Y] untuk Docker mode

# Access
curl http://localhost:7777/health
curl http://komputerku.nour/health
```

### Scenario 3: Development Workflow
```bash
# Start in native mode for development
./agent.sh start
# Pilih [N]

# Make changes to code...

# Restart
./agent.sh restart

# Check logs
./agent.sh logs

# When ready for production, setup Docker
./agent.sh setup-docker

# Restart with Docker
./agent.sh restart
# Mode akan otomatis switch ke docker
```

---

## 🔧 Troubleshooting

### Docker not installed?
```bash
curl -fsSL https://get.docker.com | sh
sudo systemctl start docker
```

### Port 7777 in use?
```bash
./agent.sh stop
sudo lsof -ti:7777 | xargs kill -9
```

### PyYAML not detected?
```bash
pip3 install PyYAML
./agent.sh verify
```

### Downloaded file corrupt?
```bash
rm -rf /tmp/agent_docker_setup/
./agent.sh setup-docker
```

---

## 💡 Tips

1. **Use Nginx** for production (faster & lighter)
2. **Use MySQL** for general purpose (most compatible)
3. **Smart caching** akan skip download jika file valid
4. **Mode is saved** - restart tanpa input ulang
5. **Check logs** jika ada error: `./agent.sh logs`

---

## 🤝 Contributing

Follow the **Golden Rules**: `docs/rules/golden_rules.md`

Key principles:
- ❌ No hardcoded paths
- ❌ No LLM for core logic (rule-based only)
- ✅ Always use error handling
- ✅ Cross-platform compatible
- ✅ Use `PROJECT_ROOT` for paths

---

## 📝 License

[Your License Here]

---

## 👥 Team

**Maintainer**: Tuan Affif  
**Contributors**: Agent Pribadi Team

---

**Last Updated**: 2025-08-XX  
**Version**: 1.1.0
