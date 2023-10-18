""" Chat utils functions """
import os
import sqlite3
import json
from typing import Dict, List
import openai

def load_chat_list() -> List[Dict[str, str]]:
    """ Load the chat from the chat.json file """
    if os.path.isfile('chat.json'):
        return json.load(open('./chat.json', 'r', encoding='utf-8'))
    return []

def load_chat_list_clean() -> List[Dict[str, str]]:
    """ Load the chat from the chat.json file with clean messages """
    chat = load_chat_list()
    to_append_messages = {}
    for i, message in enumerate(chat):
        if isinstance(message.get('content'), dict):
            if 'to_system' in message.get('content'):
                to_append_messages[i] = message.get('content').get('to_system')
            if 'to_user' in message.get('content'):
                message['content'] = message.get('content').get('to_user')
    for key, value in reversed(to_append_messages.items()):
        chat.insert(key, {'from': 'assistant', 'to': 'system', 'content': value})
    return chat

def add_message(sender, to, message):
    """ Add a message to the chat """
    chat = load_chat_list()
    chat.append({
        'from': sender,
        'to': to,
        'content': message
    })
    json.dump(chat, open('./chat.json', 'w', encoding='utf-8'))

def query_db(query) -> str:
    """ Query the database """
    con = sqlite3.connect("company_data.db")
    cur = con.cursor()
    res = cur.execute(query)
    return str(res.fetchall())

def query_gpt():
    """ Query the GPT """
    response = openai.ChatCompletion.create(
        model="gpt-4",
        max_tokens=2000,
        messages=[
            *[{
                'role': message.get('from'),
                'content': json.dumps(message.get('content')) if\
                    isinstance(message.get('content'), dict) else message.get('content')
            } for message in load_chat_list()]
        ]
    ).choices[0].message.content
    print(response)
    try:
        response = json.loads(response)
    except json.decoder.JSONDecodeError:
        response = {'to_user': response}

    add_message('assistant', 'user', response)
    if response.get('to_system'):
        if not response.get('to_system').upper().startswith('FINISHED'):
            add_message('system', 'assistant', query_db(response.get('to_system')))
            query_gpt()
