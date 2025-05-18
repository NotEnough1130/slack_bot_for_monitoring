import re
from datetime import datetime
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

SLACK_BOT_TOKEN = "xxx" #token for authenticate to workspace
SLACK_APP_TOKEN = "xxx" #token for allow this app to use platform feature (slack event API)

app = App(token=SLACK_BOT_TOKEN)

#Dict to translate channel id and name
dict_channel_id={
    'C08SFMKQZKR' : '#system-log'
}

dict_channel_name={
    '#system-log' : 'C08SFMKQZKR'
}

#Step to ackowneldge app support
def ack_app_support(channel, ts, text, client):
    client.reactions_add(
            channel=channel,
            name="eyes",
            timestamp=ts
        )
    client.chat_postMessage(channel='#app-support-request-logs', text=f'{dict_channel_id[channel]}: {text} {datetime.today().strftime('%d-%m-%Y %H:%M:%S')}')
    client.chat_postMessage(channel=channel, text=f'app support has been ack of this issue, stay turn!')
    return 0

#Funtion to handle message in #system-log channel
def handle_risk_system_error(text, channel, ts, client):
    rm_pattern = r"Risk system report process on (\d{4}-\d{2}-\d{2}) \[[A-Z]{3}\] completed successfully"
    clear_text=re.sub(r"[^A-Za-z ]", "", text.lower())
    if re.search(rm_pattern.lower(), text.lower()):
        return client.reactions_add(
            channel=channel,
            name="white_check_mark",
            timestamp=ts
        )
    elif str('unsuccessfully') in clear_text:
        return ack_app_support(channel, ts, text, client)
    else:
        return 0

#divide body message from API to usful information
def get_info(body):
    event = body.get("event", {})
    channel = event.get("channel")
    ts = event.get("ts")
    text = event.get("text")
    return channel, ts, text

#all message route
@app.event("message")
def handle_message_events(body, logger, client):
    channel, ts, text = get_info(body)
    if channel==dict_channel_name['#system-log']:
        return handle_risk_system_error(text, channel, ts, client)
    return 0

#app_mention route 
@app.event("app_mention")
def handle_mention_events(body, logger, client):
    channel, ts, text = get_info(body)
    return ack_app_support(channel, ts, text, client)

if __name__ == "__main__":
    handler = SocketModeHandler(app, SLACK_APP_TOKEN)
    handler.start()
