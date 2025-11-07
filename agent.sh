#!/bin/bash
# ============================================================================
# AGENT.SH - Main CLI Manager untuk Agent Pribadi (AG)
# ============================================================================
# Centralized management script untuk semua operasi Agent
# Author: Agent Pribadi Team
# Version: 1.0.0
# ============================================================================

set -e  # Exit on error

# --- Configuration ---
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"
CLI_DIR="$PROJECT_ROOT/cli"
SERVICE_FILE="$PROJECT_ROOT/agent_service.py"
PID_FILE="$PROJECT_ROOT/.agent.pid"
LOG_FILE="$PROJECT_ROOT/logs/agent.log"
API_URL="http://localhost:7777"
MODE_FILE="$PROJECT_ROOT/.agent_mode.conf"
DOCKER_AGENT_SCRIPT="$PROJECT_ROOT/docker-agent.sh"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# --- Helper Functions ---

print_banner() {
    echo -e "${BLUE}"
    echo "╔════════════════════════════════════════════════════════╗"
    echo "║         AGENT PRIBADI (AG) - CLI MANAGER              ║"
    echo "║                    Version 1.0.0                       ║"
    echo "╚════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# --- Command: verify ---
cmd_verify() {
    print_banner
    echo "🔍 VERIFIKASI SISTEM"
    echo "════════════════════════════════════════════════════════"
    echo ""
    
    local all_ok=true
    
    # 1. Check Python
    echo "1️⃣ Checking Python..."
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
        print_success "Python3 found: $PYTHON_VERSION"
    else
        print_error "Python3 not found!"
        all_ok=false
    fi
    echo ""
    
    # 2. Check pip
    echo "2️⃣ Checking pip..."
    if command -v pip3 &> /dev/null; then
        PIP_VERSION=$(pip3 --version 2>&1 | cut -d' ' -f2)
        print_success "pip3 found: $PIP_VERSION"
    else
        print_error "pip3 not found!"
        all_ok=false
    fi
    echo ""
    
    # 3. Check required Python packages
    echo "3️⃣ Checking Python dependencies..."
    local required_packages=("Flask" "psutil" "PyYAML" "requests")
    for package in "${required_packages[@]}"; do
        if python3 -c "import ${package,,}" &> /dev/null; then
            print_success "$package installed"
        else
            print_error "$package NOT installed"
            all_ok=false
        fi
    done
    echo ""
    
    # 4. Check jq (for ag command)
    echo "4️⃣ Checking jq (JSON parser)..."
    if command -v jq &> /dev/null; then
        JQ_VERSION=$(jq --version 2>&1)
        print_success "jq found: $JQ_VERSION"
    else
        print_warning "jq not found (required for ag command)"
        print_info "Install: sudo apt-get install jq"
        all_ok=false
    fi
    echo ""
    
    # 5. Check curl
    echo "5️⃣ Checking curl..."
    if command -v curl &> /dev/null; then
        CURL_VERSION=$(curl --version 2>&1 | head -1)
        print_success "curl found: ${CURL_VERSION:0:40}..."
    else
        print_error "curl not found!"
        all_ok=false
    fi
    echo ""
    
    # 6. Check project structure
    echo "6️⃣ Checking project structure..."
    local required_dirs=("core" "config" "cli" "storage" "logs" "bin")
    for dir in "${required_dirs[@]}"; do
        if [ -d "$PROJECT_ROOT/$dir" ]; then
            print_success "Directory /$dir exists"
        else
            print_error "Directory /$dir NOT found"
            all_ok=false
        fi
    done
    echo ""
    
    # 7. Check ag command registration
    echo "7️⃣ Checking 'ag' command registration..."
    if command -v ag &> /dev/null; then
        AG_PATH=$(which ag)
        print_success "ag command found: $AG_PATH"
    else
        print_warning "ag command NOT registered in shell"
        print_info "Run: ./agent.sh setup"
    fi
    echo ""
    
    # 8. Check custom host
    echo "8️⃣ Checking custom host (komputerku.nour)..."
    if grep -q "komputerku.nour" /etc/hosts 2>/dev/null; then
        print_success "Custom host configured"
    else
        print_warning "Custom host NOT configured"
        print_info "Run: ./agent.sh setup-host"
    fi
    echo ""
    
    # Final result
    echo "════════════════════════════════════════════════════════"
    if [ "$all_ok" = true ]; then
        print_success "VERIFICATION PASSED! System ready to use! 🎉"
        return 0
    else
        print_error "VERIFICATION FAILED! Please fix issues above."
        print_info "Run './agent.sh setup' to auto-fix most issues"
        return 1
    fi
}

# --- Command: setup ---
cmd_setup() {
    print_banner
    echo "⚙️  SETUP SISTEM"
    echo "════════════════════════════════════════════════════════"
    echo ""
    
    # 1. Install Python dependencies
    echo "1️⃣ Installing Python dependencies..."
    if [ -f "$PROJECT_ROOT/requirements.txt" ]; then
        pip3 install -r "$PROJECT_ROOT/requirements.txt" --quiet
        print_success "Python dependencies installed"
    else
        print_error "requirements.txt not found!"
    fi
    echo ""
    
    # 2. Create necessary directories
    echo "2️⃣ Creating necessary directories..."
    mkdir -p "$PROJECT_ROOT/logs"
    mkdir -p "$PROJECT_ROOT/storage"
    mkdir -p "$PROJECT_ROOT/bin"
    print_success "Directories created"
    echo ""
    
    # 3. Setup ag command
    echo "3️⃣ Setting up 'ag' command..."
    setup_ag_command
    echo ""
    
    # 4. Setup custom host (optional - ask user)
    echo "4️⃣ Setup custom host..."
    read -p "Do you want to setup custom host (komputerku.nour)? [y/N]: " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        cmd_setup_host
    else
        print_info "Skipping custom host setup"
    fi
    echo ""
    
    # 5. Test ag command
    echo "5️⃣ Testing 'ag' command..."
    if command -v ag &> /dev/null; then
        print_success "ag command is working!"
        print_info "Restarting shell to apply changes..."
        print_info "After restart, try: ag bantuan"
    else
        print_warning "ag command not yet available"
        print_info "Please restart your shell: source ~/.bashrc or source ~/.zshrc"
    fi
    echo ""
    
    print_success "SETUP COMPLETED! 🎉"
    print_info "Next steps:"
    print_info "  1. Restart your shell or run: source ~/.bashrc"
    print_info "  2. Start the service: ./agent.sh start"
    print_info "  3. Test: ag bantuan"
}

# --- Command: setup-ag-command ---
setup_ag_command() {
    local ag_launcher="$CLI_DIR/ag_launcher.sh"
    local agt_launcher="$CLI_DIR/agt_launcher.sh"
    
    if [ ! -f "$ag_launcher" ]; then
        print_error "ag_launcher.sh not found at $ag_launcher"
        return 1
    fi
    
    if [ ! -f "$agt_launcher" ]; then
        print_error "agt_launcher.sh not found at $agt_launcher"
        return 1
    fi
    
    # Make launchers executable
    chmod +x "$ag_launcher"
    chmod +x "$agt_launcher"
    
    # Detect shell
    local shell_rc=""
    local shell_name=""
    
    if [ -n "$ZSH_VERSION" ] || [[ "$SHELL" == *"zsh"* ]]; then
        shell_rc="$HOME/.zshrc"
        shell_name="zsh"
    elif [ -n "$BASH_VERSION" ] || [[ "$SHELL" == *"bash"* ]]; then
        shell_rc="$HOME/.bashrc"
        shell_name="bash"
    else
        print_warning "Unknown shell. Defaulting to .bashrc"
        shell_rc="$HOME/.bashrc"
        shell_name="bash"
    fi
    
    print_info "Detected shell: $shell_name"
    print_info "Config file: $shell_rc"
    
    # Check if already registered
    local ag_alias="alias ag='$ag_launcher'"
    local agt_alias="alias agt='$agt_launcher'"
    
    local already_registered=true
    
    if ! grep -q "$ag_launcher" "$shell_rc" 2>/dev/null; then
        already_registered=false
    fi
    
    if ! grep -q "$agt_launcher" "$shell_rc" 2>/dev/null; then
        already_registered=false
    fi
    
    if [ "$already_registered" = true ]; then
        print_info "ag and agt commands already registered in $shell_rc"
        return 0
    fi
    
    # Add aliases to shell config
    echo "" >> "$shell_rc"
    echo "# Agent Pribadi (AG) CLI - Auto-registered by agent.sh" >> "$shell_rc"
    echo "$ag_alias" >> "$shell_rc"
    echo "$agt_alias" >> "$shell_rc"
    echo "" >> "$shell_rc"
    
    print_success "ag and agt commands registered to $shell_rc"
    print_info "  • ag  : Normal mode (TTS optional with -v flag)"
    print_info "  • agt : TTS mode (Voice always enabled)"
    print_info "Run: source $shell_rc"
    
    # Try to source it in current shell
    source "$shell_rc" 2>/dev/null || true
}

# --- Command: setup-host ---
cmd_setup_host() {
    print_info "Setting up custom host..."
    
    if [ -f "$CLI_DIR/setup_hosts.sh" ]; then
        bash "$CLI_DIR/setup_hosts.sh"
    else
        print_error "setup_hosts.sh not found!"
    fi
}

# --- Helper: Check Docker ---
check_docker_available() {
    if ! command -v docker &> /dev/null; then
        return 1
    fi
    
    if ! command -v docker compose &> /dev/null && ! docker compose version &> /dev/null 2>&1; then
        return 1
    fi
    
    return 0
}

# --- Helper: Start Flask Service ---
start_flask_service() {
    print_info "Starting Flask service..."
    
    # Create logs directory
    mkdir -p "$(dirname "$LOG_FILE")"
    
    # Start service in background
    nohup python3 "$SERVICE_FILE" > "$LOG_FILE" 2>&1 &
    local pid=$!
    
    # Save PID
    echo "$pid" > "$PID_FILE"
    
    # Wait and verify
    sleep 2
    
    if ps -p "$pid" > /dev/null 2>&1; then
        print_success "Flask service started successfully! (PID: $pid)"
        
        # Test health endpoint
        sleep 1
        if curl -s "$API_URL/health" > /dev/null 2>&1; then
            print_success "Health check passed!"
        else
            print_warning "Service started but health check failed"
            print_info "Check logs: tail -f $LOG_FILE"
        fi
        return 0
    else
        print_error "Failed to start Flask service"
        print_info "Check logs: tail -f $LOG_FILE"
        rm -f "$PID_FILE"
        return 1
    fi
}

# --- Helper: Start Docker Agent ---
start_docker_agent() {
    print_info "Starting Docker Nginx Reverse Proxy..."
    
    if [ ! -f "$DOCKER_AGENT_SCRIPT" ]; then
        print_error "docker-agent.sh not found!"
        return 1
    fi
    
    # Check if image exists
    if ! docker images | grep -q "agent_nginx"; then
        print_warning "Docker image not found. Building..."
        bash "$DOCKER_AGENT_SCRIPT" build
        if [ $? -ne 0 ]; then
            print_error "Failed to build Docker image"
            return 1
        fi
    fi
    
    # Start Docker container
    bash "$DOCKER_AGENT_SCRIPT" start
    
    if [ $? -eq 0 ]; then
        print_success "Docker agent started successfully!"
        return 0
    else
        print_error "Failed to start Docker agent"
        return 1
    fi
}

# --- Helper: Save Mode ---
save_mode() {
    local mode="$1"
    echo "$mode" > "$MODE_FILE"
}

# --- Helper: Get Saved Mode ---
get_saved_mode() {
    if [ -f "$MODE_FILE" ]; then
        cat "$MODE_FILE"
    else
        echo "native"
    fi
}

# --- Command: start ---
cmd_start() {
    print_banner
    echo "🚀 STARTING AGENT SERVICE"
    echo "════════════════════════════════════════════════════════"
    echo ""
    
    # Check if already running
    if [ -f "$PID_FILE" ]; then
        local pid=$(cat "$PID_FILE")
        if ps -p "$pid" > /dev/null 2>&1; then
            print_warning "Agent service is already running (PID: $pid)"
            print_info "Use './agent.sh stop' first to stop it"
            return 1
        else
            # Stale PID file
            rm -f "$PID_FILE"
        fi
    fi
    
    # Ask user for mode selection
    echo "📦 Pilih mode untuk menjalankan Agent Service:"
    echo ""
    echo "  [Y] Dengan Docker Agent (Nginx Reverse Proxy)"
    echo "      → Flask service + Nginx container"
    echo "      → Akses: http://localhost:7777 & http://komputerku.nour"
    echo ""
    echo "  [N] Native saja (tanpa Docker)"
    echo "      → Hanya Flask service"
    echo "      → Akses: http://localhost:7777"
    echo ""
    read -p "Gunakan Docker Agent? [Y/N]: " -n 1 -r
    echo ""
    echo ""
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        # Mode: With Docker
        print_info "Mode: Flask + Docker Agent (Nginx)"
        echo "════════════════════════════════════════════════════════"
        echo ""
        
        # Check Docker availability
        if ! check_docker_available; then
            print_error "Docker atau Docker Compose tidak tersedia!"
            print_info "Install Docker: https://docs.docker.com/get-docker/"
            echo ""
            print_warning "Falling back to native mode (Flask only)..."
            echo ""
            
            start_flask_service
            save_mode "native"
        else
            # Start Flask first
            if start_flask_service; then
                echo ""
                
                # Start Docker agent
                if start_docker_agent; then
                    save_mode "docker"
                    echo ""
                    echo "════════════════════════════════════════════════════════"
                    print_success "✅ SEMUA SERVICE BERHASIL DIJALANKAN!"
                    echo ""
                    print_info "📍 URL Akses:"
                    print_info "  • http://localhost:7777 (Direct ke Flask)"
                    print_info "  • http://komputerku.nour (Melalui Nginx)"
                    echo ""
                    print_info "💡 Tips:"
                    print_info "  • Test: ag bantuan"
                    print_info "  • Logs: ./agent.sh logs"
                    print_info "  • Status: ./agent.sh status"
                else
                    print_warning "Docker agent gagal dijalankan, tapi Flask tetap jalan"
                    save_mode "native"
                fi
            else
                return 1
            fi
        fi
    else
        # Mode: Native only
        print_info "Mode: Native (Flask only)"
        echo "════════════════════════════════════════════════════════"
        echo ""
        
        if start_flask_service; then
            save_mode "native"
            echo ""
            echo "════════════════════════════════════════════════════════"
            print_success "✅ FLASK SERVICE BERHASIL DIJALANKAN!"
            echo ""
            print_info "📍 URL Akses:"
            print_info "  • http://localhost:7777"
            echo ""
            print_info "💡 Tips:"
            print_info "  • Test: ag bantuan"
            print_info "  • Logs: ./agent.sh logs"
            print_info "  • Status: ./agent.sh status"
        else
            return 1
        fi
    fi
}

# --- Helper: Stop Docker Agent ---
stop_docker_agent() {
    # Check if Docker is available
    if ! check_docker_available; then
        return 0
    fi
    
    # Check if nginx container is running
    if docker ps | grep -q "agent_nginx"; then
        print_info "Stopping Docker Nginx container..."
        
        if [ -f "$DOCKER_AGENT_SCRIPT" ]; then
            bash "$DOCKER_AGENT_SCRIPT" stop > /dev/null 2>&1
            print_success "Docker agent stopped"
        else
            # Fallback: stop container directly
            docker stop agent_nginx > /dev/null 2>&1 || true
            docker rm agent_nginx > /dev/null 2>&1 || true
            print_success "Docker container stopped"
        fi
    fi
}

# --- Command: stop ---
cmd_stop() {
    print_banner
    echo "🛑 STOPPING AGENT SERVICE"
    echo "════════════════════════════════════════════════════════"
    echo ""
    
    local flask_stopped=false
    local mode=$(get_saved_mode)
    
    print_info "Detected mode: $mode"
    echo ""
    
    # Stop Flask Service
    print_info "🔴 Stopping Flask service..."
    
    # Method 1: Try stopping via PID file
    if [ -f "$PID_FILE" ]; then
        local pid=$(cat "$PID_FILE")
        
        if ps -p "$pid" > /dev/null 2>&1; then
            print_info "Stopping agent service (PID: $pid)..."
            kill "$pid" 2>/dev/null || true
            
            # Wait for process to stop
            local count=0
            while ps -p "$pid" > /dev/null 2>&1 && [ $count -lt 10 ]; do
                sleep 1
                count=$((count + 1))
            done
            
            if ps -p "$pid" > /dev/null 2>&1; then
                print_warning "Process didn't stop gracefully, forcing kill -9..."
                kill -9 "$pid" 2>/dev/null || true
                sleep 1
            fi
            
            if ! ps -p "$pid" > /dev/null 2>&1; then
                flask_stopped=true
                print_success "Flask service stopped (PID: $pid)"
            fi
        fi
        
        rm -f "$PID_FILE"
    fi
    
    # Method 2: If still running, try finding process on port 7777
    if [ "$flask_stopped" = false ]; then
        print_info "Checking for processes on port 7777..."
        
        # Try using lsof (Linux/macOS)
        if command -v lsof &> /dev/null; then
            local port_pids=$(lsof -ti:7777 2>/dev/null || true)
            
            if [ -n "$port_pids" ]; then
                print_warning "Found processes on port 7777, killing them..."
                
                for pid in $port_pids; do
                    print_info "Killing PID: $pid"
                    kill -9 "$pid" 2>/dev/null || true
                done
                
                sleep 1
                flask_stopped=true
                print_success "Processes on port 7777 killed"
            fi
        # Try using fuser (Linux alternative)
        elif command -v fuser &> /dev/null; then
            print_info "Using fuser to kill port 7777..."
            fuser -k 7777/tcp 2>/dev/null || true
            sleep 1
            flask_stopped=true
            print_success "Port 7777 cleared via fuser"
        # Try using netstat + kill (fallback)
        elif command -v netstat &> /dev/null; then
            local port_pid=$(netstat -tlnp 2>/dev/null | grep ':7777' | awk '{print $7}' | cut -d'/' -f1)
            
            if [ -n "$port_pid" ]; then
                print_warning "Found process $port_pid on port 7777, killing..."
                kill -9 "$port_pid" 2>/dev/null || true
                sleep 1
                flask_stopped=true
                print_success "Process on port 7777 killed"
            fi
        fi
    fi
    
    if [ "$flask_stopped" = false ]; then
        print_info "No Flask service was running"
    fi
    
    echo ""
    
    # Stop Docker Agent if mode was docker
    if [ "$mode" = "docker" ]; then
        print_info "🐳 Stopping Docker agent..."
        stop_docker_agent
        echo ""
    fi
    
    # Final verification
    if command -v lsof &> /dev/null; then
        if lsof -ti:7777 &> /dev/null; then
            print_error "Failed to stop service on port 7777"
            print_info "You may need to manually kill processes: sudo lsof -ti:7777 | xargs kill -9"
            return 1
        fi
    fi
    
    echo "════════════════════════════════════════════════════════"
    print_success "✅ SEMUA SERVICE BERHASIL DIHENTIKAN!"
    
    return 0
}

# --- Command: restart ---
cmd_restart() {
    print_banner
    echo "🔄 RESTARTING AGENT SERVICE"
    echo "════════════════════════════════════════════════════════"
    echo ""
    
    local mode=$(get_saved_mode)
    print_info "Restarting dengan mode: $mode"
    echo ""
    
    # Stop all services
    cmd_stop
    
    echo ""
    sleep 2
    
    # Restart based on saved mode
    if [ "$mode" = "docker" ]; then
        print_info "Restarting dengan Docker agent..."
        echo ""
        
        # Start Flask
        start_flask_service
        
        if [ $? -eq 0 ]; then
            echo ""
            # Start Docker
            if check_docker_available; then
                start_docker_agent
                
                if [ $? -eq 0 ]; then
                    echo ""
                    echo "════════════════════════════════════════════════════════"
                    print_success "✅ RESTART SELESAI (Mode: Docker)"
                    echo ""
                    print_info "📍 URL Akses:"
                    print_info "  • http://localhost:7777"
                    print_info "  • http://komputerku.nour"
                else
                    print_warning "Docker agent gagal restart, Flask tetap jalan"
                fi
            else
                print_warning "Docker tidak tersedia, hanya Flask yang restart"
                save_mode "native"
            fi
        fi
    else
        print_info "Restarting mode native (Flask only)..."
        echo ""
        
        start_flask_service
        
        if [ $? -eq 0 ]; then
            echo ""
            echo "════════════════════════════════════════════════════════"
            print_success "✅ RESTART SELESAI (Mode: Native)"
            echo ""
            print_info "📍 URL Akses:"
            print_info "  • http://localhost:7777"
        fi
    fi
}

# --- Command: status ---
cmd_status() {
    print_banner
    echo "📊 AGENT SERVICE STATUS"
    echo "════════════════════════════════════════════════════════"
    echo ""
    
    local mode=$(get_saved_mode)
    print_info "Current mode: $mode"
    echo ""
    
    # Check Flask Service
    echo "🔹 Flask Service (Port 7777):"
    if [ -f "$PID_FILE" ]; then
        local pid=$(cat "$PID_FILE")
        
        if ps -p "$pid" > /dev/null 2>&1; then
            print_success "RUNNING (PID: $pid)"
            
            # Get process info
            echo ""
            echo "Process Info:"
            ps -p "$pid" -o pid,ppid,cmd,%cpu,%mem,etime
            
            # Check API health
            echo ""
            echo "API Health Check:"
            if curl -s "$API_URL/health" > /dev/null 2>&1; then
                local health=$(curl -s "$API_URL/health" | python3 -m json.tool 2>/dev/null)
                print_success "API is responding"
                echo "$health"
            else
                print_warning "API is not responding"
            fi
        else
            print_warning "STOPPED (stale PID file)"
            rm -f "$PID_FILE"
        fi
    else
        print_warning "STOPPED (no PID file)"
    fi
    
    echo ""
    
    # Check Docker Agent if mode is docker
    if [ "$mode" = "docker" ]; then
        echo "🔹 Docker Agent (Nginx):"
        if check_docker_available; then
            if docker ps | grep -q "agent_nginx"; then
                print_success "RUNNING"
                echo ""
                docker ps --filter "name=agent_nginx" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
                
                echo ""
                print_info "Testing endpoints..."
                if curl -s http://localhost/health > /dev/null 2>&1; then
                    print_success "HTTP endpoint responding"
                fi
                
                if curl -s http://komputerku.nour/health > /dev/null 2>&1; then
                    print_success "Virtual host working"
                fi
            else
                print_warning "STOPPED"
            fi
        else
            print_warning "Docker not available"
        fi
        echo ""
    fi
    
    echo "Configuration:"
    echo "  • Project Root: $PROJECT_ROOT"
    echo "  • Service File: $SERVICE_FILE"
    echo "  • Log File: $LOG_FILE"
    echo "  • API URL: $API_URL"
    echo "  • Mode: $mode"
}

# --- Command: logs ---
cmd_logs() {
    print_banner
    echo "📋 VIEWING LOGS"
    echo "════════════════════════════════════════════════════════"
    echo ""
    
    if [ -f "$LOG_FILE" ]; then
        print_info "Showing last 50 lines of logs..."
        print_info "Press Ctrl+C to exit"
        echo ""
        tail -f -n 50 "$LOG_FILE"
    else
        print_warning "Log file not found: $LOG_FILE"
        print_info "Service may not have been started yet"
    fi
}

# --- Command: help ---
cmd_help() {
    print_banner
    echo "📚 AVAILABLE COMMANDS"
    echo "════════════════════════════════════════════════════════"
    echo ""
    echo "Usage: ./agent.sh [command]"
    echo ""
    echo "Commands:"
    echo "  verify      - Verify all system dependencies"
    echo "  setup       - Setup system (install deps, register ag command)"
    echo "  setup-host  - Setup custom host (komputerku.nour)"
    echo "  start       - Start the agent service (with interactive mode)"
    echo "  stop        - Stop all running services"
    echo "  restart     - Restart with last used mode"
    echo "  status      - Show service status and mode"
    echo "  logs        - View service logs (tail -f)"
    echo "  help        - Show this help message"
    echo ""
    echo "Start Modes:"
    echo "  When you run './agent.sh start', you'll be asked:"
    echo "    [Y] With Docker   - Flask + Nginx reverse proxy"
    echo "    [N] Native only   - Flask only (no Docker)"
    echo ""
    echo "  • stop/restart will follow the mode you chose"
    echo "  • Mode is saved automatically"
    echo ""
    echo "Examples:"
    echo "  ./agent.sh verify       # Check system requirements"
    echo "  ./agent.sh setup        # One-time setup"
    echo "  ./agent.sh start        # Start service (interactive)"
    echo "  ./agent.sh status       # Check status & mode"
    echo "  ./agent.sh restart      # Restart with same mode"
    echo "  ag bantuan              # Use ag command (after setup)"
    echo ""
}

# --- Main Entry Point ---
main() {
    local command="${1:-help}"
    
    case "$command" in
        verify)
            cmd_verify
            ;;
        setup)
            cmd_setup
            ;;
        setup-host)
            cmd_setup_host
            ;;
        start)
            cmd_start
            ;;
        stop)
            cmd_stop
            ;;
        restart)
            cmd_restart
            ;;
        status)
            cmd_status
            ;;
        logs)
            cmd_logs
            ;;
        help|--help|-h)
            cmd_help
            ;;
        *)
            print_error "Unknown command: $command"
            echo ""
            cmd_help
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
