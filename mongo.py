
from pymongo import MongoClient
import logging


class MongoDB:

    mongo_server_ip = None  # type: str
    mongo_server_port = None  # type: int
    client = None  # type: MongoClient
    database_name = None  # type: str
    configuration = None  # type: dict
    habits = None  # type: str

    def __init__(self, mongo_server_ip: str, database_name: str, configuration: dict, mongo_server_port=27017):
        self.mongo_server_ip = mongo_server_ip
        self.mongo_server_port = mongo_server_port
        self.client = MongoClient(self.mongo_server, self.mongo_port)  # type: pymongo.mongo_client.MongoClient
        self.database_name = database_name
        self.configuration = configuration
        self.habits = configuration['habit_collection_name']

    def get_document(self, collection, document_name: str):

        document = self.client.collection.find({collection: {"$in": document_name}})
        print("Document is type: " + type(document))

        if document.count() > 0:
            if document.count() > 1:
                logging.warning(document_name + " matched more than one document, only returning the first!")
            print("Document[0] is type: " + type(document[0]))
            return document[0]
        else:
            return None

    def create_new_habit(self, habit_id: str):

        collection = self.client[self.habits]

        new_habit = { "_id": habit_id, "total": 1, "difficulty": }

        collection.insert_one()

    def update_habit(self, habit_id):

        collection = self.client[self.habits]
        print("Collection is type: " + type(collection))

        document = self.get_document(collection, habit_id)

        if document is not None:
            print("YAY")
        else:
            print("NO")



