import os
from notion_client import AsyncClient
from dotenv import load_dotenv

async def test_connection():
    # Загружаем переменные окружения
    load_dotenv()
    
    # Получаем токен и проверяем его
    token = os.getenv('NOTION_TOKEN')
    if not token or not token.startswith(('secret_', 'ntn_')):
        print("Invalid token format")
        return
        
    client = AsyncClient(auth=token)
    try:
        response = await client.databases.retrieve(
            database_id=os.getenv('DATABASE_ID')
        )
        print('Connection successful!')
        print('Database name:', response['title'][0]['text']['content'])
    except Exception as e:
        print('Connection failed:', str(e))

if __name__ == '__main__':
    import asyncio
    asyncio.run(test_connection()) 