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

# Local imports
import watch_logs
from commands import SYSTEM_COMMANDS

app = AsyncApp(token=os.environ["SLACK_BOT_TOKEN"], process_before_response=True)

## Bot commands

logs_running = False

async def logs(*args):
    """Process the logs command"""
    if len(args) == 0:
        if logs_running:
            return ":white_check_mark: " + "Subcommands of `install` and `check``"
        else:
            return ":skull: " + "Subcommands of `install` and `check``"
    elif args[0] == "install":
        # Install the watchers
        pass


async def help(*args):
    """Returns all available commands."""
    msg = (":bulb: *Usage* @BOT [COMMAND] (args)\n_System commands_\n"
           + "\n- ".join([f"`{c}`: {SYSTEM_COMMANDS[c].__doc__}" for c in SYSTEM_COMMANDS.keys()])
           + "\n_Bot commands_\n"
           + "\n- ".join([f"`{c}`: {BOT_COMMANDS[c].__doc__}" for c in BOT_COMMANDS.keys()])
           )
    return msg



BOT_COMMANDS = {
    "logs": logs,
    "help": help,
}


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
        cmd_raw = event["text"].split(" ")
        cmd = cmd_raw[1]
        if len(cmd_raw) > 2:
            cmds = cmd_raw[2:]
        else:
            cmds = []
    except IndexError:  # you just pinged me
        api_response = await client.reactions_add(
            channel=event["channel"],
            timestamp=event["ts"],
            name="eyes",
        )
        return

    if (cmd not in SYSTEM_COMMANDS) and (cmd not in BOT_COMMANDS):  # unknown command
        logger.info(f"Unknown command {cmd}")
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


async def main():
    #setup_tasks(config)
    handler = AsyncSocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
    await handler.start_async()


if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    config = tomllib.load(open("config.toml", "rb"))
    asyncio.run(main())
