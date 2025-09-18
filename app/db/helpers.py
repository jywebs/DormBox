"""Database helper functions."""
from datetime import datetime
from typing import Any, Dict, List, Optional
from bson import ObjectId

from app.config import Database
from app.models.box import Box, BoxCreate, BoxUpdate
from app.models.item import Item, ItemCreate, ItemUpdate
from app.models.bundle import Bundle, BundleCreate, BundleUpdate

class DBHelper:
    """Database helper functions."""

    @staticmethod
    def _prepare_find_query(
        workspace_id: str,
        filters: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Prepare a MongoDB find query with workspace filtering."""
        query = {"workspaceId": workspace_id}
        if filters:
            query.update(filters)
        return query

    @staticmethod
    async def create_document(
        collection: str,
        workspace_id: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a new document in the specified collection."""
        now = datetime.utcnow()
        doc = {
            "workspaceId": workspace_id,
            "createdAt": now,
            "updatedAt": now,
            **data
        }
        result = await Database.get_db()[collection].insert_one(doc)
        doc["_id"] = str(result.inserted_id)
        return doc

    @staticmethod
    async def find_document(
        collection: str,
        workspace_id: str,
        doc_id: str
    ) -> Optional[Dict[str, Any]]:
        """Find a document by ID in the specified collection."""
        try:
            doc = await Database.get_db()[collection].find_one({
                "_id": ObjectId(doc_id),
                "workspaceId": workspace_id
            })
            if doc:
                doc["_id"] = str(doc["_id"])
            return doc
        except:
            return None

    @staticmethod
    async def update_document(
        collection: str,
        workspace_id: str,
        doc_id: str,
        update_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Update a document in the specified collection."""
        try:
            now = datetime.utcnow()
            update_data["updatedAt"] = now
            result = await Database.get_db()[collection].find_one_and_update(
                {
                    "_id": ObjectId(doc_id),
                    "workspaceId": workspace_id
                },
                {"$set": update_data},
                return_document=True
            )
            if result:
                result["_id"] = str(result["_id"])
            return result
        except:
            return None

    @staticmethod
    async def delete_document(
        collection: str,
        workspace_id: str,
        doc_id: str
    ) -> bool:
        """Delete a document from the specified collection."""
        try:
            result = await Database.get_db()[collection].delete_one({
                "_id": ObjectId(doc_id),
                "workspaceId": workspace_id
            })
            return result.deleted_count > 0
        except:
            return False

    @staticmethod
    async def list_documents(
        collection: str,
        workspace_id: str,
        filters: Dict[str, Any] = None,
        skip: int = 0,
        limit: int = 25,
        sort: List[tuple] = None
    ) -> List[Dict[str, Any]]:
        """List documents from the specified collection."""
        query = DBHelper._prepare_find_query(workspace_id, filters)
        cursor = Database.get_db()[collection].find(query)
        
        if sort:
            cursor = cursor.sort(sort)
        
        cursor = cursor.skip(skip).limit(min(limit, 100))
        
        docs = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            docs.append(doc)
        
        return docs