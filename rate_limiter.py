import json
import time
import threading
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime, timedelta

class RateLimiter:
    """Rate limiter that restricts users to one request per hour."""
    
    def __init__(self, storage_path: str = "rate_limits.json"):
        """Initialize the rate limiter with storage path."""
        self.storage_path = Path(storage_path)
        self._lock = threading.Lock()
        self._load_limits()
    
    def _load_limits(self) -> None:
        """Load rate limits from storage file."""
        try:
            if self.storage_path.exists():
                with open(self.storage_path, 'r') as f:
                    self.limits = json.load(f)
            else:
                self.limits = {}
        except (json.JSONDecodeError, IOError):
            self.limits = {}
    
    def _save_limits(self) -> None:
        """Save rate limits to storage file."""
        with open(self.storage_path, 'w') as f:
            json.dump(self.limits, f)
    
    def _cleanup_expired(self) -> None:
        """Remove expired entries."""
        current_time = time.time()
        expired = []
        for user_id, last_request in self.limits.items():
            if current_time - last_request > 3600:  # 1 hour
                expired.append(user_id)
        
        for user_id in expired:
            del self.limits[user_id]
    
    def check_rate_limit(self, user_id: int, is_admin: bool = False) -> tuple[bool, Optional[int]]:
        """
        Check if a user has exceeded their rate limit.
        
        Args:
            user_id: The user's ID
            is_admin: Whether the user is an admin (bypasses rate limit)
            
        Returns:
            tuple[bool, Optional[int]]: (is_allowed, seconds_remaining)
            - is_allowed: True if request is allowed, False if rate limited
            - seconds_remaining: Seconds until next allowed request, None if allowed
        """
        # Admins bypass rate limiting
        if is_admin:
            return True, None

        with self._lock:
            self._cleanup_expired()
            
            current_time = time.time()
            last_request = self.limits.get(str(user_id))
            
            if last_request is None:
                self.limits[str(user_id)] = current_time
                self._save_limits()
                return True, None
            
            time_passed = current_time - last_request
            if time_passed < 3600:  # 1 hour in seconds
                return False, int(3600 - time_passed)
            
            self.limits[str(user_id)] = current_time
            self._save_limits()
            return True, None
