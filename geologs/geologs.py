# -*- coding: utf-8 -*-
"""
Created on Sat Sep 07 19:07 2024

Basic slack bot to send notifications to specific slack channels.

Configure it to read log files for updates and broadcast messages.

@author: james
"""
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

import os
import tomllib
from slack_bolt.app.async_app import AsyncApp
from slack_bolt.adapter.socket_mode.async_handler import AsyncSocketModeHandler
import asyncio
import re

# Local imports
from . import watch_logs
from .commands import SYSTEM_COMMANDS

app = AsyncApp(token=os.environ["SLACK_BOT_TOKEN"], process_before_response=True)

__VERSION__ = "0.9"
USERNAME = ""  # populated by who_am_i

## Bot commands

logs_running = False
async def logs(*args):
    """Process the logs command"""
    global logs_running
    if logs_running:
        return ":white_check_mark: Loggers are running."
    else:
        # Install the watchers
        await watch_logs.setup_tasks(app, config)
        logs_running = True
        return "Loggers running"


async def help(*args):
    """Returns all available commands"""
    msg = (":bulb: *Usage* @BOT [COMMAND] (args)\n_System commands_\n"
           + "\n- ".join([f"`{c}`: {SYSTEM_COMMANDS[c].__doc__}" for c in SYSTEM_COMMANDS.keys()])
           + "\n_Bot commands_\n"
           + "\n- ".join([f"`{c}`: {BOT_COMMANDS[c].__doc__}" for c in BOT_COMMANDS.keys()])
           )
    return msg


async def version(*args):
    """Returns the current version"""
    return "Geologs version " + __VERSION__ + ". See https://github.com/gyndlf/geologs"


BOT_COMMANDS = {
    "logs": logs,
    "help": help,
    "version": version,
}


async def who_am_i(app: AsyncApp):
    global USERNAME
    api_result = await app.client.auth_test()
    if "user" in api_result.data:
        USERNAME = api_result["user_id"]
        logger.info(f"Slack username: {api_result['user']} ({USERNAME})")
    else:
        raise RuntimeError("Could not determine bot username")


async def get_if_reacted(channel, timestamp) -> bool:
    """Return if the current bot has reacted to this message."""
    api_response = await app.client.reactions_get(channel=channel, timestamp=timestamp)
    if "reactions" in api_response["message"].keys():
        for emoji in api_response["message"]["reactions"]:
            if USERNAME in emoji["users"]:  # check if we have personally reacted
                return True
    return False


def remove_other_mentions(command: str) -> str:
    """Remove all other bot mentions from the string to call multiple bots."""
    return re.sub(r"<.*?>", "", command).strip()


@app.event("app_mention")
async def handle_mentions(event, client, say):  # async function
    # Check if reacted (and so already has been processed)
    if await get_if_reacted(event["channel"], event["ts"]):
        logger.info(f"Already responded to mention.")
        return

    logger.info(f"Bot mentioned: {event['text']}")
    try:
        cmd_raw = remove_other_mentions(event["text"]).split(" ")
        cmd = cmd_raw[0]
        if len(cmd_raw) > 1:
            cmds = cmd_raw[1:]
        else:
            cmds = []
    except IndexError:
        cmd = ''

    if cmd == '':  # you just pinged me
        api_response = await client.reactions_add(
            channel=event["channel"],
            timestamp=event["ts"],
            name="eyes",
        )
        return

    if (cmd not in SYSTEM_COMMANDS) and (cmd not in BOT_COMMANDS):  # unknown command
        logger.info(f"Unknown command '{cmd}'")
        api_response = await client.reactions_add(
            channel=event["channel"],
            timestamp=event["ts"],
            name="thinking_face",
        )
        await say("Unknown command. " + "Available commands are " + ", ".join(
            [f"`{c}`" for c in SYSTEM_COMMANDS.keys()] + [f"`{c}`" for c in BOT_COMMANDS.keys()]
        ))
        return

    # Command accepted. Run it
    api_response = await client.reactions_add(
        channel=event["channel"],
        timestamp=event["ts"],
        name="thumbsup",
    )
    if cmd in SYSTEM_COMMANDS:  # System command
        try:
            stdout = await SYSTEM_COMMANDS[cmd](*cmds)
        except (FileNotFoundError, RuntimeError) as error:
            # There was an issue completing the command
            api_response = await client.reactions_add(
                channel=event["channel"],
                timestamp=event["ts"],
                name="x",
            )
            logger.error(error)
            await say(":exclamation: Uh oh.```" + str(error) + "```")
            return
        await say(stdout)

    elif cmd in BOT_COMMANDS:  # Bot command
        await say(await BOT_COMMANDS[cmd](*cmds))


async def main_async():
    #setup_tasks(config)
    handler = AsyncSocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
    await who_am_i(app)  # load the bot username
    await handler.start_async()


def main(config_file: str):
    global config
    logger.info("Loading config file from %s", config_file)
    config = tomllib.load(open(config_file, "rb"))
    asyncio.run(main_async())
