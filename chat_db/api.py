""" API for chat db demo """
import os
import openai
import waitress
import yaml
from flask import Flask, request, jsonify

from chat_utils import add_message, load_chat_list_clean, query_gpt

openai.api_key = yaml.safe_load(open('./credentials.yaml', 'r', encoding='utf-8')).get('openai_key')
app = Flask(__name__)

def _success_response():
    """ Return a success response """
    response = jsonify({'result': 'success'})
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route('/new_chat')
def new_chat():
    """ Starts a new chat """
    if not os.path.isfile('chat.json'):
        add_message(
            'system',
            'assistant',
            yaml.safe_load(open('./context.yaml', 'r', encoding='utf-8')).get('context')
        )
        query_gpt()
    return _success_response()

@app.route('/send_message', methods=['GET'])
def send_message():
    """ Send a new message to the chat """
    add_message('user', 'assistant', request.args.get('message'))
    query_gpt()
    return _success_response()

@app.route('/load_chat', methods=['GET'])
def load_chat():
    """ Check if there is a new message in the chat """
    response = jsonify(load_chat_list_clean())
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

waitress.serve(app, host='localhost', port=5000)
