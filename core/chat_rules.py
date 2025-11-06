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
from core.tools_manager import get_tools_manager


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
    
    # Rule 3: Tools Management - Setup Tool
    if 'setup' in user_input:
        return _handle_tool_setup(user_input)
    
    # Rule 4: Tools Management - List Available Tools
    if any(phrase in user_input for phrase in ['list tools', 'tools available', 'daftar tools']):
        return _handle_list_available_tools()
    
    # Rule 5: Tools Management - List Installed Tools
    if any(phrase in user_input for phrase in ['tools installed', 'installed tools', 'tools terpasang']):
        return _handle_list_installed_tools()
    
    # Rule 6: Tools Management - Remove Tool
    if 'remove' in user_input or 'uninstall' in user_input:
        return _handle_tool_remove(user_input)
    
    # Rule 7: Status RAM
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
    
    # Rule 8: Status CPU
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
    
    # Rule 9: Status GPU
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
    
    # Rule 10: Status Sistem Lengkap
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
    
    # Rule 11: Bantuan / Help
    if any(word in user_input for word in ['bantuan', 'help', 'tolong', 'bisa apa']):
        message = (
            f"{get_greeting()}. Saya dapat membantu Anda dengan:\n\n"
            "📋 Perintah Sistem:\n"
            "  • 'cek ram' - Melihat status RAM\n"
            "  • 'cek cpu' - Melihat status CPU\n"
            "  • 'cek gpu' - Melihat status GPU\n"
            "  • 'cek sistem' - Ringkasan lengkap sistem\n"
            "  • 'jam berapa' - Melihat waktu saat ini\n\n"
            "🔧 Perintah Tools Manager:\n"
            "  • 'setup nginx 1.25.4' - Install tool\n"
            "  • 'list tools' - Lihat tools tersedia\n"
            "  • 'tools installed' - Lihat tools terpasang\n"
            "  • 'remove nginx 1.25.4' - Hapus tool\n\n"
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


def _handle_tool_setup(user_input: str) -> Dict[str, Any]:
    """Handle setup tool command.
    
    Expected format: "setup <tool> <version>"
    Example: "setup nginx 1.25.4"
    """
    parts = user_input.split()
    
    if len(parts) < 3:
        return {
            'success': False,
            'message': f"Mohon maaf, {MASTER_NAME}. Format command: 'setup <tool> <version>'\nContoh: 'setup nginx 1.25.4'",
            'command_type': 'tool_setup'
        }
    
    tool = parts[1]
    version = parts[2]
    
    try:
        tools_manager = get_tools_manager()
        success, message = tools_manager.setup_tool(tool, version)
        
        formatted_message = f"{get_greeting()}. {message}" if success else f"Mohon maaf, {MASTER_NAME}. {message}"
        
        return {
            'success': success,
            'message': formatted_message,
            'data': {
                'tool': tool,
                'version': version
            },
            'command_type': 'tool_setup'
        }
    
    except Exception as e:
        return {
            'success': False,
            'message': f"Mohon maaf, {MASTER_NAME}. Terjadi error: {str(e)}",
            'command_type': 'tool_setup'
        }


def _handle_list_available_tools() -> Dict[str, Any]:
    """Handle list available tools command."""
    try:
        tools_manager = get_tools_manager()
        available = tools_manager.list_available_tools()
        
        if not available:
            return {
                'success': False,
                'message': f"Mohon maaf, {MASTER_NAME}. Tidak ada tools yang tersedia dalam konfigurasi.",
                'command_type': 'list_tools'
            }
        
        message_lines = [f"{get_greeting()}. Berikut daftar tools yang tersedia:\n"]
        
        for tool, versions in sorted(available.items()):
            versions_str = ', '.join(versions)
            message_lines.append(f"🔧 {tool}: {versions_str}")
        
        message_lines.append(f"\nGunakan 'setup <tool> <version>' untuk menginstall.")
        
        return {
            'success': True,
            'message': '\n'.join(message_lines),
            'data': available,
            'command_type': 'list_tools'
        }
    
    except Exception as e:
        return {
            'success': False,
            'message': f"Mohon maaf, {MASTER_NAME}. Terjadi error: {str(e)}",
            'command_type': 'list_tools'
        }


def _handle_list_installed_tools() -> Dict[str, Any]:
    """Handle list installed tools command."""
    try:
        tools_manager = get_tools_manager()
        installed = tools_manager.list_installed_tools()
        
        if not installed:
            return {
                'success': True,
                'message': f"{get_greeting()}. Belum ada tools yang terinstall.\nGunakan 'setup <tool> <version>' untuk menginstall.",
                'command_type': 'installed_tools'
            }
        
        message_lines = [f"{get_greeting()}. Tools yang terinstall:\n"]
        
        for item in installed:
            message_lines.append(f"✅ {item['tool']} {item['version']}")
            message_lines.append(f"   📁 {item['path']}\n")
        
        return {
            'success': True,
            'message': '\n'.join(message_lines),
            'data': installed,
            'command_type': 'installed_tools'
        }
    
    except Exception as e:
        return {
            'success': False,
            'message': f"Mohon maaf, {MASTER_NAME}. Terjadi error: {str(e)}",
            'command_type': 'installed_tools'
        }


def _handle_tool_remove(user_input: str) -> Dict[str, Any]:
    """Handle remove tool command.
    
    Expected format: "remove <tool> <version>"
    Example: "remove nginx 1.25.4"
    """
    parts = user_input.split()
    
    if len(parts) < 3:
        return {
            'success': False,
            'message': f"Mohon maaf, {MASTER_NAME}. Format command: 'remove <tool> <version>'\nContoh: 'remove nginx 1.25.4'",
            'command_type': 'tool_remove'
        }
    
    tool = parts[1]
    version = parts[2]
    
    try:
        tools_manager = get_tools_manager()
        success, message = tools_manager.remove_tool(tool, version)
        
        formatted_message = f"{get_greeting()}. {message}" if success else f"Mohon maaf, {MASTER_NAME}. {message}"
        
        return {
            'success': success,
            'message': formatted_message,
            'data': {
                'tool': tool,
                'version': version
            },
            'command_type': 'tool_remove'
        }
    
    except Exception as e:
        return {
            'success': False,
            'message': f"Mohon maaf, {MASTER_NAME}. Terjadi error: {str(e)}",
            'command_type': 'tool_remove'
        }
