from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorCollection


class Database:
    client: AsyncIOMotorClient | None = None
    db: AsyncIOMotorDatabase | None = None
    collection: AsyncIOMotorCollection | None = None

    async def connect(self) -> None:
        try:
            self.client = AsyncIOMotorClient(
                self._mongodb_url, serverSelectionTimeoutMS=2000
            )
            self.db = self.client[self._db_name]
            self.collection = self.db[self._collection_name]
        except Exception:
            self.client = None
            self.db = None
            self.collection = None

    async def disconnect(self) -> None:
        if self.client:
            self.client.close()

    async def is_healthy(self) -> bool:
        try:
            if self.client is None:
                return False
            await self.client.admin.command("ping")
            return True
        except Exception:
            return False

    def configure(self, mongodb_url: str, db_name: str, collection_name: str) -> None:
        self._mongodb_url = mongodb_url
        self._db_name = db_name
        self._collection_name = collection_name


database = Database()
