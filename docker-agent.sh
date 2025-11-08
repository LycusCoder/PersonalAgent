#!/bin/bash
# ============================================================================
# DOCKER-AGENT.SH - Docker Management Script untuk Web Server Reverse Proxy
# ============================================================================
# Manage nginx/apache container untuk Agent Pribadi
# Author: Agent Pribadi Team
# Version: 2.0.0
# ============================================================================

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"
DOCKER_COMPOSE_FILE="$PROJECT_ROOT/docker-compose.yml"

# Default web server (can be overridden by parameter)
DEFAULT_WEBSERVER="nginx"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Helper Functions
get_webserver_display_name() {
    local webserver="$1"
    case "$webserver" in
        nginx) echo "Nginx" ;;
        apache) echo "Apache2" ;;
        *) echo "$webserver" ;;
    esac
}

print_banner() {
    local webserver="${1:-$DEFAULT_WEBSERVER}"
    local display_name=$(get_webserver_display_name "$webserver")
    
    echo -e "${BLUE}"
    echo "╔════════════════════════════════════════════════════════╗"
    echo "║       AGENT PRIBADI - DOCKER MANAGEMENT               ║"
    echo "║         $display_name Reverse Proxy Manager              ║"
    echo "╚════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

print_success() { echo -e "${GREEN}✅ $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
print_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }

# Check Docker Installation
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed!"
        print_info "Install Docker: https://docs.docker.com/get-docker/"
        exit 1
    fi
    
    if ! command -v docker compose &> /dev/null && ! docker compose version &> /dev/null 2>&1; then
        print_error "Docker Compose is not installed!"
        print_info "Install Docker Compose: https://docs.docker.com/compose/install/"
        exit 1
    fi
}

# Command: build
cmd_build() {
    print_banner
    echo "🔨 BUILDING NGINX DOCKER IMAGE"
    echo "═══════════════════════════════════════════════════════════"
    echo ""
    
    check_docker
    
    print_info "Building nginx image from Dockerfile.nginx..."
    docker compose -f "$DOCKER_COMPOSE_FILE" build --no-cache
    
    print_success "Nginx image built successfully!"
    print_info "Next: Run './docker-agent.sh start' to start nginx"
}

# Command: start
cmd_start() {
    print_banner
    echo "🚀 STARTING NGINX REVERSE PROXY"
    echo "═══════════════════════════════════════════════════════════"
    echo ""
    
    check_docker
    
    # Check if Agent Service is running on host
    print_info "Checking if Agent Service is running on host:7777..."
    if curl -s http://localhost:7777/health > /dev/null 2>&1; then
        print_success "Agent Service is running!"
    else
        print_warning "Agent Service is NOT running on port 7777!"
        print_info "Please start it first: ./agent.sh start"
        read -p "Do you want to continue anyway? [y/N]: " -n 1 -r
        echo ""
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
    
    print_info "Starting nginx container..."
    docker compose -f "$DOCKER_COMPOSE_FILE" up -d
    
    sleep 2
    
    if docker ps | grep -q agent_nginx; then
        print_success "Nginx container started successfully!"
        echo ""
        print_info "Access URLs:"
        print_info "  • http://komputerku.nour (virtual host)"
        print_info "  • http://localhost (direct)"
        print_info "  • http://127.0.0.1 (IP)"
        echo ""
        print_info "Test: curl http://komputerku.nour/health"
    else
        print_error "Failed to start nginx container"
        print_info "Check logs: ./docker-agent.sh logs"
    fi
}

# Command: stop
cmd_stop() {
    print_banner
    echo "🛑 STOPPING NGINX REVERSE PROXY"
    echo "═══════════════════════════════════════════════════════════"
    echo ""
    
    check_docker
    
    print_info "Stopping nginx container..."
    docker compose -f "$DOCKER_COMPOSE_FILE" down
    
    print_success "Nginx container stopped!"
}

# Command: restart
cmd_restart() {
    print_banner
    echo "🔄 RESTARTING NGINX REVERSE PROXY"
    echo "═══════════════════════════════════════════════════════════"
    echo ""
    
    cmd_stop
    sleep 2
    cmd_start
}

# Command: status
cmd_status() {
    print_banner
    echo "📊 NGINX CONTAINER STATUS"
    echo "═══════════════════════════════════════════════════════════"
    echo ""
    
    check_docker
    
    if docker ps | grep -q agent_nginx; then
        print_success "Nginx container is RUNNING"
        echo ""
        docker ps --filter "name=agent_nginx" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
        
        echo ""
        print_info "Testing endpoints..."
        
        if curl -s http://localhost/health > /dev/null 2>&1; then
            print_success "HTTP endpoint is responding"
        else
            print_warning "HTTP endpoint is NOT responding"
        fi
        
        if curl -s http://komputerku.nour/health > /dev/null 2>&1; then
            print_success "Virtual host is working"
        else
            print_warning "Virtual host is NOT working (check /etc/hosts)"
        fi
    else
        print_warning "Nginx container is STOPPED"
    fi
    
    echo ""
    print_info "Agent Service Status:"
    if curl -s http://localhost:7777/health > /dev/null 2>&1; then
        print_success "Agent Service is running on port 7777"
    else
        print_warning "Agent Service is NOT running on port 7777"
    fi
}

# Command: logs
cmd_logs() {
    print_banner
    echo "📋 VIEWING NGINX LOGS"
    echo "═══════════════════════════════════════════════════════════"
    echo ""
    
    check_docker
    
    print_info "Showing nginx container logs (Ctrl+C to exit)..."
    echo ""
    docker compose -f "$DOCKER_COMPOSE_FILE" logs -f nginx
}

# Command: test
cmd_test() {
    print_banner
    echo "🧪 TESTING NGINX CONFIGURATION"
    echo "═══════════════════════════════════════════════════════════"
    echo ""
    
    check_docker
    
    print_info "Testing nginx configuration..."
    
    if docker ps | grep -q agent_nginx; then
        docker exec agent_nginx nginx -t
        print_success "Nginx configuration is valid!"
    else
        print_warning "Nginx container is not running"
        print_info "Building and testing configuration..."
        docker run --rm -v "$PROJECT_ROOT/nginx/agent.conf:/etc/nginx/conf.d/agent.conf" nginx:1.25.4-alpine nginx -t
    fi
}

# Command: help
cmd_help() {
    print_banner
    echo "📚 AVAILABLE COMMANDS"
    echo "═══════════════════════════════════════════════════════════"
    echo ""
    echo "Usage: ./docker-agent.sh [command]"
    echo ""
    echo "Commands:"
    echo "  build       - Build nginx Docker image"
    echo "  start       - Start nginx container (reverse proxy)"
    echo "  stop        - Stop nginx container"
    echo "  restart     - Restart nginx container"
    echo "  status      - Show container and endpoint status"
    echo "  logs        - View nginx logs (tail -f)"
    echo "  test        - Test nginx configuration"
    echo "  help        - Show this help message"
    echo ""
    echo "Workflow:"
    echo "  1. ./agent.sh start           # Start Agent Service (port 7777)"
    echo "  2. ./docker-agent.sh build    # Build nginx image (first time)"
    echo "  3. ./docker-agent.sh start    # Start nginx proxy (port 80)"
    echo "  4. curl http://komputerku.nour/health  # Test!"
    echo ""
}

# Main Entry Point
main() {
    local command="${1:-help}"
    
    case "$command" in
        build)
            cmd_build
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
        test)
            cmd_test
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

main "$@"