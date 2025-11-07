#!/bin/bash
# ============================================================================
# DOCKER SETUP HYBRID - Setup Docker dengan Nginx/Apache + MySQL
# ============================================================================
# Script ini akan:
# 1. Download web server (Nginx/Apache) dan database (MySQL) dari packages.yaml
# 2. Validasi file yang sudah ada di bin/ (skip jika valid)
# 3. Extract dan setup ke bin/{app}/{version}/
# 4. Generate Dockerfile hybrid
# 5. Build Docker image
# ============================================================================

set -e

# --- Configuration ---
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BIN_DIR="$PROJECT_ROOT/bin"
CONFIG_DIR="$PROJECT_ROOT/config"
PACKAGES_YAML="$CONFIG_DIR/tools/packages.yaml"
TEMP_DIR="/tmp/agent_docker_setup"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# --- Helper Functions ---

print_banner() {
    echo -e "${CYAN}"
    echo "╔════════════════════════════════════════════════════════╗"
    echo "║       DOCKER HYBRID SETUP - Nginx/Apache + MySQL      ║"
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

print_step() {
    echo -e "${CYAN}▶ $1${NC}"
}

# --- Parse YAML Function ---
parse_yaml_url() {
    local app="$1"
    local version="$2"
    
    # Simple YAML parser using awk
    local url=$(awk -v app="$app" -v ver="$version" '
        /^[a-z]/ { current_app = $1; gsub(/:/, "", current_app) }
        current_app == app && $1 == ver":" { print $2 }
    ' "$PACKAGES_YAML")
    
    echo "$url"
}

# --- Get Latest Version from YAML ---
get_latest_version() {
    local app="$1"
    
    # Get the first version listed (assumed to be latest)
    local version=$(awk -v app="$app" '
        /^[a-z]/ { current_app = $1; gsub(/:/, "", current_app) }
        current_app == app && /^  [0-9]/ { 
            gsub(/:/, "", $1)
            print $1
            exit
        }
    ' "$PACKAGES_YAML")
    
    echo "$version"
}

# --- List Available Versions ---
list_versions() {
    local app="$1"
    
    awk -v app="$app" '
        /^[a-z]/ { current_app = $1; gsub(/:/, "", current_app) }
        current_app == app && /^  [0-9]/ { 
            gsub(/:/, "", $1)
            print $1
        }
    ' "$PACKAGES_YAML"
}

# --- Validate File Integrity ---
validate_file() {
    local filepath="$1"
    
    if [ ! -f "$filepath" ]; then
        return 1
    fi
    
    # Check file size (should be > 1KB)
    local filesize=$(stat -f%z "$filepath" 2>/dev/null || stat -c%s "$filepath" 2>/dev/null)
    if [ "$filesize" -lt 1024 ]; then
        print_warning "File too small (corrupt): $filepath"
        return 1
    fi
    
    # Check file type based on extension
    local filename=$(basename "$filepath")
    local extension="${filename##*.}"
    
    case "$extension" in
        tar.gz|tgz)
            if tar -tzf "$filepath" &> /dev/null; then
                return 0
            else
                print_warning "Invalid tar.gz archive: $filepath"
                return 1
            fi
            ;;
        tar.xz|txz)
            if tar -tJf "$filepath" &> /dev/null; then
                return 0
            else
                print_warning "Invalid tar.xz archive: $filepath"
                return 1
            fi
            ;;
        zip)
            if command -v unzip &> /dev/null; then
                if unzip -t "$filepath" &> /dev/null; then
                    return 0
                else
                    print_warning "Invalid zip archive: $filepath"
                    return 1
                fi
            else
                # If unzip not available, assume valid
                return 0
            fi
            ;;
        *)
            # Unknown extension, assume valid
            return 0
            ;;
    esac
}

# --- Check if App Version Exists and is Valid ---
check_existing_install() {
    local app="$1"
    local version="$2"
    local install_dir="$BIN_DIR/$app/$version"
    
    if [ -d "$install_dir" ]; then
        # Check if directory has files
        if [ -n "$(ls -A "$install_dir" 2>/dev/null)" ]; then
            # Check for key files depending on app
            case "$app" in
                nginx)
                    if [ -f "$install_dir/sbin/nginx" ] || [ -f "$install_dir/nginx" ]; then
                        return 0
                    fi
                    ;;
                apache)
                    if [ -f "$install_dir/bin/httpd" ] || [ -f "$install_dir/httpd" ]; then
                        return 0
                    fi
                    ;;
                mysql)
                    if [ -f "$install_dir/bin/mysqld" ] || [ -d "$install_dir/bin" ]; then
                        return 0
                    fi
                    ;;
                *)
                    # For other apps, just check if directory is not empty
                    return 0
                    ;;
            esac
        fi
    fi
    
    return 1
}

