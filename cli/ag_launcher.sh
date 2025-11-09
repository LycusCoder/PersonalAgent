#!/bin/bash
# AG Launcher - CLI untuk Agent Pribadi
# Usage: 
#   ag "perintah"        -> Tanpa TTS (mode default)
#   ag -v "perintah"     -> Dengan TTS (voice)

# --- Configuration ---
API_URL="http://localhost:7777/api/chat"
USE_TTS=false

# --- Function: Speak ---
# Fungsi cross-platform untuk Text-to-Speech
speak() {
    local text="$1"
    
    # Hapus bullet points (•, *) agar espeak tidak membacanya
    CLEAN_TEXT=$(echo "$text" | sed 's/•//g' | sed 's/\*/ /g')
    
    # Deteksi OS dan panggil TTS tool yang sesuai
    if command -v espeak &> /dev/null; then
        # Linux - espeak
        espeak -v en-us -s 140 "$CLEAN_TEXT" 2>/dev/null &
    elif command -v say &> /dev/null; then
        # macOS - say
        say "$CLEAN_TEXT" 2>/dev/null &
    elif command -v powershell.exe &> /dev/null; then
        # Windows (WSL) - PowerShell Speech
        powershell.exe -Command "Add-Type -AssemblyName System.Speech; (New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak('$CLEAN_TEXT')" 2>/dev/null &
    else
        echo "[INFO: TTS tidak tersedia atau tidak dikonfigurasi di sistem ini.]" >&2
    fi
}


# --- Command Parsing ---
# Parse arguments
if [ "$1" = "-v" ]; then
    USE_TTS=true
    shift  # Hapus -v dari argumen
fi

# Gabungkan semua argumen menjadi satu command
COMMAND="$*"

# Jika user ingin membuka web UI: ag --ui | ag -w | ag ui
if [ "$COMMAND" = "--ui" ] || [ "$COMMAND" = "-w" ] || [ "$COMMAND" = "ui" ] || [ "$COMMAND" = "open-ui" ]; then
    URL="http://localhost:7777"
    echo "Opening web dashboard at $URL"
    if command -v xdg-open &> /dev/null; then
        xdg-open "$URL" >/dev/null 2>&1 &
    elif command -v gnome-open &> /dev/null; then
        gnome-open "$URL" >/dev/null 2>&1 &
    elif command -v open &> /dev/null; then
        open "$URL" >/dev/null 2>&1 &
    else
        # Fallback to python webbrowser
        python3 -m webbrowser "$URL" >/dev/null 2>&1 &
    fi
    exit 0
fi

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


# --- API Call ---
# Kirim request ke API Flask
RESPONSE=$(curl -s -X POST "$API_URL" \
    -H "Content-Type: application/json" \
    -d "{\"message\":\"$COMMAND\"}" 2>/dev/null)


# --- Error Checking and JSON Parsing (KUNCI PERBAIKAN) ---

# Cek apakah curl gagal terhubung ke server (Error Code != 0)
if [ $? -ne 0 ]; then
    echo "Error: Tidak dapat terhubung ke Agent Service."
    echo "Pastikan server berjalan di $API_URL"
    exit 1
fi

# 🚨 Perbaikan 1: Gunakan jq untuk parsing yang kokoh
# Ambil field 'message' dari JSON. jq -r memastikan string di-unescape (misal: \n menjadi newline)
MESSAGE=$(echo "$RESPONSE" | jq -r '.message' 2>/dev/null)
SUCCESS=$(echo "$RESPONSE" | jq -r '.success' 2>/dev/null)
RAW_RESPONSE=$(echo "$RESPONSE" | jq '.' 2>/dev/null) # Formatting raw response untuk debug

# Cek kegagalan parsing atau kegagalan logika Agent
if [ -z "$MESSAGE" ] || [ "$MESSAGE" = "null" ] || [ "$SUCCESS" = "false" ]; then
    echo "Error: Agent Service gagal memproses command."
    echo "Detail:"
    # Tampilkan pesan error dari Agent atau respons mentah jika Agent tidak memberikan pesan
    ERROR_MESSAGE=$(echo "$RESPONSE" | jq -r '.message' 2>/dev/null)
    if [ "$ERROR_MESSAGE" != "null" ]; then
        echo "$ERROR_MESSAGE"
    else
        echo "Raw Response: $RAW_RESPONSE"
    fi
    exit 1
fi

# --- Output and TTS ---

# Tampilkan response di terminal
# Perbaikan 2: Hapus bullet point dari output terminal (•) agar rapi
CLEAN_MESSAGE=$(echo "$MESSAGE" | sed 's/•/\*/g')
echo "$CLEAN_MESSAGE"

# TTS jika diminta
if [ "$USE_TTS" = true ]; then
    speak "$MESSAGE"
fi