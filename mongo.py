
from pymongo import MongoClient, database, mongo_client, cursor
import datetime


class MongoDB:

    mongo_ip = None  # type: str
    mongo_port = None  # type: int
    client = None  # type: MongoClient
    configuration = None  # type: dict

    @staticmethod
    def priority_to_difficulty(priority: int) -> (str, int):
        if priority == 2:
            return "Hard", 100
        elif priority == 1.5:
            return "Medium", 75
        elif priority == 1:
            return "Easy", 50
        elif priority == 0.1:
            return "Trivial", 25
        else:
            return None

    @staticmethod
    def create_new_habit_or_daily(habit_id: str, name: str, total: int, difficulty: (str, int), time,
                                  collection: database.Database):

        new_habit = {"_id": habit_id, "name": name, "total": total, "difficulty": difficulty[0],
                     "points": difficulty[1], "time": time}

        return collection.insert_one(new_habit)

    def __init__(self, configuration: dict, database_name: str):
        self.mongo_ip = configuration['mongo_server']
        self.mongo_port = configuration['mongo_server_port']
        self.configuration = configuration
        self.client = MongoClient(self.mongo_ip, self.mongo_port)[database_name]  # type: mongo_client.MongoClient

    def get_habits(self) -> cursor.Cursor:
        return self.client['habits'].find()

    def get_dailies(self) -> cursor.Cursor:
        return self.client['dailies'].find()

    def update_habit(self, habitdaily: dict, is_habit: bool):

        habitdaily_id = habitdaily['id']
        habitdaily_name = habitdaily['text']
        habitdaily_difficulty = MongoDB.priority_to_difficulty(habitdaily['priority'])
        habitdaily_time = 20

        if is_habit:
            collection = self.client['habits']  # type: database.Database
        else:
            collection = self.client['dailies']  # type: database.Database

        document = collection.find_one({"_id": habitdaily_id})

        if self.configuration['user_ids'][habitdaily['userId']]['username'] == "foozand" and \
                datetime.datetime.today().weekday() < 5:
            habitdaily_time = 30

        if habitdaily_name.lower() == 'work':
            habitdaily_time = 60

        if document is not None:
            document_query = {"_id": document['_id']}

            # Update total
            collection.update_one(document_query, {"$set": {"total": document['total'] + 1}})

            # Update total points
            collection.update_one(document_query, {"$set": {"points": document['points'] + habitdaily_difficulty[1]}})

            # Update total time
            collection.update_one(document_query, {"$set": {"time": document['time'] + habitdaily_time}})

        else:

            MongoDB.create_new_habit_or_daily(habitdaily_id, habitdaily_name, 1, habitdaily_difficulty, habitdaily_time, collection)



