import logging
import yaml
from pprint import pprint
from flask import Flask, request
from mongo import MongoDB


app = Flask(__name__)

configuration = {}


@app.route('/taskevent', methods=['POST'])
def webhook():

    habitica_update = request.json  # type: dict
    pprint(habitica_update)

    if habitica_update['direction'] != "down":

        client = MongoDB(configuration, habitica_update['task']['userId'])

        if habitica_update['task']['type'] == "daily":
            logging.info("Received a daily task and we are now processing.")
            client.update_habit(habitica_update['task'], False)
        elif habitica_update['task']['type'] == "habit":
            logging.info("Received a habit and we are now processing.")
            client.update_habit(habitica_update['task'], True)
        else:
            logging.error("Received an unrecognized task type.")

    return '', 200


if __name__ == "__main__":
    with open('config.yml', 'r') as config:
        configuration = yaml.load(config)  # type: dict
    app.run(host='0.0.0.0')