import os
from dotenv import load_dotenv
from flask import Flask, request
from pymessenger.bot import Bot
import hyphenate

# load env
load_dotenv()
ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
VERIFY_TOKEN = os.getenv('VERIFY_TOKEN')

# Flask setup
app = Flask(__name__)
bot = Bot(ACCESS_TOKEN)


# We will receive messages that Facebook sends our bot at this endpoint
@app.route("/", methods=['GET', 'POST'])
def receive_message():
    if request.method == 'GET':
        """Before allowing people to message your bot, Facebook has implemented a verify token
        that confirms all requests that your bot receives came from Facebook."""
        token_sent = request.args.get("hub.verify_token")
        return verify_fb_token(token_sent)
    if request.method == 'POST':
        payload = request.json
        event = payload['entry'][0]['messaging']
        for x in event:
            if is_user_message(x):
                text = x['message']['text']
                sender_id = x['sender']['id']
                reply = good_word(text)
                if reply:
                    reply = f'{reply}? I hardly know her!'
                    send_message(sender_id, reply)
    return "Message Processed"


def verify_fb_token(token_sent):
    # take token sent by facebook and verify it matches the verify token you sent
    # if they match, allow the request, else return an error
    if token_sent == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return 'Invalid verification token'


# check for message from user (and not the bot)
def is_user_message(message):
    """Check if the message is a message from the user"""
    return (message.get('message') and
            message['message'].get('text') and
            not message['message'].get("is_echo"))


# if message contains a funny word, return that word if it has more than one syllable. otherwise return None
def good_word(text: str):
    words = text.split()
    for word in words:
        if word[-1].lower == 'a' or word[-2:].lower() in ('er', 'or', 'ar') or word[-3:].lower in ('eur', 'ure'):
            if len(hyphenate.hyphenate_word(word)) > 0:
                return word.lower()
    return None


# uses PyMessenger to send response to user
def send_message(recipient_id, response):
    # sends user the text message provided via input response parameter
    bot.send_text_message(recipient_id, response)
    return "success"


if __name__ == "__main__":
    app.run()
