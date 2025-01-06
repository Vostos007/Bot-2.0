"""Notion API service with rate limiting and error handling"""

import asyncio
import logging
from typing import Dict, Optional
from notion_client import Client

class NotionError(Exception):
    """Base class for Notion API errors"""
    pass

class RateLimitError(NotionError):
    """Raised when rate limit is exceeded"""
    pass

class NotionService:
    def __init__(self, token: str, database_id: str):
        self.client = Client(auth=token)
        self.database_id = database_id
        self._rate_limit_remaining = 90
        
    async def create_task(self, title: str, assignee_id: Optional[str] = None, status: Optional[str] = None):
        """Create task with rate limiting"""
        if self._rate_limit_remaining < 1:
            await asyncio.sleep(60)
            
        try:
            task = await self.client.pages.create(
                parent={"database_id": self.database_id},
                properties={
                    "Name": {"title": [{"text": {"content": title}}]},
                    **({
                        "Assignee": {"people": [{"id": assignee_id}]}
                    } if assignee_id else {}),
                    **({
                        "Status": {"status": {"name": status}}
                    } if status else {})
                }
            )
            return task
        except Exception as e:
            logging.error(f"Failed to create task: {e}")
            raise NotionError(str(e))
            
    async def query_database(self, filter_conditions=None):
        """Query database with rate limiting"""
        if self._rate_limit_remaining < 1:
            await asyncio.sleep(60)
            
        try:
            response = await self.client.databases.query(
                database_id=self.database_id,
                filter=filter_conditions
            )
            self._rate_limit_remaining = int(
                response.get("x-rate-limit-remaining", 90)
            )
            return response
        except Exception as e:
            logging.error(f"Database query error: {e}")
            return []