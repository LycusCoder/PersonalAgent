"""Response Templates - Multiple Response Variations for Agent Persona

Menyediakan variasi template response agar Agent terasa lebih natural dan tidak monoton.
Tetap rule-based, tapi dengan random selection dari multiple templates.
"""

import random
from typing import List, Dict, Any
from datetime import datetime


class ResponseTemplates:
    """Manager untuk template response dengan variasi."""
    
    # Greeting Variations
    GREETINGS = {
        "morning": [
            "Selamat pagi, {master}.",
            "Pagi yang cerah, {master}.",
            "Selamat pagi, {master}. Semoga hari Anda menyenangkan.",
            "Pagi, {master}. Siap melayani Anda hari ini.",
        ],
        "afternoon": [
            "Selamat siang, {master}.",
            "Siang yang produktif, {master}.",
            "Selamat siang, {master}. Apa yang bisa saya bantu?",
            "Siang, {master}. Ada yang perlu saya lakukan?",
        ],
        "evening": [
            "Selamat sore, {master}.",
            "Sore yang tenang, {master}.",
            "Selamat sore, {master}. Bagaimana hari Anda?",
            "Sore, {master}. Semoga hari Anda lancar.",
        ],
        "night": [
            "Selamat malam, {master}.",
            "Malam yang damai, {master}.",
            "Selamat malam, {master}. Jangan terlalu larut bekerja.",
            "Malam, {master}. Istirahat yang cukup ya.",
        ]
    }
    
    # RAM Status Templates
    RAM_TEMPLATES = {
        "normal": [  # < 60%
            "Status RAM saat ini dalam kondisi baik:\n• Total: {total_gb} GB\n• Digunakan: {used_gb} GB\n• Tersedia: {available_gb} GB\n• Penggunaan: {percent}%\n\nSemuanya berjalan normal, {master}.",
            "RAM Anda masih sangat lapang:\n• Total: {total_gb} GB\n• Terpakai: {used_gb} GB\n• Sisa: {available_gb} GB\n• Persentase: {percent}%\n\nTidak ada yang perlu dikhawatirkan.",
            "Memori sistem dalam kondisi optimal:\n• Kapasitas: {total_gb} GB\n• Digunakan: {used_gb} GB ({percent}%)\n• Tersedia: {available_gb} GB\n\nSemua baik-baik saja, {master}.",
        ],
        "warning": [  # 60-80%
            "Status RAM:\n• Total: {total_gb} GB\n• Digunakan: {used_gb} GB\n• Tersedia: {available_gb} GB\n• Penggunaan: {percent}%\n\n⚠️ Penggunaan RAM mulai tinggi. Pertimbangkan untuk menutup aplikasi yang tidak digunakan.",
            "RAM Anda mulai penuh:\n• Total: {total_gb} GB\n• Terpakai: {used_gb} GB ({percent}%)\n• Sisa: {available_gb} GB\n\nMungkin perlu menutup beberapa program, {master}.",
            "Perhatian! Memori sudah {percent}% terisi:\n• Kapasitas: {total_gb} GB\n• Digunakan: {used_gb} GB\n• Tersedia: {available_gb} GB\n\nSebaiknya monitoring lebih ketat.",
        ],
        "critical": [  # > 80%
            "Status RAM:\n• Total: {total_gb} GB\n• Digunakan: {used_gb} GB\n• Tersedia: {available_gb} GB\n• Penggunaan: {percent}%\n\n🔴 PERINGATAN! RAM hampir penuh. Sangat disarankan untuk menutup aplikasi atau restart sistem.",
            "RAM KRITIS!\n• Total: {total_gb} GB\n• Terpakai: {used_gb} GB ({percent}%)\n• Sisa: {available_gb} GB\n\nSegera ambil tindakan, {master}! Sistem bisa melambat.",
            "🚨 Memori sangat penuh ({percent}%):\n• Kapasitas: {total_gb} GB\n• Digunakan: {used_gb} GB\n• Tersedia: {available_gb} GB\n\nTindakan segera diperlukan untuk menghindari crash!",
        ]
    }
    
    # CPU Status Templates
    CPU_TEMPLATES = {
        "idle": [  # < 30%
            "Status CPU:\n• Penggunaan: {percent}%\n• Core Count: {core_count}\n• Frekuensi: {frequency} MHz\n\nCPU dalam kondisi idle. Sangat efisien, {master}.",
            "Prosesor Anda santai:\n• Beban: {percent}%\n• Jumlah Core: {core_count}\n• Kecepatan: {frequency} MHz\n\nSemua berjalan lancar.",
            "CPU sedang bekerja ringan:\n• Utilisasi: {percent}%\n• Core: {core_count}\n• Frekuensi: {frequency} MHz\n\nTidak ada masalah, {master}.",
        ],
        "normal": [  # 30-70%
            "Status CPU:\n• Penggunaan: {percent}%\n• Core Count: {core_count}\n• Frekuensi: {frequency} MHz\n\nCPU bekerja dengan normal. Tidak ada bottleneck.",
            "Prosesor dalam beban wajar:\n• Utilisasi: {percent}%\n• Core: {core_count}\n• Speed: {frequency} MHz\n\nPerforma masih optimal.",
            "CPU sedang produktif:\n• Beban: {percent}%\n• Jumlah Core: {core_count}\n• Frekuensi: {frequency} MHz\n\nSemuanya dalam kendali.",
        ],
        "high": [  # > 70%
            "Status CPU:\n• Penggunaan: {percent}%\n• Core Count: {core_count}\n• Frekuensi: {frequency} MHz\n\n⚠️ CPU bekerja keras. Pastikan ventilasi baik untuk menghindari overheating.",
            "Prosesor sedang bekerja berat:\n• Beban: {percent}%\n• Core: {core_count}\n• Speed: {frequency} MHz\n\nMonitor suhu ya, {master}.",
            "🔥 CPU usage tinggi ({percent}%):\n• Core: {core_count}\n• Frekuensi: {frequency} MHz\n\nCek proses yang makan resource.",
        ]
    }
    
    # GPU Status Templates
    GPU_TEMPLATES = {
        "cool": [  # < 60°C
            "Status GPU:\n• Nama: {name}\n• Temperature: {temp}°C\n• Utilization: {utilization}%\n• Memory: {memory_used}MB / {memory_total}MB\n\n❄️ GPU dalam suhu dingin. Sempurna untuk gaming atau rendering!",
            "Kartu grafis Anda adem:\n• Model: {name}\n• Suhu: {temp}°C\n• Penggunaan: {utilization}%\n• VRAM: {memory_used}/{memory_total}MB\n\nSiap untuk beban berat, {master}.",
            "GPU status optimal:\n• {name}\n• Temp: {temp}°C (Cool)\n• Usage: {utilization}%\n• Memory: {memory_used}MB used\n\nKondisi sangat baik.",
        ],
        "warm": [  # 60-75°C
            "Status GPU:\n• Nama: {name}\n• Temperature: {temp}°C\n• Utilization: {utilization}%\n• Memory: {memory_used}MB / {memory_total}MB\n\nGPU sedang bekerja. Suhu normal untuk beban kerja saat ini.",
            "Kartu grafis hangat:\n• {name}\n• Suhu: {temp}°C\n• Beban: {utilization}%\n• VRAM: {memory_used}/{memory_total}MB\n\nMasih dalam batas aman.",
            "GPU temperature normal:\n• Model: {name}\n• Temp: {temp}°C\n• Usage: {utilization}%\n• Memory: {memory_used}MB\n\nTidak ada masalah.",
        ],
        "hot": [  # > 75°C
            "Status GPU:\n• Nama: {name}\n• Temperature: {temp}°C\n• Utilization: {utilization}%\n• Memory: {memory_used}MB / {memory_total}MB\n\n🔥 GPU panas! Pastikan cooling berfungsi dengan baik.",
            "PERINGATAN - GPU hot:\n• {name}\n• Suhu: {temp}°C 🔥\n• Beban: {utilization}%\n• VRAM: {memory_used}/{memory_total}MB\n\nCek fan speed dan airflow, {master}!",
            "⚠️ GPU overheating:\n• Model: {name}\n• Temp: {temp}°C (HOT!)\n• Usage: {utilization}%\n• Memory: {memory_used}MB\n\nKurangi beban atau tingkatkan cooling.",
        ]
    }
    
    # Acknowledgment / Casual Responses
    ACKNOWLEDGMENTS = [
        "Baik, {master}.",
        "Siap, {master}.",
        "Dengan senang hati, {master}.",
        "Saya mengerti, {master}.",
        "Tentu, {master}.",
        "Segera, {master}.",
    ]
    
    # Unknown Command Responses
    UNKNOWN_RESPONSES = [
        "Maaf {master}, saya belum memahami perintah tersebut. Coba gunakan 'bantuan' untuk melihat daftar perintah.",
        "Mohon maaf, perintah tidak dikenali. Ketik 'bantuan' untuk melihat apa yang bisa saya lakukan.",
        "Saya belum dilatih untuk perintah itu, {master}. Gunakan 'ag bantuan' untuk daftar perintah yang tersedia.",
        "Hmm, saya tidak familiar dengan perintah tersebut. Coba 'agt bantuan' untuk bantuan lebih lanjut.",
    ]
    
    @staticmethod
    def get_greeting(time_of_day: str, master_name: str) -> str:
        """Get random greeting based on time of day."""
        templates = ResponseTemplates.GREETINGS.get(time_of_day, ResponseTemplates.GREETINGS["morning"])
        return random.choice(templates).format(master=master_name)
    
    @staticmethod
    def get_ram_response(data: Dict[str, Any], master_name: str) -> str:
        """Get RAM status response with variation."""
        percent = data.get('percent', 0)
        
        if percent < 60:
            category = "normal"
        elif percent < 80:
            category = "warning"
        else:
            category = "critical"
        
        templates = ResponseTemplates.RAM_TEMPLATES[category]
        template = random.choice(templates)
        
        return template.format(
            total_gb=data.get('total_gb', 0),
            used_gb=data.get('used_gb', 0),
            available_gb=data.get('available_gb', 0),
            percent=data.get('percent', 0),
            master=master_name
        )
    
    @staticmethod
    def get_cpu_response(data: Dict[str, Any], master_name: str) -> str:
        """Get CPU status response with variation."""
        percent = data.get('percent', 0)
        
        if percent < 30:
            category = "idle"
        elif percent < 70:
            category = "normal"
        else:
            category = "high"
        
        templates = ResponseTemplates.CPU_TEMPLATES[category]
        template = random.choice(templates)
        
        return template.format(
            percent=data.get('percent', 0),
            core_count=data.get('core_count', 0),
            frequency=data.get('frequency', 0),
            master=master_name
        )
    
    @staticmethod
    def get_gpu_response(data: Dict[str, Any], master_name: str) -> str:
        """Get GPU status response with variation."""
        temp = data.get('temperature', 0)
        
        if temp < 60:
            category = "cool"
        elif temp < 75:
            category = "warm"
        else:
            category = "hot"
        
        templates = ResponseTemplates.GPU_TEMPLATES[category]
        template = random.choice(templates)
        
        return template.format(
            name=data.get('name', 'N/A'),
            temp=data.get('temperature', 0),
            utilization=data.get('utilization', 0),
            memory_used=data.get('memory_used', 0),
            memory_total=data.get('memory_total', 0),
            master=master_name
        )
    
    @staticmethod
    def get_acknowledgment(master_name: str) -> str:
        """Get random acknowledgment."""
        return random.choice(ResponseTemplates.ACKNOWLEDGMENTS).format(master=master_name)
    
    @staticmethod
    def get_unknown_response(master_name: str) -> str:
        """Get random unknown command response."""
        return random.choice(ResponseTemplates.UNKNOWN_RESPONSES).format(master=master_name)