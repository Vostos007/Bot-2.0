"""Rate limiting implementation"""

from datetime import datetime, timedelta
from collections import deque
from typing import Dict, Deque

class RateLimiter:
    def __init__(self, max_requests: int = 30, time_window: int = 60):
        """Initialize rate limiter
        
        Args:
            max_requests: Maximum requests per time window
            time_window: Time window in seconds
        """
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests: Dict[int, Deque[datetime]] = {}
        
    def can_make_request(self, user_id: int) -> bool:
        """Check if user can make a request"""
        now = datetime.now()
        
        # Initialize user's request history
        if user_id not in self.requests:
            self.requests[user_id] = deque()
            
        # Remove old requests
        while self.requests[user_id] and \
            (now - self.requests[user_id][0]) > timedelta(seconds=self.time_window):
            self.requests[user_id].popleft()
            
        # Check limit
        if len(self.requests[user_id]) >= self.max_requests:
            return False
            
        # Add new request
        self.requests[user_id].append(now)
        return True