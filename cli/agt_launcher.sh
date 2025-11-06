#!/bin/bash
# AGT Launcher - CLI untuk Agent Pribadi dengan TTS Always-On
# Usage: agt "perintah" -> Selalu dengan TTS espeak

# --- Configuration ---
API_URL="http://localhost:7777/api/chat"
USE_TTS=true  # Always TRUE untuk agt

# --- Function: Speak ---
# Fungsi cross-platform untuk Text-to-Speech
speak() {
    local text="$1"
    
    # Hapus bullet points (•, *) dan format khusus agar TTS lebih natural
    CLEAN_TEXT=$(echo "$text" | sed 's/•//g' | sed 's/\*/ /g' | sed 's/─/ /g' | sed 's/│/ /g')
    
    # Deteksi OS dan panggil TTS tool yang sesuai
    if command -v espeak &> /dev/null; then
        # Linux - espeak with Indonesian voice
        # -v id = Indonesian voice (jika tersedia), fallback ke en-us
        # -s 150 = speed 150 words per minute
        # -a 100 = amplitude/volume
        espeak -v id -s 150 -a 100 "$CLEAN_TEXT" 2>/dev/null &
    elif command -v espeak-ng &> /dev/null; then
        # espeak-ng (newer version)
        espeak-ng -v id -s 150 "$CLEAN_TEXT" 2>/dev/null &
    elif command -v say &> /dev/null; then
        # macOS - say (built-in)
        say -r 180 "$CLEAN_TEXT" 2>/dev/null &
    elif command -v powershell.exe &> /dev/null; then
        # Windows WSL - PowerShell Speech
        powershell.exe -Command "Add-Type -AssemblyName System.Speech; (New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak('$CLEAN_TEXT')" 2>/dev/null &
    else
        echo "[WARNING: TTS tidak tersedia. Install: sudo apt install espeak espeak-ng]" >&2
    fi
}

# --- Command Parsing ---
# Gabungkan semua argumen menjadi satu command
COMMAND="$*"

# Validasi input
if [ -z "$COMMAND" ]; then
    echo "═══════════════════════════════════════════════════════════"
    echo "  AGT - Agent Pribadi dengan Text-to-Speech (TTS)"
    echo "═══════════════════════════════════════════════════════════"
    echo ""
    echo "Usage: agt <command>"
    echo ""
    echo "Perbedaan dengan 'ag':"
    echo "  • ag  : TTS optional (gunakan flag -v untuk voice)"
    echo "  • agt : TTS selalu aktif (default voice mode)"
    echo ""
    echo "Contoh:"
    echo "  agt cek ram"
    echo "  agt cek sistem"
    echo "  agt jam berapa"
    echo "  agt bantuan"
    echo ""
    echo "Note: Pastikan espeak terinstall untuk TTS"
    echo "      Install: sudo apt install espeak espeak-ng"
    echo "═══════════════════════════════════════════════════════════"
    exit 1
fi

# --- API Call ---
# Kirim request ke API Flask
RESPONSE=$(curl -s -X POST "$API_URL" \
    -H "Content-Type: application/json" \
    -d "{\"message\":\"$COMMAND\"}" 2>/dev/null)

# --- Error Checking and JSON Parsing ---

# Cek apakah curl gagal terhubung ke server
if [ $? -ne 0 ]; then
    ERROR_MSG="Error: Tidak dapat terhubung ke Agent Service. Pastikan server berjalan di $API_URL"
    echo "$ERROR_MSG"
    speak "Error. Tidak dapat terhubung ke Agent Service."
    exit 1
fi

# Gunakan jq untuk parsing JSON
MESSAGE=$(echo "$RESPONSE" | jq -r '.message' 2>/dev/null)
SUCCESS=$(echo "$RESPONSE" | jq -r '.success' 2>/dev/null)

# Cek kegagalan parsing atau kegagalan logika Agent
if [ -z "$MESSAGE" ] || [ "$MESSAGE" = "null" ] || [ "$SUCCESS" = "false" ]; then
    ERROR_MSG="Error: Agent Service gagal memproses command."
    echo "$ERROR_MSG"
    
    ERROR_DETAIL=$(echo "$RESPONSE" | jq -r '.message' 2>/dev/null)
    if [ "$ERROR_DETAIL" != "null" ]; then
        echo "Detail: $ERROR_DETAIL"
        speak "Error. $ERROR_DETAIL"
    else
        speak "Error. Agent Service gagal memproses command."
    fi
    exit 1
fi

# --- Output and TTS ---

# Tampilkan response di terminal dengan format yang lebih baik
echo "══════════════════════════════════════════════════════════════"
CLEAN_MESSAGE=$(echo "$MESSAGE" | sed 's/•/*/g')
echo "$CLEAN_MESSAGE"
echo "══════════════════════════════════════════════════════════════"

# TTS Always ON untuk agt
speak "$MESSAGE"

# Optional: Show speaker icon untuk indikasi TTS
echo "🔊 [TTS Active - Voice Output Enabled]"