"""Optimized Notion service"""

import logging
import asyncio
from typing import Dict, List, Optional
from notion_client import Client

logger = logging.getLogger(__name__)

class NotionService:
    def __init__(self, token: str, database_id: str):
        self.client = Client(auth=token)
        self.database_id = database_id
        self._last_request = 0
        self._min_request_interval = 0.34  # ~3 requests per second
        
    async def _wait_for_rate_limit(self):
        """Simple rate limiting for Notion API"""
        now = asyncio.get_event_loop().time()
        time_since_last = now - self._last_request
        if time_since_last < self._min_request_interval:
            await asyncio.sleep(self._min_request_interval - time_since_last)
        self._last_request = now

    async def query_database(self, limit: int = 10, filter_conditions: Optional[Dict] = None) -> List[Dict]:
        """Query database with rate limiting and error handling"""
        await self._wait_for_rate_limit()
        
        try:
            response = await self.client.databases.query(
                database_id=self.database_id,
                filter=filter_conditions,
                page_size=limit
            )
            return response.get("results", [])
            
        except Exception as e:
            logger.error(f"Failed to query database: {e}")
            return []

    async def create_task(self, title: str, status: Optional[str] = None) -> Optional[Dict]:
        """Create task with rate limiting"""
        await self._wait_for_rate_limit()
        
        try:
            properties = {
                "Title": {"title": [{"text": {"content": title}}]},
            }
            
            if status:
                properties["Status"] = {"status": {"name": status}}
                
            response = await self.client.pages.create(
                parent={"database_id": self.database_id},
                properties=properties
            )
            return response
            
        except Exception as e:
            logger.error(f"Failed to create task: {e}")
            return None