import logging
import asyncio
from typing import Dict, Any, List, Optional
import mongomock
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings

logger = logging.getLogger("resume_matcher.database")

class MockAsyncCursor:
    def __init__(self, data: List[Dict[str, Any]]):
        self._data = data

    def sort(self, key_or_list, direction=None):
        if isinstance(key_or_list, str):
            reverse = (direction == -1)
            self._data.sort(key=lambda x: x.get(key_or_list, 0), reverse=reverse)
        elif isinstance(key_or_list, list):
            for k, d in reversed(key_or_list):
                self._data.sort(key=lambda x: x.get(k, 0), reverse=(d == -1))
        return self

    def limit(self, count: int):
        self._data = self._data[:count]
        return self

    async def to_list(self, length: Optional[int] = None):
        if length is not None:
            return self._data[:length]
        return self._data

    def __aiter__(self):
        self._iter = iter(self._data)
        return self

    async def __anext__(self):
        try:
            return next(self._iter)
        except StopIteration:
            raise StopAsyncIteration


class MockAsyncCollection:
    def __init__(self, sync_collection):
        self._sync_col = sync_collection

    async def insert_one(self, document: Dict[str, Any]):
        doc_copy = dict(document)
        res = self._sync_col.insert_one(doc_copy)
        return res

    async def insert_many(self, documents: List[Dict[str, Any]]):
        docs_copy = [dict(d) for d in documents]
        res = self._sync_col.insert_many(docs_copy)
        return res

    async def find_one(self, filter: Dict[str, Any] = None):
        res = self._sync_col.find_one(filter or {})
        return res

    def find(self, filter: Dict[str, Any] = None):
        res = list(self._sync_col.find(filter or {}))
        return MockAsyncCursor(res)

    async def update_one(self, filter: Dict[str, Any], update: Dict[str, Any], upsert: bool = False):
        res = self._sync_col.update_one(filter, update, upsert=upsert)
        return res

    async def delete_one(self, filter: Dict[str, Any]):
        res = self._sync_col.delete_one(filter)
        return res

    async def count_documents(self, filter: Dict[str, Any] = None):
        return self._sync_col.count_documents(filter or {})


class MockAsyncDatabase:
    def __init__(self):
        self._sync_client = mongomock.MongoClient()
        self._sync_db = self._sync_client[settings.DATABASE_NAME]
        self._collections: Dict[str, MockAsyncCollection] = {}

    def __getitem__(self, name: str) -> MockAsyncCollection:
        if name not in self._collections:
            self._collections[name] = MockAsyncCollection(self._sync_db[name])
        return self._collections[name]

    def get_collection(self, name: str) -> MockAsyncCollection:
        return self[name]


class DatabaseManager:
    client: Optional[AsyncIOMotorClient] = None
    db: Any = None
    is_mock: bool = False

    @classmethod
    async def connect(cls):
        try:
            client = AsyncIOMotorClient(
                settings.MONGODB_URI,
                serverSelectionTimeoutMS=2000,
                connectTimeoutMS=2000
            )
            # Test connection with a quick ping
            await client.admin.command('ping')
            cls.client = client
            cls.db = client[settings.DATABASE_NAME]
            cls.is_mock = False
            logger.info(f"Connected successfully to MongoDB at {settings.MONGODB_URI}")
        except Exception as e:
            if settings.USE_MOCK_DB_IF_UNAVAILABLE:
                logger.warning(
                    f"Could not connect to external MongoDB ({e}). Falling back to in-memory Mongomock store."
                )
                cls.db = MockAsyncDatabase()
                cls.is_mock = True
            else:
                logger.error(f"MongoDB connection failed: {e}")
                raise

    @classmethod
    async def close(cls):
        if cls.client:
            cls.client.close()
            logger.info("Closed MongoDB client connection.")

    @classmethod
    def get_db(cls):
        if cls.db is None:
            # Fallback auto-init if accessed before lifecycle
            cls.db = MockAsyncDatabase()
            cls.is_mock = True
        return cls.db

db_manager = DatabaseManager

