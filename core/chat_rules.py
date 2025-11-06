"""Modul Chat Rules untuk Agent Pribadi (AG)

Otak rule-based yang menerjemahkan prompt user ke fungsi sistem yang tepat.
Tidak menggunakan LLM - murni if-elif-else untuk stabilitas 100%.
"""

from typing import Dict, Any
from core.persona import (
    format_response,
    format_unknown_command,
    get_current_time_response,
    get_greeting,
    MASTER_NAME
)
from core.system_monitor import (
    get_ram_status,
    get_cpu_status,
    get_gpu_status,
    get_system_summary
)


def process_command(user_input: str) -> Dict[str, Any]:
    """Memproses command user dengan rule-based logic.
    
    Args:
        user_input: Input dari user (string command)
    
    Returns:
        dict: {
            'success': bool,
            'message': str,
            'data': dict (optional),
            'command_type': str
        }
    """
    # Normalize input
    user_input = user_input.lower().strip()
    
    # Rule 1: Sapaan / Greeting
    if any(word in user_input for word in ['halo', 'hai', 'hello', 'hi']):
        return {
            'success': True,
            'message': f"{get_greeting()}. Ada yang bisa saya bantu?",
            'command_type': 'greeting'
        }
    
    # Rule 2: Waktu / Time
    if any(word in user_input for word in ['jam', 'waktu', 'pukul', 'tanggal']):
        return {
            'success': True,
            'message': get_current_time_response(),
            'command_type': 'time'
        }
    
    # Rule 3: Status RAM
    if any(word in user_input for word in ['ram', 'memori', 'memory']):
        ram_data = get_ram_status()
        if ram_data['status'] == 'ok':
            message = (
                f"{get_greeting()}. Status RAM saat ini:\n"
                f"• Total: {ram_data['total_gb']} GB\n"
                f"• Digunakan: {ram_data['used_gb']} GB\n"
                f"• Tersedia: {ram_data['available_gb']} GB\n"
                f"• Penggunaan: {ram_data['percent']}%"
            )
            return {
                'success': True,
                'message': message,
                'data': ram_data,
                'command_type': 'ram_status'
            }
        else:
            return {
                'success': False,
                'message': f"Mohon maaf, {MASTER_NAME}. Gagal mendapatkan status RAM: {ram_data['status']}",
                'command_type': 'ram_status'
            }
    
    # Rule 4: Status CPU
    if 'cpu' in user_input or 'processor' in user_input or 'prosesor' in user_input:
        cpu_data = get_cpu_status()
        if cpu_data['status'] == 'ok':
            message = (
                f"{get_greeting()}. Status CPU saat ini:\n"
                f"• Penggunaan: {cpu_data['percent']}%\n"
                f"• Core Fisik: {cpu_data['cores_physical']}\n"
                f"• Core Logical: {cpu_data['cores_logical']}\n"
                f"• Frekuensi: {cpu_data['freq_current_mhz']} MHz"
            )
            return {
                'success': True,
                'message': message,
                'data': cpu_data,
                'command_type': 'cpu_status'
            }
        else:
            return {
                'success': False,
                'message': f"Mohon maaf, {MASTER_NAME}. Gagal mendapatkan status CPU: {cpu_data['status']}",
                'command_type': 'cpu_status'
            }
    
    # Rule 5: Status GPU
    if 'gpu' in user_input or 'grafis' in user_input or 'vga' in user_input:
        gpu_data = get_gpu_status()
        if gpu_data['status'] == 'ok':
            message = (
                f"{get_greeting()}. Status GPU saat ini:\n"
                f"• Nama: {gpu_data['name']}\n"
                f"• Suhu: {gpu_data['temperature_c']}°C\n"
                f"• Penggunaan: {gpu_data['utilization_percent']}%\n"
                f"• Memory Digunakan: {gpu_data['memory_used_mb']} MB\n"
                f"• Memory Total: {gpu_data['memory_total_mb']} MB"
            )
            return {
                'success': True,
                'message': message,
                'data': gpu_data,
                'command_type': 'gpu_status'
            }
        else:
            message = f"Mohon maaf, {MASTER_NAME}. Status GPU: {gpu_data['status']}"
            return {
                'success': False,
                'message': message,
                'data': gpu_data,
                'command_type': 'gpu_status'
            }
    
    # Rule 6: Status Sistem Lengkap
    if any(word in user_input for word in ['sistem', 'system', 'semua', 'lengkap', 'ringkasan']):
        summary = get_system_summary()
        ram = summary['ram']
        cpu = summary['cpu']
        gpu = summary['gpu']
        
        message = (
            f"{get_greeting()}. Berikut ringkasan sistem lengkap:\n\n"
            f"📊 RAM:\n"
            f"  • {ram['used_gb']}/{ram['total_gb']} GB ({ram['percent']}%)\n\n"
            f"⚙️ CPU:\n"
            f"  • Penggunaan: {cpu['percent']}%\n"
            f"  • Cores: {cpu['cores_physical']} fisik, {cpu['cores_logical']} logical\n\n"
            f"🎮 GPU:\n"
            f"  • {gpu['name']}\n"
            f"  • Suhu: {gpu['temperature_c']}°C, Penggunaan: {gpu['utilization_percent']}%"
        )
        
        return {
            'success': True,
            'message': message,
            'data': summary,
            'command_type': 'system_summary'
        }
    
    # Rule 7: Bantuan / Help
    if any(word in user_input for word in ['bantuan', 'help', 'tolong', 'bisa apa']):
        message = (
            f"{get_greeting()}. Saya dapat membantu Anda dengan:\n\n"
            "📋 Perintah yang tersedia:\n"
            "  • 'cek ram' - Melihat status RAM\n"
            "  • 'cek cpu' - Melihat status CPU\n"
            "  • 'cek gpu' - Melihat status GPU\n"
            "  • 'cek sistem' - Ringkasan lengkap sistem\n"
            "  • 'jam berapa' - Melihat waktu saat ini\n"
            "  • 'bantuan' - Menampilkan pesan ini\n\n"
            "Silakan berikan perintah yang Anda inginkan."
        )
        return {
            'success': True,
            'message': message,
            'command_type': 'help'
        }
    
    # Rule Default: Unknown Command
    return {
        'success': False,
        'message': format_unknown_command(),
        'command_type': 'unknown'
    }
