"""MongoDB CRUD helper for the Animal Shelter project."""

import os

from pymongo import MongoClient
from pymongo.errors import PyMongoError
from urllib.parse import quote_plus


class AnimalShelter:
    """Basic create, read, update, and delete methods for animal records."""

    def __init__(self, username=None, password=None):
        username = username or os.getenv("MONGO_USER")
        password = password or os.getenv("MONGO_PASSWORD")
        host = os.getenv("MONGO_HOST", "localhost")
        port = int(os.getenv("MONGO_PORT", "27017"))
        db_name = os.getenv("MONGO_DB", "aac")
        collection_name = os.getenv("MONGO_COLLECTION", "animals")
        auth_source = os.getenv("MONGO_AUTH_SOURCE", db_name)

        # Use the local MongoDB instance when credentials aren't needed.
        if username and password:
            uri = (
                f"mongodb://{quote_plus(username)}:{quote_plus(password)}@"
                f"{host}:{port}/{db_name}?authSource={quote_plus(auth_source)}"
            )
        elif not username and not password:
            uri = f"mongodb://{host}:{port}/"
        else:
            raise ValueError("Set both MONGO_USER and MONGO_PASSWORD, or neither.")

        self.client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        self.database = self.client[db_name]
        self.collection = self.database[collection_name]

    def create(self, data):
        if not isinstance(data, dict) or not data:
            return False
        try:
            self.collection.insert_one(data)
            return True
        except PyMongoError:
            return False

    def read(self, query):
        if not isinstance(query, dict):
            return []
        try:
            return list(self.collection.find(query))
        except PyMongoError:
            return []

    def update(self, query, new_values):
        if not isinstance(query, dict) or not query or not isinstance(new_values, dict) or not new_values:
            return 0
        try:
            return self.collection.update_many(query, {"$set": new_values}).modified_count
        except PyMongoError:
            return 0

    def delete(self, query):
        if not isinstance(query, dict) or not query:
            return 0
        try:
            return self.collection.delete_many(query).deleted_count
        except PyMongoError:
            return 0
