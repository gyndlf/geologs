# -*- coding: utf-8 -*-
"""
Created on Sat Sep 07 17:48 2024

Basic slack bot to send notifications to specific slack channels.

Configure it to read log files for updates and broadcast messages.

@author: james
"""

import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler


#print(os.environ.get('JAMES'))


app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

# async def ack_check_command(body, ack):
#     text = body.get("text")
#     if text is None or len(text) == 0:
#         await ack(f":x: Usage: /check [service]")
#     else:
#         await ack(f"Accepted! (task: {body['text']})")
#
#
# async def check_health(respond, body):
#     await asyncio.sleep(8)
#     await respond(f"Healthy!! (task: {body['text']})")
#
#
# app.command("/check")(
#     # ack() is still called within 3 seconds
#     ack=ack_check_command,
#     # Lazy function is responsible for processing the event
#     lazy=[check_health]
# )

# Listens to incoming messages that contain "hello"
@app.message("hello")
def message_hello(message, say):
    # say() sends a message to the channel where the event was triggered
    #say(f"Hey there <@{message['user']}>!")
    say(
        blocks=[
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"Hey there <@{message['user']}>!"},
                "accessory": {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "Click Me"},
                    "action_id": "button_click"
                }
            }
        ],
        text=f"Hey there <@{message['user']}>!"
    )


@app.action("button_click")
def action_button_click(body, ack, say):
    # Acknowledge the action
    ack()
    say(f"<@{body['user']['id']}> clicked the button")


@app.event("app_mention")
def handle_app_mention_events(body, logger):
    print(body)
    logger.info(body)
    logger("heeonfdf")


@app.event("message")
def handle_message_events(body, logger):
    print(body)
    logger.info(body)


@app.command("/check")
def check_command(ack, respond, command):
    ack()
    respond("Looking good... maybe")
    print(f"Attempting to get the status of the server {command}")


if __name__ == "__main__":
    #app.start(port=int(os.environ.get("PORT", 3000)))
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()
