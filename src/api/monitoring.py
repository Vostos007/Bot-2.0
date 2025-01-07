from fastapi import APIRouter, HTTPException
import psutil
import time
from typing import Dict, Any

router = APIRouter()

class SystemMonitor:
    @staticmethod
    def get_system_stats() -> Dict[str, Any]:
        return {
            'cpu_percent': psutil.cpu_percent(),
            'memory_usage': psutil.virtual_memory().percent,
            'disk_usage': psutil.disk_usage('/').percent,
            'uptime': time.time() - psutil.boot_time()
        }
    
    @staticmethod
    def get_bot_stats() -> Dict[str, Any]:
        return {
            'active_users': 0,  # Replace with actual data
            'messages_processed': 0,
            'errors_count': 0
        }

@router.get('/health')
async def health_check():
    return {'status': 'healthy'}

@router.get('/metrics')
async def get_metrics():
    try:
        system_stats = SystemMonitor.get_system_stats()
        bot_stats = SystemMonitor.get_bot_stats()
        
        return {
            'system': system_stats,
            'bot': bot_stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))