"""Resource monitoring and management"""

import psutil
import logging
import asyncio
from typing import Dict, Optional

class ResourceMonitor:
    def __init__(
        self,
        cpu_threshold: int = 80,  # 80% CPU max
        memory_threshold: int = 400 * 1024 * 1024,  # 400MB memory max
        check_interval: int = 30  # Check every 30 seconds
    ):
        self.cpu_threshold = cpu_threshold
        self.memory_threshold = memory_threshold
        self.check_interval = check_interval
        self._running = False
        self._last_check: Optional[Dict] = None
        
    async def start_monitoring(self):
        """Start resource monitoring"""
        self._running = True
        while self._running:
            try:
                await self.check_resources()
                await asyncio.sleep(self.check_interval)
            except Exception as e:
                logging.error(f"Monitoring error: {e}")
                
    def stop_monitoring(self):
        """Stop resource monitoring"""
        self._running = False
        
    async def check_resources(self) -> Dict:
        """Check system resources"""
        try:
            process = psutil.Process()
            
            # Get CPU usage (as percentage)
            cpu_percent = process.cpu_percent(interval=1)
            
            # Get memory usage (in bytes)
            memory_info = process.memory_info()
            memory_usage = memory_info.rss
            
            status = {
                "cpu_percent": cpu_percent,
                "memory_usage": memory_usage,
                "memory_percent": memory_usage / psutil.virtual_memory().total * 100
            }
            
            # Log if exceeding thresholds
            if cpu_percent > self.cpu_threshold:
                logging.warning(f"High CPU usage: {cpu_percent}%")
                
            if memory_usage > self.memory_threshold:
                logging.warning(
                    f"High memory usage: {memory_usage / 1024 / 1024:.1f} MB"
                )
                
            self._last_check = status
            return status
            
        except Exception as e:
            logging.error(f"Error checking resources: {e}")
            return {}
            
    def should_throttle(self) -> bool:
        """Check if we should throttle requests"""
        if not self._last_check:
            return False
            
        return (
            self._last_check["cpu_percent"] > self.cpu_threshold or
            self._last_check["memory_usage"] > self.memory_threshold
        )