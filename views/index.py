# /index.py
from flask import Flask, request, jsonify, render_template
import os
import dialogflow
import requests
import json, jsonpickle
import pusher
import export

template_dir = os.path.abspath('templates')
static_dir = os.path.abspath('static')
app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)

@app.route('/')
def index():
    export.run_export()
    return render_template('index.html')

# run Flask app
if __name__ == "__main__":
    app.run()
    

def detect_intent_texts(project_id, session_id, text, language_code):
    session_client = dialogflow.SessionsClient()
    session = session_client.session_path(project_id, session_id)

    if text:
        text_input = dialogflow.types.TextInput(
            text=text, language_code=language_code)
        query_input = dialogflow.types.QueryInput(text=text_input)
        response = session_client.detect_intent(
            session=session, query_input=query_input)
        return response.query_result.fulfillment_text


@app.route('/send_message', methods=['POST'])
def send_message():
    message = request.form['message']
    project_id = os.getenv('DIALOGFLOW_PROJECT_ID')
    fulfillment_text = detect_intent_texts(project_id, "unique", message, 'en')
    response_text = { "message":  fulfillment_text }
    
    return jsonify(response_text)


@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json(silent=True)
    with open('output/all_output.json') as f:
        canvas_data = json.load(f)[0]
    
    if data['queryResult']['intent']['displayName'] == 'Announcements':
        reply = {
            "fulfillmentText": canvas_data['announcements'][0]['body'],
        }

    elif data['queryResult']['intent']['displayName'] == 'Assignments':
        response = 'Title: '+ canvas_data['assignments'][0]['title'] +"Due Date: "+ canvas_data['assignments'][0]['due_date']
        reply = {
            "fulfillmentText": response,
        }
    elif data['queryResult']['intent']['displayName'] == 'Submission':
        response = 'Grade: '+ canvas_data['assignments'][0]['submission']['grade']
        reply = {
            "fulfillmentText": response,
        }
    elif data['queryResult']['intent']['displayName'] == 'Discussion':
        response = 'Recent Discussions: '+ canvas_data['discussions'][0]['body']
        reply = {
            "fulfillmentText": response,
        }
   
    elif data['queryResult']['intent']['displayName'] == 'Lectures':
        reply = {
                "fulfillmentText": "What course are you looking for?",
        }
    elif data['queryResult']['intent']['displayName'] == 'LecturesName':
        reply = {
                "fulfillmentText": "What phrase you want us to search?",
        }
    elif data['queryResult']['intent']['displayName'] == 'LectureWordSearch':
        f = open('/Users/hamzamohiuddin/RUHack2021/views/LectureText/CPS100_CGEO793 Lecture 1.txt', "r")
        contents = f.read
        courseCodeUserInput = data['queryResult']['queryText']

        with open('/Users/hamzamohiuddin/RUHack2021/views/LectureText/CPS100_CGEO793 Lecture 1.txt','r') as fd: 
            if courseCodeUserInput in fd.read(): 
                response = 'This topic is present in the following lecture files - ' + canvas_data['modules'][0]['items'][0]['title']
            else:
                response = "FAILURE"
        reply = {
                "fulfillmentText": response, 
            }
            
    return jsonify(reply)    
