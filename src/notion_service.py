"""Notion API service"""

import logging
from typing import Dict, Any, Optional
from notion_client import Client
from .constants import TASK_STATUSES

class NotionService:
    def __init__(self, token: str):
        self.client = Client(auth=token)
        
    async def create_task(self, database_id: str, title: str, assignee_id: str):
        """Create basic task"""
        try:
            return await self.client.pages.create(
                parent={"database_id": database_id},
                properties={
                    "Title": {"title": [{"text": {"content": title}}]},
                    "Assignee": {"people": [{"id": assignee_id}]},
                    "Status": {"select": {"name": TASK_STATUSES["TODO"]}}
                }
            )
        except Exception as e:
            logging.error(f"Failed to create task: {e}")
            raise

    async def update_status(self, page_id: str, status: str):
        """Update task status"""
        try:
            return await self.client.pages.update(
                page_id=page_id,
                properties={"Status": {"select": {"name": status}}}
            )
        except Exception as e:
            logging.error(f"Failed to update status: {e}")
            raise

    async def query_database(self, database_id: str, filter_params: Optional[Dict] = None):
        """Query tasks with optional filters"""
        try:
            return await self.client.databases.query(
                database_id=database_id,
                filter=filter_params
            )
        except Exception as e:
            logging.error(f"Failed to query database: {e}")
            return []