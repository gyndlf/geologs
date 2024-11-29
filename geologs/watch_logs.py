# -*- coding: utf-8 -*-
"""
Created on Sun Sep 08 07:58 2024

Command and methods for subscribing to watch a log file

@author: james
"""

import asyncio
from typing import Callable
import os
import logging
from slack_bolt.app.async_app import AsyncApp


logger = logging.getLogger(__name__)

from .parsers import PARSERS


# Channel topic to set
TOPIC = "Listening to logs! :notes:"


async def watch_file(app: AsyncApp, fname: str, channel_id: str, delay: int, parser: Callable[[str], str]):
    """Start a loop to watch and send a message for new lines in a log file."""
    # Open the file
    file = open(fname, 'r')
    st_results = os.stat(fname)  # move to the end
    st_size = st_results[6]
    file.seek(st_size)

    while True:  # loop... but do it asynchronously
        where = file.tell()
        line = file.readline().strip()
        if not line:
            await asyncio.sleep(delay)
            file.seek(where)
        else:
            # Something new. Send a message
            logger.info(f"Log '{fname}' updated, sending '{line}'")
            await app.client.chat_postMessage(
                channel=channel_id,
                text=parser(line),
            )


async def watch_process(app: AsyncApp, cmd: str, channel_id: str, delay: int, parser: Callable[[str], str]):
    """Start a process and parse the output as a message to a specific channel"""
    # Open the process
    proc = await asyncio.create_subprocess_exec(
        *cmd.split(),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    while True:
        stdout_data = await proc.stdout.readline()
        stdout = stdout_data.decode('utf-8').strip()

        if stdout:
            logger.info(f"Log '{cmd}' updated, sending '{stdout}'")
            await app.client.chat_postMessage(
                channel=channel_id,
                text=parser(stdout),
            )
        if proc.returncode is not None:
            logger.info("Command finished.")
            break


async def check_channel(app: AsyncApp, channel_id: str):
    """Check if a channel exists (or if the bot has access to it), and if not creates one"""
    api_result = await app.client.conversations_list()
    channel_id = channel_id.strip("#")
    for channel in api_result["channels"]:
        if channel["id"] == channel_id or channel["name"] == channel_id.replace("#", ""):
            # Valid channel
            api_result = await app.client.conversations_join(
                channel=channel["id"],
            )
            if api_result["channel"]["topic"]["value"] != TOPIC:
                logger.info(f"Updated channel #{channel['name']} topic")
                api_result = await app.client.conversations_setTopic(
                    channel=channel["id"],
                    topic=TOPIC
                )
            return
    # No channel exists. Make one
    api_result = await app.client.conversations_create(
        name=channel_id
    )
    api_result = await app.client.conversations_join(
        channel=api_result["channel"]["id"],
    )
    api_result = await app.client.conversations_setTopic(
        channel=api_result["channel"]["id"],
        topic="Listening to logs! (Rock music :notes:)"
    )


async def validate_task(app: AsyncApp, task: dict) -> bool:
    """Check that all the required information is given."""
    for r in ["channel", "delay", "parser"]:
        if r not in task.keys():
            raise KeyError(f"Missing required field '{r}'")
    if "logfile" in task.keys() != "logcmd" in task.keys():
        raise KeyError("Either 'logfile' or 'logcmd' must be present but not both.")
    if task["parser"] not in PARSERS.keys():
        raise KeyError(f"Unknown parser {task['parser']}. Valid parsers are {PARSERS.keys()}.")
    if not isinstance(task["delay"], int):
        raise TypeError("Delay must be of type int.")
    if "logfile" in task.keys():  # Check file exists if applicable
        if not os.path.exists(task["logfile"]):
            raise FileNotFoundError(f"Could not find log file '{task['logfile']}'")
    await check_channel(app, task["channel"])
    return True


async def setup_tasks(app: AsyncApp, config: dict):
    """Set up the tasks to watch the appropriate log files."""
    tasks = config.keys()
    for task_name in tasks:
        task = config[task_name]
        await validate_task(app, task)
        # install the task
        if "logfile" in task.keys():  # a file based task
            logger.info(f"Installing file task '{task_name}' to watch '{task['logfile']}'")
            api_result = await app.client.chat_postMessage(
                channel=task["channel"],
                text=f":open_file_folder: :file_cabinet: Subscribed to logs from `{task['logfile']}`"
            )
            asyncio.ensure_future(
                watch_file(
                    app=app,
                    fname=task["logfile"],
                    channel_id=task["channel"],
                    delay=task["delay"],
                    parser=PARSERS[task["parser"]],
                )
            )
        else:
            logger.info(f"Installing process task '{task_name}' to watch '{task['logcmd']}'")
            api_result = await app.client.chat_postMessage(
                channel=task["channel"],
                text=f":open_file_folder: :electric_plug: Subscribed to logs from `{task['logcmd']}`"
            )
            asyncio.ensure_future(
                watch_process(
                    app=app,
                    cmd=task["logcmd"],
                    channel_id=task["channel"],
                    delay=task["delay"],
                    parser=PARSERS[task["parser"]],
                )
            )

