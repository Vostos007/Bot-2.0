"""Optimized Notion service with token validation"""

import logging
import asyncio
import re
from typing import Dict, List, Optional
from notion_client import Client

logger = logging.getLogger(__name__)

class NotionTokenError(Exception):
    """Raised when Notion token is invalid"""
    pass

class NotionService:
    def __init__(self, token: str, database_id: str):
        # Validate token and init client
        if not self._validate_token(token):
            raise NotionTokenError(
                "Invalid Notion token. "
                "Please check your token in https://www.notion.so/my-integrations"
            )
            
        self.client = Client(auth=token)
        self.database_id = self._validate_database_id(database_id)
        self._last_request = 0
        self._min_request_interval = 0.34  # ~3 requests per second

    def _validate_token(self, token: str) -> bool:
        """Validates Notion API token format"""
        if not token or len(token) < 10:
            return False
        return True
    
    def _validate_database_id(self, database_id: str) -> str:
        """Validates and formats database ID"""
        formatted_id = database_id.replace('-', '')
        if not re.match(r'^[a-zA-Z0-9]{32}$', formatted_id):
            raise ValueError(
                "Invalid database ID format. ID should be 32 characters long "
                "(excluding hyphens)."
            )
        return formatted_id

    async def test_connection(self) -> bool:
        """Tests the API connection and token validity"""
        try:
            await self._wait_for_rate_limit()
            await self.client.databases.retrieve(self.database_id)
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Notion: {e}")
            return False
            
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