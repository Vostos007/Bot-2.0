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
        """Initialize Notion client"""
        try:
            self.client = Client(auth=self.token)
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

    async def query_database(self, user_id: int, limit: int = 10, filter_conditions: Optional[Dict] = None) -> List[Dict]:
        """Query database with user isolation and error handling"""
        try:
            await self._wait_for_rate_limit(user_id)
            conn = await self.get_user_connection(user_id)
            
            response = await conn['client'].databases.query(
                database_id=self.database_id,
                filter=filter_conditions,
                page_size=limit
            )
            
            # Cache results for user
            conn['tasks_cache'] = {
                task['id']: task for task in response.get("results", [])
            }
            
            return list(conn['tasks_cache'].values())
            
        except Exception as e:
            logger.error(f"Failed to query database for user {user_id}: {e}")
            return []

    async def create_task(self, user_id: int, title: str, status: Optional[str] = None) -> Optional[Dict]:
        """Create task with user isolation"""
        try:
            await self._wait_for_rate_limit(user_id)
            conn = await self.get_user_connection(user_id)
            
            properties = {
                "Title": {"title": [{"text": {"content": title}}]},
            }
            
            if status:
                properties["Status"] = {"status": {"name": status}}
                
            response = await conn['client'].pages.create(
                parent={"database_id": self.database_id},
                properties=properties
            )
            
            # Update user's cache
            if response:
                conn['tasks_cache'][response['id']] = response
                
            return response
            
        except Exception as e:
            logger.error(f"Failed to create task for user {user_id}: {e}")
            return None
            
    async def update_task(self, user_id: int, task_id: str, properties: Dict) -> Optional[Dict]:
        """Update task with user validation"""
        try:
            await self._wait_for_rate_limit(user_id)
            conn = await self.get_user_connection(user_id)
            
            # Verify task exists in user's cache
            if task_id not in conn['tasks_cache']:
                return None
                
            response = await conn['client'].pages.update(
                page_id=task_id,
                properties=properties
            )
            
            # Update cache
            if response:
                conn['tasks_cache'][task_id] = response
                
            return response
            
        except Exception as e:
            logger.error(f"Failed to update task {task_id} for user {user_id}: {e}")
            return None

    def cleanup_user(self, user_id: int):
        """Clean up user's connection and cache"""
        if user_id in self._connection_pool:
            del self._connection_pool[user_id]

    async def get_tasks(self):
        """Get tasks from Notion"""
        try:
            # Проверка подключения к Notion
            if not self.client:
                raise Exception("Notion client not initialized")
            
            # Проверка токена
            if not self.token or not self.token.startswith(('secret_', 'ntn_')):
                raise Exception("Invalid Notion token format")
            
            # Получение задач из базы данных
            response = await self.client.databases.query(
                database_id=self.database_id,
                filter={
                    "property": "Status",
                    "select": {
                        "does_not_equal": "Done"
                    }
                }
            )
            
            # Логирование структуры ответа для отладки
            logger.debug(f"Notion API response: {response}")
            
            tasks = []
            for page in response.get("results", []):
                # Проверка наличия обязательных полей
                if "properties" not in page:
                    logger.warning(f"Page missing properties: {page}")
                    continue
                    
                if "Name" not in page["properties"]:
                    logger.warning(f"Page missing Name property: {page}")
                    continue
                    
                if "title" not in page["properties"]["Name"]:
                    logger.warning(f"Name property missing title: {page}")
                    continue
                    
                title = page["properties"]["Name"]["title"][0]["text"]["content"]
                tasks.append(f"• {title}")
                
            return tasks
            
        except Exception as e:
            logger.error(f"Failed to get tasks from Notion: {e}")
            raise