# --- Download File ---
download_file() {
    local url="$1"
    local output_file="$2"
    local app_name="$3"
    
    print_info "Downloading $app_name..."
    print_info "URL: $url"
    
    # Create temp directory
    mkdir -p "$(dirname "$output_file")"
    
    # Download with progress
    if command -v wget &> /dev/null; then
        wget -q --show-progress -O "$output_file" "$url"
    elif command -v curl &> /dev/null; then
        curl -L --progress-bar -o "$output_file" "$url"
    else
        print_error "Neither wget nor curl available!"
        return 1
    fi
    
    if [ $? -eq 0 ]; then
        print_success "Downloaded successfully"
        return 0
    else
        print_error "Download failed"
        return 1
    fi
}

# --- Extract Archive ---
extract_archive() {
    local archive_file="$1"
    local target_dir="$2"
    local app_name="$3"
    
    print_info "Extracting $app_name..."
    
    # Create target directory
    mkdir -p "$target_dir"
    
    local filename=$(basename "$archive_file")
    local extension="${filename##*.}"
    
    case "$extension" in
        gz)
            if [[ "$filename" == *.tar.gz ]] || [[ "$filename" == *.tgz ]]; then
                tar -xzf "$archive_file" -C "$target_dir" --strip-components=1 2>/dev/null || \
                tar -xzf "$archive_file" -C "$target_dir" 2>/dev/null
            fi
            ;;
        xz)
            if [[ "$filename" == *.tar.xz ]] || [[ "$filename" == *.txz ]]; then
                tar -xJf "$archive_file" -C "$target_dir" --strip-components=1 2>/dev/null || \
                tar -xJf "$archive_file" -C "$target_dir" 2>/dev/null
            fi
            ;;
        zip)
            if command -v unzip &> /dev/null; then
                unzip -q "$archive_file" -d "$target_dir"
            fi
            ;;
        *)
            print_error "Unsupported archive format: $extension"
            return 1
            ;;
    esac
    
    if [ $? -eq 0 ]; then
        print_success "Extracted successfully"
        return 0
    else
        print_error "Extraction failed"
        return 1
    fi
}

# --- Install Package ---
install_package() {
    local app="$1"
    local version="$2"
    
    echo ""
    print_step "Installing $app $version..."
    
    # Check if already installed and valid
    if check_existing_install "$app" "$version"; then
        print_success "$app $version already installed at bin/$app/$version/"
        print_info "Skipping download (files validated)"
        return 0
    fi
    
    # Get download URL
    local url=$(parse_yaml_url "$app" "$version")
    
    if [ -z "$url" ]; then
        print_error "URL not found for $app $version in packages.yaml"
        return 1
    fi
    
    # Prepare paths
    local filename=$(basename "$url")
    local download_file="$TEMP_DIR/$filename"
    local install_dir="$BIN_DIR/$app/$version"
    
    # Check if download file exists and is valid
    if [ -f "$download_file" ]; then
        print_info "Found cached download: $filename"
        if validate_file "$download_file"; then
            print_success "Cached file is valid"
        else
            print_warning "Cached file is corrupt, re-downloading..."
            rm -f "$download_file"
        fi
    fi
    
    # Download if needed
    if [ ! -f "$download_file" ]; then
        if ! download_file "$url" "$download_file" "$app"; then
            return 1
        fi
        
        # Validate downloaded file
        if ! validate_file "$download_file"; then
            print_error "Downloaded file is corrupt!"
            rm -f "$download_file"
            return 1
        fi
    fi
    
    # Extract
    if ! extract_archive "$download_file" "$install_dir" "$app"; then
        return 1
    fi
    
    print_success "$app $version installed successfully!"
    return 0
}

