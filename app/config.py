"""Configuration module for DormBox application."""
from functools import lru_cache
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")guration module for DormBox application."""
from functools import lru_cache
from typing import Optional
from pydantic_settings import BaseSettings
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    mongodb_uri: str = "mongodb://localhost:27017"
    mongodb_db: str = "dormbox"
    app_name: str = "DormBox"
    amazon_url_timeout: float = 5.0
    rate_limit_per_minute: int = 60
    jwt_secret: str = "replace_with_secure_secret_in_production"
    jwt_algorithm: str = "HS256"
    jwt_expiry_minutes: int = 30
    api_prefix: str = "/api/v1"

    class Config:
        env_file = ".env"

@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings()

class Database:
    """Database connection manager."""
    client: Optional[AsyncIOMotorClient] = None
    db: Optional[AsyncIOMotorDatabase] = None

    @classmethod
    def get_db(cls) -> AsyncIOMotorDatabase:
        """Get database instance."""
        if cls.db is None:
            settings = get_settings()
            cls.client = AsyncIOMotorClient(
                settings.mongodb_uri,
                uuidRepresentation="standard"
            )
            cls.db = cls.client[settings.mongodb_db]
        return cls.db

    @classmethod
    async def close_db(cls):
        """Close database connection."""
        if cls.client is not None:
            cls.client.close()
            cls.client = None
            cls.db = None

# Create indexes on startup
async def init_indexes():
    """Initialize database indexes."""
    db = Database.get_db()
    
    # Boxes indexes
    await db.boxes.create_index([("workspaceId", 1)])
    await db.boxes.create_index([("qrSlug", 1)], unique=True)
    await db.boxes.create_index([("status", 1)])
    
    # Items indexes
    await db.items.create_index([("workspaceId", 1)])
    await db.items.create_index([("boxId", 1)])
    await db.items.create_index([("bundleIds", 1)])
    await db.items.create_index([("title", "text")])
    await db.items.create_index([("category", 1)])
    await db.items.create_index([("status", 1)])
    
    # Bundles indexes
    await db.bundles.create_index([("workspaceId", 1)])
    await db.bundles.create_index([("name", 1)])