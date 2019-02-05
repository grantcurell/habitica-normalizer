import requests
import sys
import json
import os
import logging
import yaml
from pprint import pprint
from elasticsearch import Elasticsearch
from flask import Flask, request


app = Flask(__name__)

configuration = {}


def process_habit(habit_id: str, user_id: str):
    headers = {
        'Content-Type': 'application/json',
        'x-api-user': user_id,
        'x-api-key': configuration['user_ids'][user_id]['api_key'],
    }

    response = requests.get('https://habitica.com/api/v3/tasks/' + habit_id, headers=headers)  # type: requests.models.Response

    habit_data = response.json()  # type: dict
    pprint(habit_data)
    data = habit_data['data']  # type: list


def process_daily(daily_id: str):
    print("NO")


@app.route("/")
def index():
    return "Hello World!"


@app.route('/taskevent', methods=['POST'])
def webhook():
    habitica_update = request.json  # type: dict
    pprint(habitica_update)

    if habitica_update['task']['type'] == "daily":
        logging.info("Received a daily task and we are now processing.")
        process_daily(habitica_update['task']['id'], habitica_update['task']['userId'])
    elif habitica_update['task']['type'] == "habit":
        logging.info("Received a habit and we are now processing.")
        process_habit(habitica_update['task']['id'], habitica_update['task']['userId'])
    else:
        logging.error("Received an unrecognized task type.")

    return '', 200


def main():
    headers = {
        'Content-Type': 'application/json',
        'x-api-user': '80a78d03-1d42-43c7-9d5a-5de4dd7d923c',
        'x-api-key': 'c291fa23-61d1-4aae-9670-64a3d94591ab',
        "type" : 'dailys',
    }


    response = requests.get('https://habitica.com/api/v3/tasks/user', headers=headers)  # type: requests.models.Response

    json_response = response.json()  # type: dict

    data = json_response['data']  # type: list

    #print(type(data))

    #pprint(data)

    for habit_or_task in data:

        #if
        if habit_or_task['type'] == "daily":
            process_daily(habit_or_task)


    #es = Elasticsearch([{'host': '192.168.1.10', 'port': '9200'}])

    #if es.indices.exists(index="index"):
    #    print("YES")


if __name__ == "__main__":
    with open('config.yml', 'r') as config:
        configuration = yaml.load(config)  # type: dict
    app.run(host='0.0.0.0')