# --- Generate Dockerfile ---
generate_dockerfile() {
    local webserver="$1"
    local webserver_version="$2"
    local database="$3"
    local database_version="$4"
    
    local dockerfile="$PROJECT_ROOT/Dockerfile.hybrid"
    
    print_step "Generating Dockerfile..."
    
    cat > "$dockerfile" << EOF
# ============================================================================
# Dockerfile Hybrid - $webserver + $database
# Auto-generated by docker_setup_hybrid.sh
# ============================================================================

FROM ubuntu:22.04

# Install dependencies
RUN apt-get update && apt-get install -y \\
    build-essential \\
    libpcre3 libpcre3-dev \\
    zlib1g zlib1g-dev \\
    libssl-dev \\
    libgd-dev \\
    libgeoip-dev \\
    libxml2-dev \\
    libxslt1-dev \\
    libaio1 \\
    libncurses5-dev \\
    wget \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

# Copy binaries from host
COPY bin/$webserver/$webserver_version /opt/$webserver
COPY bin/$database/$database_version /opt/$database

# Setup $webserver
WORKDIR /opt/$webserver
EOF

    if [ "$webserver" = "nginx" ]; then
        cat >> "$dockerfile" << 'EOF'

# Configure and compile Nginx (if source)
RUN if [ -f "configure" ]; then \
        ./configure \
            --prefix=/opt/nginx \
            --with-http_ssl_module \
            --with-http_v2_module \
            --with-http_realip_module \
            --with-http_gzip_static_module && \
        make && make install; \
    fi

# Copy nginx config
COPY nginx/agent.conf /opt/nginx/conf/nginx.conf

EXPOSE 80 443

# Start Nginx
CMD ["/opt/nginx/sbin/nginx", "-g", "daemon off;"]
EOF
    else
        cat >> "$dockerfile" << 'EOF'

# Configure and compile Apache (if source)
RUN if [ -f "configure" ]; then \
        ./configure \
            --prefix=/opt/apache \
            --enable-ssl \
            --enable-so \
            --enable-rewrite && \
        make && make install; \
    fi

EXPOSE 80 443

# Start Apache
CMD ["/opt/apache/bin/httpd", "-D", "FOREGROUND"]
EOF
    fi
    
    print_success "Dockerfile generated: $dockerfile"
}

# --- Build Docker Image ---
build_docker_image() {
    local webserver="$1"
    local image_name="agent_${webserver}_hybrid"
    
    print_step "Building Docker image: $image_name..."
    
    cd "$PROJECT_ROOT"
    
    if docker build -f Dockerfile.hybrid -t "$image_name:latest" .; then
        print_success "Docker image built successfully!"
        print_info "Image: $image_name:latest"
        return 0
    else
        print_error "Failed to build Docker image"
        return 1
    fi
}

