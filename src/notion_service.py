"""Notion service with connection pooling and user isolation"""

import logging
import asyncio
from typing import Dict, List, Optional
from notion_client import Client

logger = logging.getLogger(__name__)

class NotionService:
    def __init__(self, token: str, database_id: str):
        self.token = token
        self.database_id = database_id
        self.client = None
        self._initialize_client()
        self._connection_pool = {}
        self._min_request_interval = 0.34  # ~3 requests per second
        
    def _initialize_client(self):
        """Initialize Notion client with error handling"""
        try:
            self.client = Client(auth=self.token)
            # Test connection
            self.client.users.me()
            logger.info("Successfully connected to Notion API")
        except Exception as e:
            logger.error(f"Failed to initialize Notion client: {e}")
            raise
        
    def _validate_database_id(self, database_id: str) -> str:
        """Validates and formats database ID"""
        formatted_id = database_id.replace('-', '')
        if len(formatted_id) != 32:
            raise ValueError(
                "Invalid database ID format. ID should be 32 characters"
            )
        return formatted_id

    async def _test_database_access(self):
        """Test database access and schema"""
        try:
            # Query database to verify access
            response = await self.client.databases.retrieve(database_id=self.database_id)
            
            # Verify required properties exist
            properties = response.get('properties', {})
            required_props = {'Title': 'title', 'Status': 'status'}
            
            for prop_name, prop_type in required_props.items():
                if prop_name not in properties:
                    raise ValueError(f"Missing required property: {prop_name}")
                if properties[prop_name]['type'] != prop_type:
                    raise ValueError(f"Invalid type for {prop_name}. Expected {prop_type}")
            
            logger.info(f"Successfully verified database schema")
            return True
            
        except Exception as e:
            logger.error(f"Database access test failed: {e}")
            raise

    async def initialize(self):
        """Full initialization with connection and schema validation"""
        await self._test_database_access()
        
    async def get_user_connection(self, user_id: int) -> Dict:
        """Get or create connection for user with rate limiting"""
        if user_id not in self._connection_pool:
            self._connection_pool[user_id] = {
                'client': Client(auth=self.client.auth),
                'last_request': 0,
                'tasks_cache': {}
            }
        return self._connection_pool[user_id]

    async def _wait_for_rate_limit(self, user_id: int):
        """Per-user rate limiting"""
        conn = await self.get_user_connection(user_id)
        now = asyncio.get_event_loop().time()
        time_since_last = now - conn['last_request']
        
        if time_since_last < self._min_request_interval:
            await asyncio.sleep(self._min_request_interval - time_since_last)
        conn['last_request'] = now

    async def create_task(self, user_id: int, title: str, status: str = "Not Started") -> Optional[Dict]:
        """Create task with user isolation and proper error handling"""
        try:
            await self._wait_for_rate_limit(user_id)
            conn = await self.get_user_connection(user_id)
            
            # Validate inputs
            if not title:
                raise ValueError("Task title cannot be empty")
                
            properties = {
                "Title": {"title": [{"text": {"content": title}}]},
                "Status": {"status": {"name": status}}
            }
                
            response = await conn['client'].pages.create(
                parent={"database_id": self.database_id},
                properties=properties
            )
            
            # Update user's cache
            if response:
                conn['tasks_cache'][response['id']] = response
                logger.info(f"Successfully created task: {title}")
                
            return response
            
        except Exception as e:
            logger.error(f"Failed to create task for user {user_id}: {e}")
            raise