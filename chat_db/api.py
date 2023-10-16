""" API for chat db demo """
import openai
import waitress
import yaml
from flask import Flask, json, request, jsonify

from chat_utils import get_first_message

openai.api_key = yaml.safe_load(open('./credentials.yaml', 'r', encoding='utf-8')).get('openai_key')
app = Flask(__name__)

@app.route('/new_chat')
def new_chat():
    """ Starts a new chat """

    message = get_first_message()

    json.dump({
        'role': 'assistant',
        'to': 'user',
        'content': message
    }, open('./chat.json', 'w', encoding='utf-8'))

    response = jsonify({'message': message})
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route('/send_message', methods=['GET'])
def send_message():
    """ Send a new message to the chat """
    message = request.args.get('message')

    #TODO

    response = jsonify({'result': 'success'})
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route('/check_message', methods=['GET'])
def check_message():
    """ Check if there is a new message in the chat """
    chat = json.load(open('./chat.json', 'r', encoding='utf-8'))
    if chat.get('role') == 'assistant' and chat.get('to') == 'user':
        response = jsonify({'message': chat.get('content')})
    else:
        response = jsonify({'message': None})
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

waitress.serve(app, host='localhost', port=5000)
