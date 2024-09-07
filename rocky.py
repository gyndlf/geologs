# -*- coding: utf-8 -*-
"""
Created on Sat Sep 07 19:07 2024

Basic slack bot to send notifications to specific slack channels.

Configure it to read log files for updates and broadcast messages.

@author: james
"""
import logging
logging.basicConfig(level=logging.INFO)

import os
import tomllib
from slack_bolt.app.async_app import AsyncApp
from slack_bolt.adapter.socket_mode.async_handler import AsyncSocketModeHandler
import asyncio
from typing import Callable

import parsers
from commands import COMMANDS

app = AsyncApp(token=os.environ["SLACK_BOT_TOKEN"], process_before_response=True)


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


async def watch_file(fname: str, channel_id: str, delay: int, parser: Callable[[str], str]):
    """Start a loop to watch and send a message for new lines in a log file."""
    # Open the file
    file = open(fname, 'r')
    st_results = os.stat(fname)  # move to the end
    st_size = st_results[6]
    file.seek(st_size)

    while True:  # loop... but do it asynchronously
        where = file.tell()
        line = file.readline()
        if not line:
            await asyncio.sleep(delay)
            file.seek(where)
        else:
            # Something new. Send a message
            print(f"New line: {line}")
            await app.client.chat_postMessage(
                channel=channel_id,
                text=parser(line),
            )


# on @rocky
#@app.event("message")
@app.event("app_mention")
async def handle_mentions(event, client, say):  # async function
    # Check if reacted (and so already has been processed)
    api_response = await client.reactions_get(
        channel=event["channel"],
        timestamp=event["ts"]
    )
    if "reactions" in api_response["message"].keys():
        logger.info(f"Already responded to mention: {event["text"]}")
        return

    logger.info(f"Bot mentioned: {event["text"]}")
    try:
        cmd = event["text"].split(" ")[1]
    except IndexError: # you just pinged me
        api_response = await client.reactions_add(
            channel=event["channel"],
            timestamp=event["ts"],
            name="eyes",
        )
        return

    if cmd not in COMMANDS:  # unknown command
        print(cmd)
        api_response = await client.reactions_add(
            channel=event["channel"],
            timestamp=event["ts"],
            name="thinking_face",
        )
        await say("Unknown command. " + await COMMANDS["help"]())
        return

    api_response = await client.reactions_add(
        channel=event["channel"],
        timestamp=event["ts"],
        name="white_check_mark",
    )
    # Run the command
    await say(await COMMANDS[cmd]())


def validate_task(task: dict) -> bool:
    """Check that all the required information is given."""
    for r in ["channel", "logfile", "delay", "parser"]:
        if r not in task.keys():
            raise KeyError(f"Missing required field '{r}'")
    if task["parser"] not in parsers.PARSERS.keys():
        raise KeyError(f"Unknown parser {task["parser"]}. Valid parsers are {parsers.PARSERS.keys()}.")
    if not isinstance(task["delay"], int):
        raise TypeError("Delay must be of type int.")
    # Check file exists
    if not os.path.exists(task["logfile"]):
        raise FileNotFoundError(f"Could not find log file '{task['logfile']}'")
    return True


def setup_tasks(config: dict):
    """Set up the tasks to watch the appropriate log files."""
    tasks = config.keys()
    for task_name in tasks:
        task = config[task_name]
        validate_task(task)

        # install the task
        logger.info(f"Installing task '{task_name}' to watch '{task['logfile']}'")
        asyncio.ensure_future(
            watch_file(
                fname=task["logfile"],
                channel_id=task["channel"],
                delay=task["delay"],
                parser=parsers.PARSERS[task["parser"]],
            )
        )


async def main():
    setup_tasks(config)
    handler = AsyncSocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
    await handler.start_async()


if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    config = tomllib.load(open("config.toml", "rb"))
    asyncio.run(main())
