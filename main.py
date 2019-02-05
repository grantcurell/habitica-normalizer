import logging
import yaml
from pprint import pprint
from flask import Flask, request, render_template
from mongo import MongoDB


app = Flask(__name__)

configuration = {}

@app.route('/')
def index():

    players = {}

    for key, value in configuration['user_ids'].items():

        client = MongoDB(configuration, key)

        points = 0
        time = 0
        total_activities = 0

        for habit in client.get_habits():
            points = points + habit['points']
            time = time + time + habit['time']
            total_activities = total_activities + habit['total']

        for daily in client.get_dailies():
            points = points + daily['points']
            time = time + time + daily['time']
            total_activities = total_activities + daily['total']

        # Gets the total number of days
        days = divmod(time, 1440)
        hours = divmod(days[1], 60)
        minutes = hours[1]

        players[key] = {"Username": value['username'], "Total Points": points, "Days": days[0], "Hours": hours[0], "Minutes": minutes, "Total Activities": total_activities}

    pprint(players)

    #for document in 
    return render_template('index.html', players=players)


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

    logging.basicConfig(filename=configuration['log_file'],level=logging.DEBUG)
    
    app.run(host='0.0.0.0')