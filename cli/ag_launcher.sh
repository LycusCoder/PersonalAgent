#!/bin/bash
# AG Launcher - CLI untuk Agent Pribadi
# Usage: 
#   ag "perintah"        -> Tanpa TTS
#   ag -v "perintah"     -> Dengan TTS (voice)

# Konfigurasi
API_URL="http://localhost:7777/api/chat"
USE_TTS=false

# Parse arguments
if [ "$1" = "-v" ]; then
    USE_TTS=true
    shift  # Remove -v from arguments
fi

# Gabungkan semua argumen menjadi satu command
COMMAND="$*"

# Validasi input
if [ -z "$COMMAND" ]; then
    echo "Usage: ag [-v] <command>"
    echo "  -v    Enable Text-to-Speech"
    echo ""
    echo "Examples:"
    echo "  ag cek ram"
    echo "  ag -v cek sistem"
    exit 1
fi

# Kirim request ke API
RESPONSE=$(curl -s -X POST "$API_URL" \
    -H "Content-Type: application/json" \
    -d "{\"message\":\"$COMMAND\"}" 2>/dev/null)

# Cek apakah curl berhasil
if [ $? -ne 0 ]; then
    echo "Error: Tidak dapat terhubung ke Agent Service."
    echo "Pastikan server berjalan di port 7777"
    exit 1
fi

# Parse response (extract message field)
MESSAGE=$(echo "$RESPONSE" | grep -o '"message":"[^"]*"' | sed 's/"message":"//;s/"$//' | sed 's/\\n/\n/g')

# Tampilkan response
if [ -n "$MESSAGE" ]; then
    echo "$MESSAGE"
    
    # TTS jika diminta
    if [ "$USE_TTS" = true ]; then
        # Detect OS dan gunakan TTS yang sesuai
        if command -v espeak &> /dev/null; then
            # Linux - espeak
            echo "$MESSAGE" | espeak 2>/dev/null
        elif command -v say &> /dev/null; then
            # macOS - say
            echo "$MESSAGE" | say
        elif command -v powershell.exe &> /dev/null; then
            # Windows (WSL) - PowerShell Speech
            powershell.exe -Command "Add-Type -AssemblyName System.Speech; (New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak('$MESSAGE')" 2>/dev/null
        else
            echo "[TTS tidak tersedia di sistem ini]"
        fi
    fi
else
    echo "Error: Tidak dapat memproses response dari server"
    echo "Raw response: $RESPONSE"
    exit 1
fi
