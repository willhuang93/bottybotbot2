from flask import Flask, request
from urllib.parse import quote
import json
import requests

app = Flask(__name__)

# This needs to be filled with the Page Access Token that will be provided
# by the Facebook App that will be created.
# followed by bot info

PAT = 'EAAFKW3kWutoBAP1OBCqr5aYzCffyP88jZCerP3HBLOD89XDvZAcZBcVVLFuaPrgoPpsZBhowQEYkDEM1t4uthbUBZCTk5HwX1SscZCtyZA6oYPQvdfO4ZBqR5iv6Vf8B2lphPDuvZAwlQwV0vf5ZAwexHzcDOUaG2qsostAFOPOAxwOQZDZD'
app_id = '1409614021357'
user_key = '954b5550b8a4a07f7ee98794c9bdbe8d'
botname = 'messengerbot'

@app.route('/', methods=['GET'])
def handle_verification():
  print("Handling Verification.")
  if request.args.get('hub.verify_token', '') == 'my_voice_is_my_password_verify_me':
    print("Verification successful!")
    return request.args.get('hub.challenge', '')
  else:
    print("Verification failed!")
    return 'Error, wrong validation token'

@app.route('/', methods=['POST'])
def handle_messages():
  print("Handling Messages")
  payload = request.get_data()
  print(payload)
  for sender, message in messaging_events(payload):
    print("Incoming from %s: %s" % (sender, message))
    get_reply(PAT, sender, message)
  return "ok"

def messaging_events(payload):
  """Generate tuples of (sender_id, message_text) from the
  provided payload.
  """
  data = json.loads(payload)
  messaging_events = data["entry"][0]["messaging"]
  for event in messaging_events:
    if "message" in event and "text" in event["message"]:
      yield event["sender"]["id"], event["message"]["text"].encode('unicode_escape')
    else:
      yield event["sender"]["id"], "I can't understand this"

def get_reply(token, sender, message):
  # https://aiaas.pandorabots.com/talk/APP_ID/BOTNAME?user_key=USER_KEY&input=INPUT
  print(message)
  print(quote(message, safe = ''))
  message = quote(message, safe = '')
  base_url = 'https://aiaas.pandorabots.com/talk'
  url = '{0}/{1}/{2}?user_key={3}&input={4}&client_name={5}'.format(
    base_url, app_id, botname, user_key, message, sender.lower())

  print(url)
  r = requests.post(url)
  print(r.text)
  print(r.status_code)
  print("\n\n")
  data = json.loads(r.text)
  reply_messages = data["responses"]
  reply = ''

  for message in reply_messages:
    reply += '{0} {1}'.format(reply, message)

  send_message(token, sender, reply)


def send_message(token, recipient, text):
  """Send the message text to recipient with id recipient.
  """

  r = requests.post("https://graph.facebook.com/v2.6/me/messages",
    params={"access_token": token},
    data=json.dumps({
      "recipient": {"id": recipient},
      "message": {"text": text}
    }),
    headers={'Content-type': 'application/json'})
  if r.status_code != requests.codes.ok:
    print(r.text)

if __name__ == '__main__':
  app.run()