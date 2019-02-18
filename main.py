import logging
import yaml
from pprint import pprint
from flask import Flask, request, render_template
from mongo import MongoDB
from elasticsearch import Elasticsearch


app = Flask(__name__)

configuration = {}

@app.route('/')
def index():

    logging.info("Received request for index page.")

    players = {}

    for key, value in configuration['user_ids'].items():

        client = MongoDB(configuration, key)

        points = 0
        time = 0
        work_time = 0
        total_activities = 0

        for habit in client.get_habits():

            points = points + habit['points']
            total_activities = total_activities + habit['total']

            if habit['name'].lower() == 'work':
                work_time = work_time + habit['time']
                continue
            
            time = time + habit['time']
            
        for daily in client.get_dailies():
            points = points + daily['points']
            time = time + daily['time']
            total_activities = total_activities + daily['total']

        logging.debug("Calculated time to be: " + str(time))

        total_time = work_time + time

        # Gets the total number of days
        days = divmod(time, 1440)
        hours = divmod(days[1], 60)
        minutes = hours[1]

        work_days = divmod(work_time, 1440)
        work_hours = divmod(work_days[1], 60)

        players[key] = {"Username": value['username'], "Total Points": points, "Hobby Days": days[0], "Hobby Hours": hours[0], "Hobby Minutes": minutes, "Work Days": work_days[0], "Work Hours": work_hours[0], "Total Activities": total_activities}

    logging.debug(pprint(players))

    return render_template('index.html', players=players)


@app.route('/taskevent', methods=['POST'])
def webhook():

    habitica_update = request.json  # type: dict

    logging.info("Received update")

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

        es = Elasticsearch([{'host': configuration['elasticsearch_server'], 'port': configuration['elasticsearch_port']}])

        logging.info("Pushing event to Elasticsearch")

        res = es.index(index="test-index", doc_type='_doc', body=habitica_update)
        
        logging.debug("Elasticsearch returned " + str(res['result']))

    return '', 200


if __name__ == "__main__":

    with open('config.yml', 'r') as config:
        configuration = yaml.load(config)  # type: dict

    logging.basicConfig(filename=configuration['log_file'],level=logging.DEBUG)
    
    app.run(host='0.0.0.0')