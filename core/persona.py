"""Modul Persona untuk Agent Pribadi (AG)

Mengelola konsistensi gaya bicara, sapaan, dan format response
dengan karakter Sekretaris Sarah yang formal, profesional, dan hangat.
"""

from datetime import datetime
from config.settings import PERSONA_NAME, MASTER_NAME


def get_greeting_time() -> str:
    """Mendapatkan sapaan berdasarkan waktu saat ini.
    
    Returns:
        str: Sapaan yang sesuai dengan waktu (Pagi/Siang/Sore/Malam)
    """
    hour = datetime.now().hour
    
    if 5 <= hour < 11:
        return "Selamat pagi"
    elif 11 <= hour < 15:
        return "Selamat siang"
    elif 15 <= hour < 18:
        return "Selamat sore"
    else:
        return "Selamat malam"


def get_greeting() -> str:
    """Mendapatkan sapaan lengkap dengan nama master.
    
    Returns:
        str: Sapaan lengkap (contoh: "Selamat pagi, Tuan Affif")
    """
    return f"{get_greeting_time()}, {MASTER_NAME}"


def format_response(message: str, include_greeting: bool = False) -> str:
    """Format response dengan gaya persona Sarah.
    
    Args:
        message: Pesan utama yang akan disampaikan
        include_greeting: Apakah perlu menyertakan sapaan di awal
    
    Returns:
        str: Response yang sudah diformat dengan persona
    """
    if include_greeting:
        return f"{get_greeting()}. {message}"
    return message


def format_error_response(error_message: str) -> str:
    """Format response untuk error dengan gaya yang sopan.
    
    Args:
        error_message: Pesan error
    
    Returns:
        str: Error response yang sudah diformat
    """
    return f"Mohon maaf, {MASTER_NAME}. {error_message}"


def format_unknown_command() -> str:
    """Response standar untuk command yang tidak dikenali.
    
    Returns:
        str: Response untuk unknown command
    """
    return (
        f"Mohon maaf, {MASTER_NAME}. Saya belum memahami perintah tersebut. "
        "Silakan coba perintah lain seperti: 'cek ram', 'cek cpu', 'cek gpu', "
        "'cek sistem', atau 'bantuan'."
    )


def get_current_time_response() -> str:
    """Response untuk menampilkan waktu saat ini.
    
    Returns:
        str: Response dengan waktu saat ini
    """
    now = datetime.now()
    time_str = now.strftime("%H:%M:%S")
    date_str = now.strftime("%d %B %Y")
    day_str = now.strftime("%A")
    
    # Translate day to Indonesian
    days_id = {
        'Monday': 'Senin',
        'Tuesday': 'Selasa',
        'Wednesday': 'Rabu',
        'Thursday': 'Kamis',
        'Friday': 'Jumat',
        'Saturday': 'Sabtu',
        'Sunday': 'Minggu'
    }
    day_str = days_id.get(day_str, day_str)
    
    return (
        f"{get_greeting()}. Saat ini pukul {time_str}, "
        f"{day_str}, {date_str}."
    )
