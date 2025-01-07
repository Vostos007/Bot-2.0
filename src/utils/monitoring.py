"""System monitoring utilities"""

import psutil
import logging
from datetime import datetime
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class SystemMonitor:
    def __init__(self, cpu_threshold: float = 80.0, memory_threshold: float = 80.0):
        self.cpu_threshold = cpu_threshold
        self.memory_threshold = memory_threshold
        self.last_check = None
        self.process = psutil.Process()
        
    def check_system(self) -> Dict[str, float]:
        """Check system resources"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory_percent = psutil.virtual_memory().percent
            process_cpu = self.process.cpu_percent()
            process_memory = self.process.memory_percent()
            
            self.last_check = datetime.now()
            
            metrics = {
                'system_cpu': cpu_percent,
                'system_memory': memory_percent,
                'process_cpu': process_cpu,
                'process_memory': process_memory
            }
            
            self._log_metrics(metrics)
            self._check_thresholds(metrics)
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error monitoring system: {e}")
            return {}
            
    def _log_metrics(self, metrics: Dict[str, float]):
        """Log system metrics"""
        logger.info(
            f"System metrics - CPU: {metrics['system_cpu']:.1f}%, "
            f"Memory: {metrics['system_memory']:.1f}%, "
            f"Process CPU: {metrics['process_cpu']:.1f}%, "
            f"Process Memory: {metrics['process_memory']:.1f}%"
        )
        
    def _check_thresholds(self, metrics: Dict[str, float]):
        """Check if metrics exceed thresholds"""
        if metrics['system_cpu'] > self.cpu_threshold:
            logger.warning(
                f"High CPU usage: {metrics['system_cpu']:.1f}% "
                f"(threshold: {self.cpu_threshold}%)"
            )
            
        if metrics['system_memory'] > self.memory_threshold:
            logger.warning(
                f"High memory usage: {metrics['system_memory']:.1f}% "
                f"(threshold: {self.memory_threshold}%)"
            )

class BotMonitor:
    def __init__(self):
        self.active_users = set()
        self.command_counts = {}
        self.error_counts = {}
        self.last_errors = {}
        
    def log_user_activity(self, user_id: int, command: str):
        """Log user command execution"""
        self.active_users.add(user_id)
        if command not in self.command_counts:
            self.command_counts[command] = 0
        self.command_counts[command] += 1
        
    def log_error(self, error_type: str, error: Exception, user_id: Optional[int] = None):
        """Log error occurrence"""
        if error_type not in self.error_counts:
            self.error_counts[error_type] = 0
        self.error_counts[error_type] += 1
        
        self.last_errors[error_type] = {
            'time': datetime.now(),
            'error': str(error),
            'user_id': user_id
        }
        
    def get_stats(self) -> Dict:
        """Get bot statistics"""
        return {
            'active_users': len(self.active_users),
            'command_counts': self.command_counts.copy(),
            'error_counts': self.error_counts.copy(),
            'last_errors': self.last_errors.copy()
        }
