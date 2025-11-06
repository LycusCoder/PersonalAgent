#!/bin/bash
# SETUP HOSTS - Script untuk menambahkan custom domain AG ke /etc/hosts

TARGET_HOSTS_FILE="/etc/hosts"
DOMAIN_NAME="komputerku.nour"
IP_ADDRESS="127.0.0.1"
HOST_ENTRY="$IP_ADDRESS\t$DOMAIN_NAME"

echo "--- Setup Custom Host Agent Pribadi ---"
echo "Target: $DOMAIN_NAME -> $IP_ADDRESS"

# Cek apakah entri sudah ada di file hosts
if grep -q "$DOMAIN_NAME" "$TARGET_HOSTS_FILE"; then
    echo "✅ Entri $DOMAIN_NAME sudah ditemukan di $TARGET_HOSTS_FILE. Tidak ada perubahan yang dilakukan."
else
    echo "Menambahkan entri ke $TARGET_HOSTS_FILE..."
    
    # Tambahkan entri. Perintah ini membutuhkan izin sudo!
    echo "$HOST_ENTRY" | sudo tee -a "$TARGET_HOSTS_FILE" > /dev/null
    
    # Cek status penulisan
    if [ $? -eq 0 ]; then
        echo "✅ Entri berhasil ditambahkan. Anda dapat mengakses dashboard melalui http://$DOMAIN_NAME:7777"
    else
        echo "❌ Gagal menambahkan entri. Pastikan Anda menjalankan script ini dengan sudo."
    fi
fi