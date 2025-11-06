"""Context Manager - Track conversation context and system state

Membantu Agent memiliki 'memory' dan awareness terhadap context:
- Command history
- System state trends
- Time-based patterns
- User preferences (future)
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from collections import defaultdict

from config.settings import PROJECT_ROOT


class ContextManager:
    """Manage conversation context and system awareness."""
    
    def __init__(self):
        self.context_file = PROJECT_ROOT / 'storage' / 'context.json'
        self.context_data = self._load_context()
        
    def _load_context(self) -> Dict:
        """Load context from file."""
        if self.context_file.exists():
            try:
                with open(self.context_file, 'r') as f:
                    return json.load(f)
            except Exception:
                pass
        
        return {
            "last_commands": [],
            "system_stats": {},
            "interaction_count": 0,
            "preferences": {},
            "last_updated": None
        }
    
    def _save_context(self):
        """Save context to file."""
        try:
            self.context_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.context_file, 'w') as f:
                json.dump(self.context_data, f, indent=2)
        except Exception:
            pass
    
    def add_command(self, command: str, command_type: str, success: bool):
        """Add command to history (limited to last 10)."""
        command_entry = {
            "command": command,
            "type": command_type,
            "success": success,
            "timestamp": datetime.now().isoformat()
        }
        
        self.context_data["last_commands"].append(command_entry)
        
        # Keep only last 10 commands
        if len(self.context_data["last_commands"]) > 10:
            self.context_data["last_commands"] = self.context_data["last_commands"][-10:]
        
        self.context_data["interaction_count"] += 1
        self.context_data["last_updated"] = datetime.now().isoformat()
        
        self._save_context()
    
    def update_system_stats(self, stat_type: str, value: Any):
        """Update system statistics for trend analysis."""
        if stat_type not in self.context_data["system_stats"]:
            self.context_data["system_stats"][stat_type] = []
        
        stat_entry = {
            "value": value,
            "timestamp": datetime.now().isoformat()
        }
        
        self.context_data["system_stats"][stat_type].append(stat_entry)
        
        # Keep only last 50 stat entries per type
        if len(self.context_data["system_stats"][stat_type]) > 50:
            self.context_data["system_stats"][stat_type] = \
                self.context_data["system_stats"][stat_type][-50:]
        
        self._save_context()
    
    def get_recent_commands(self, limit: int = 5) -> List[Dict]:
        """Get recent commands."""
        return self.context_data["last_commands"][-limit:]
    
    def get_command_frequency(self) -> Dict[str, int]:
        """Get frequency of command types."""
        freq = defaultdict(int)
        for cmd in self.context_data["last_commands"]:
            freq[cmd["type"]] += 1
        return dict(freq)
    
    def get_interaction_count(self) -> int:
        """Get total interaction count."""
        return self.context_data.get("interaction_count", 0)
    
    def is_frequent_user(self) -> bool:
        """Check if user is frequent (> 100 interactions)."""
        return self.get_interaction_count() > 100
    
    def get_system_trend(self, stat_type: str, minutes: int = 30) -> Optional[str]:
        """Analyze trend for a stat type in last N minutes.
        
        Returns: 'increasing', 'decreasing', 'stable', or None
        """
        if stat_type not in self.context_data["system_stats"]:
            return None
        
        stats = self.context_data["system_stats"][stat_type]
        if len(stats) < 3:
            return None
        
        # Filter stats from last N minutes
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        recent_stats = [
            s for s in stats
            if datetime.fromisoformat(s["timestamp"]) > cutoff_time
        ]
        
        if len(recent_stats) < 3:
            return None
        
        # Simple trend analysis
        values = [s["value"] for s in recent_stats]
        first_half = sum(values[:len(values)//2]) / (len(values)//2)
        second_half = sum(values[len(values)//2:]) / (len(values) - len(values)//2)
        
        threshold = 5  # 5% change threshold
        diff_percent = ((second_half - first_half) / first_half) * 100 if first_half > 0 else 0
        
        if diff_percent > threshold:
            return "increasing"
        elif diff_percent < -threshold:
            return "decreasing"
        else:
            return "stable"
    
    def get_contextual_greeting_suffix(self) -> str:
        """Get context-aware greeting suffix."""
        count = self.get_interaction_count()
        
        if count == 0:
            return " Senang berkenalan dengan Anda."
        elif count < 10:
            return " Ada yang bisa saya bantu hari ini?"
        elif count < 50:
            return " Seperti biasa, saya siap membantu."
        elif count < 100:
            return " Selalu senang melayani Anda."
        else:
            return " Terima kasih atas kepercayaan Anda selama ini."
    
    def should_suggest_action(self, stat_type: str, threshold: float) -> bool:
        """Check if should suggest action based on recent stats."""
        if stat_type not in self.context_data["system_stats"]:
            return False
        
        stats = self.context_data["system_stats"][stat_type]
        if not stats:
            return False
        
        # Check last 3 entries
        recent = stats[-3:]
        if len(recent) < 3:
            return False
        
        # All above threshold?
        return all(s["value"] > threshold for s in recent)


# Global instance
_context_manager = None

def get_context_manager() -> ContextManager:
    """Get global context manager instance."""
    global _context_manager
    if _context_manager is None:
        _context_manager = ContextManager()
    return _context_manager