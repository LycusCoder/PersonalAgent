"""Modul Database untuk Agent Pribadi (AG)

Mengelola SQLite database untuk:
- Command history
- Reminders (future feature)
- Usage statistics
"""

import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path
from config.settings import DB_PATH, MAX_COMMAND_HISTORY


class AgentDatabase:
    """Class untuk mengelola database Agent."""
    
    def __init__(self, db_path: Path = DB_PATH):
        """Inisialisasi database.
        
        Args:
            db_path: Path ke file database SQLite
        """
        self.db_path = db_path
        self._init_database()
    
    def _get_connection(self) -> sqlite3.Connection:
        """Mendapatkan koneksi database.
        
        Returns:
            sqlite3.Connection: Koneksi database
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Agar hasil query bisa diakses seperti dict
        return conn
    
    def _init_database(self) -> None:
        """Inisialisasi tabel database jika belum ada."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Tabel untuk command history
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS command_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                command TEXT NOT NULL,
                command_type TEXT,
                success INTEGER NOT NULL,
                response_preview TEXT,
                data_json TEXT
            )
        ''')
        
        # Tabel untuk reminders (future feature)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reminders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                remind_at TEXT NOT NULL,
                message TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                completed_at TEXT
            )
        ''')
        
        # Index untuk performa
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_command_timestamp 
            ON command_history(timestamp DESC)
        ''')
        
        conn.commit()
        conn.close()
    
    def add_command_history(
        self,
        command: str,
        command_type: str,
        success: bool,
        response_preview: str,
        data: Optional[Dict] = None
    ) -> int:
        """Menambahkan entry ke command history.
        
        Args:
            command: Command yang dijalankan
            command_type: Tipe command (dari chat_rules)
            success: Apakah command berhasil
            response_preview: Preview dari response (max 200 char)
            data: Data tambahan (akan di-serialize ke JSON)
        
        Returns:
            int: ID dari entry yang ditambahkan
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        timestamp = datetime.now().isoformat()
        data_json = json.dumps(data) if data else None
        response_preview = response_preview[:200] if response_preview else ""
        
        cursor.execute('''
            INSERT INTO command_history 
            (timestamp, command, command_type, success, response_preview, data_json)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (timestamp, command, command_type, int(success), response_preview, data_json))
        
        entry_id = cursor.lastrowid
        conn.commit()
        
        # Cleanup old entries jika melebihi MAX_COMMAND_HISTORY
        self._cleanup_old_history(conn)
        
        conn.close()
        return entry_id
    
    def _cleanup_old_history(self, conn: sqlite3.Connection) -> None:
        """Menghapus history lama jika melebihi MAX_COMMAND_HISTORY.
        
        Args:
            conn: Koneksi database yang aktif
        """
        cursor = conn.cursor()
        
        # Hitung jumlah entries
        cursor.execute('SELECT COUNT(*) as count FROM command_history')
        count = cursor.fetchone()['count']
        
        if count > MAX_COMMAND_HISTORY:
            # Hapus entries tertua
            delete_count = count - MAX_COMMAND_HISTORY
            cursor.execute('''
                DELETE FROM command_history 
                WHERE id IN (
                    SELECT id FROM command_history 
                    ORDER BY timestamp ASC 
                    LIMIT ?
                )
            ''', (delete_count,))
            conn.commit()
    
    def get_command_history(self, limit: int = 20) -> List[Dict]:
        """Mengambil command history terbaru.
        
        Args:
            limit: Maksimal jumlah entries yang diambil
        
        Returns:
            List[Dict]: List of command history entries
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, timestamp, command, command_type, success, response_preview
            FROM command_history
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_command_statistics(self) -> Dict:
        """Mengambil statistik penggunaan command.
        
        Returns:
            Dict: Statistik command (total, success rate, most used, dll)
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Total commands
        cursor.execute('SELECT COUNT(*) as total FROM command_history')
        total = cursor.fetchone()['total']
        
        # Success rate
        cursor.execute('SELECT COUNT(*) as success FROM command_history WHERE success = 1')
        success = cursor.fetchone()['success']
        success_rate = (success / total * 100) if total > 0 else 0
        
        # Most used command types
        cursor.execute('''
            SELECT command_type, COUNT(*) as count
            FROM command_history
            GROUP BY command_type
            ORDER BY count DESC
            LIMIT 5
        ''')
        most_used = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        
        return {
            'total_commands': total,
            'success_rate': round(success_rate, 1),
            'most_used_commands': most_used
        }
    
    def add_reminder(self, remind_at: str, message: str) -> int:
        """Menambahkan reminder baru.
        
        Args:
            remind_at: Waktu reminder (ISO format)
            message: Pesan reminder
        
        Returns:
            int: ID reminder yang ditambahkan
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        created_at = datetime.now().isoformat()
        
        cursor.execute('''
            INSERT INTO reminders (created_at, remind_at, message, status)
            VALUES (?, ?, ?, 'pending')
        ''', (created_at, remind_at, message))
        
        reminder_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return reminder_id
    
    def get_pending_reminders(self) -> List[Dict]:
        """Mengambil reminders yang masih pending.
        
        Returns:
            List[Dict]: List of pending reminders
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, created_at, remind_at, message
            FROM reminders
            WHERE status = 'pending'
            ORDER BY remind_at ASC
        ''')
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]


# Singleton instance
_db_instance = None


def get_db() -> AgentDatabase:
    """Mendapatkan instance database singleton.
    
    Returns:
        AgentDatabase: Instance database
    """
    global _db_instance
    if _db_instance is None:
        _db_instance = AgentDatabase()
    return _db_instance