# --- Main Setup Flow ---
main() {
    print_banner
    echo ""
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed!"
        print_info "Install Docker: curl -fsSL https://get.docker.com | sh"
        exit 1
    fi
    
    if ! docker info &> /dev/null 2>&1; then
        print_error "Docker daemon is not running!"
        print_info "Start Docker: sudo systemctl start docker"
        exit 1
    fi
    
    # Check packages.yaml
    if [ ! -f "$PACKAGES_YAML" ]; then
        print_error "packages.yaml not found at $CONFIG_DIR/tools/"
        exit 1
    fi
    
    print_success "Docker is ready"
    echo ""
    
    # === WEB SERVER SELECTION ===
    echo "════════════════════════════════════════════════════════"
    echo "🌐 PILIH WEB SERVER:"
    echo "════════════════════════════════════════════════════════"
    echo ""
    echo "  [1] Nginx (recommended - ringan & cepat)"
    echo "  [2] Apache2 (kompatibilitas tinggi)"
    echo ""
    read -p "Pilihan [1/2]: " webserver_choice
    
    case "$webserver_choice" in
        1)
            WEBSERVER="nginx"
            ;;
        2)
            WEBSERVER="apache"
            ;;
        *)
            print_error "Pilihan tidak valid!"
            exit 1
            ;;
    esac
    
    echo ""
    print_info "Web Server: $WEBSERVER"
    
    # Get available versions
    print_info "Available versions:"
    list_versions "$WEBSERVER" | while read ver; do
        echo "  • $ver"
    done
    
    # Get latest version
    WEBSERVER_VERSION=$(get_latest_version "$WEBSERVER")
    
    echo ""
    read -p "Enter version (default: $WEBSERVER_VERSION): " custom_version
    if [ -n "$custom_version" ]; then
        WEBSERVER_VERSION="$custom_version"
    fi
    
    echo ""
    print_success "Selected: $WEBSERVER $WEBSERVER_VERSION"
    
    # === DATABASE SELECTION ===
    echo ""
    echo "════════════════════════════════════════════════════════"
    echo "🗄️  PILIH DATABASE:"
    echo "════════════════════════════════════════════════════════"
    echo ""
    echo "  [1] MySQL (popular & reliable)"
    echo "  [2] PostgreSQL (advanced features)"
    echo "  [3] MongoDB (NoSQL)"
    echo "  [4] Skip (tidak perlu database)"
    echo ""
    read -p "Pilihan [1/2/3/4]: " database_choice
    
    case "$database_choice" in
        1)
            DATABASE="mysql"
            ;;
        2)
            DATABASE="postgresql"
            ;;
        3)
            DATABASE="mongodb"
            ;;
        4)
            DATABASE="none"
            ;;
        *)
            print_error "Pilihan tidak valid!"
            exit 1
            ;;
    esac
    
    if [ "$DATABASE" != "none" ]; then
        echo ""
        print_info "Database: $DATABASE"
        
        # Get available versions
        print_info "Available versions:"
        list_versions "$DATABASE" | while read ver; do
            echo "  • $ver"
        done
        
        # Get latest version
        DATABASE_VERSION=$(get_latest_version "$DATABASE")
        
        echo ""
        read -p "Enter version (default: $DATABASE_VERSION): " custom_db_version
        if [ -n "$custom_db_version" ]; then
            DATABASE_VERSION="$custom_db_version"
        fi
        
        echo ""
        print_success "Selected: $DATABASE $DATABASE_VERSION"
    else
        print_info "Skipping database installation"
    fi
    
    # === CONFIRMATION ===
    echo ""
    echo "════════════════════════════════════════════════════════"
    echo "📋 SUMMARY:"
    echo "════════════════════════════════════════════════════════"
    echo "  • Web Server: $WEBSERVER $WEBSERVER_VERSION"
    if [ "$DATABASE" != "none" ]; then
        echo "  • Database: $DATABASE $DATABASE_VERSION"
    fi
    echo "  • Install Path: $BIN_DIR"
    echo ""
    read -p "Lanjutkan instalasi? [Y/n]: " confirm
    
    if [[ ! $confirm =~ ^[Yy]$ ]] && [ -n "$confirm" ]; then
        print_warning "Installation cancelled"
        exit 0
    fi
    
    # === INSTALLATION ===
    echo ""
    echo "════════════════════════════════════════════════════════"
    echo "🚀 STARTING INSTALLATION"
    echo "════════════════════════════════════════════════════════"
    
    # Create temp directory
    mkdir -p "$TEMP_DIR"
    mkdir -p "$BIN_DIR"
    
    # Install web server
    if ! install_package "$WEBSERVER" "$WEBSERVER_VERSION"; then
        print_error "Failed to install $WEBSERVER"
        exit 1
    fi
    
    # Install database
    if [ "$DATABASE" != "none" ]; then
        if ! install_package "$DATABASE" "$DATABASE_VERSION"; then
            print_error "Failed to install $DATABASE"
            exit 1
        fi
    fi
    
    # Generate Dockerfile
    echo ""
    if [ "$DATABASE" != "none" ]; then
        generate_dockerfile "$WEBSERVER" "$WEBSERVER_VERSION" "$DATABASE" "$DATABASE_VERSION"
    else
        generate_dockerfile "$WEBSERVER" "$WEBSERVER_VERSION" "none" "none"
    fi
    
    # Build Docker image
    echo ""
    echo "════════════════════════════════════════════════════════"
    echo "🐳 BUILDING DOCKER IMAGE"
    echo "════════════════════════════════════════════════════════"
    echo ""
    read -p "Build Docker image now? [Y/n]: " build_confirm
    
    if [[ $build_confirm =~ ^[Yy]$ ]] || [ -z "$build_confirm" ]; then
        if ! build_docker_image "$WEBSERVER"; then
            print_warning "Docker build failed, but files are installed"
            print_info "You can build manually later with: docker build -f Dockerfile.hybrid -t agent_${WEBSERVER}_hybrid ."
        fi
    else
        print_info "Skipping Docker build"
        print_info "Build later with: docker build -f Dockerfile.hybrid -t agent_${WEBSERVER}_hybrid ."
    fi
    
    # Cleanup temp files (optional)
    echo ""
    read -p "Cleanup temporary download files? [Y/n]: " cleanup_confirm
    if [[ $cleanup_confirm =~ ^[Yy]$ ]] || [ -z "$cleanup_confirm" ]; then
        rm -rf "$TEMP_DIR"
        print_success "Temporary files cleaned"
    fi
    
    # Final summary
    echo ""
    echo "════════════════════════════════════════════════════════"
    print_success "✅ SETUP COMPLETED!"
    echo "════════════════════════════════════════════════════════"
    echo ""
    print_info "Installed files:"
    print_info "  • $BIN_DIR/$WEBSERVER/$WEBSERVER_VERSION/"
    if [ "$DATABASE" != "none" ]; then
        print_info "  • $BIN_DIR/$DATABASE/$DATABASE_VERSION/"
    fi
    echo ""
    print_info "Next steps:"
    print_info "  1. Verify: ./agent.sh verify-docker"
    print_info "  2. Start: ./agent.sh start"
    print_info "  3. Choose Docker mode when prompted"
    echo ""
}

# Run main
main "$@"
