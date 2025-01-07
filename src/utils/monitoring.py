"""Resource monitoring utilities"""

import psutil
import logging
from datetime import datetime

class ResourceMonitor:
    def __init__(self, warning_threshold: int = 40):
        """Initialize monitor with CPU warning threshold"""
        self.warning_threshold = warning_threshold
        self.process = psutil.Process()
        
    def check_resources(self) -> dict:
        """Check CPU and memory usage"""
        try:
            cpu_percent = self.process.cpu_percent(interval=1)
            memory_info = self.process.memory_info()
            
            # Log warning if CPU usage is too high
            if cpu_percent > self.warning_threshold:
                logging.warning(f"High CPU usage: {cpu_percent}%")
            
            return {
                'cpu_percent': cpu_percent,
                'memory_mb': memory_info.rss / 1024 / 1024,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logging.error(f"Monitoring error: {e}")
            return {}
