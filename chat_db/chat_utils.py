""" Chat utils functions """
import openai
import yaml

def get_first_message():
    """ Return the first message for a new chat """
    return openai.ChatCompletion.create(
        model="gpt-4",
        max_tokens=2000,
        messages=[{
            "role": "system",
            "content": yaml.safe_load(open('./context.yaml', 'r', encoding='utf-8')).get('context')
        }]
    ).choices[0].message.content
