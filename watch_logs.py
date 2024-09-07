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

from parsers import PARSERS


async def watch_file(app: AsyncApp, fname: str, channel_id: str, delay: int, parser: Callable[[str], str]):
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


async def check_channel(app: AsyncApp, channel_id: str):
    """Check if a channel exists (or if the bot has access to it), and if not creates one"""
    api_result = await app.client.conversations_list()
    print(api_result)


async def validate_task(app: AsyncApp, task: dict) -> bool:
    """Check that all the required information is given."""
    for r in ["channel", "logfile", "delay", "parser"]:
        if r not in task.keys():
            raise KeyError(f"Missing required field '{r}'")
    if task["parser"] not in PARSERS.keys():
        raise KeyError(f"Unknown parser {task["parser"]}. Valid parsers are {parsers.PARSERS.keys()}.")
    if not isinstance(task["delay"], int):
        raise TypeError("Delay must be of type int.")
    # Check file exists
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
        logger.info(f"Installing task '{task_name}' to watch '{task['logfile']}'")
        asyncio.ensure_future(
            watch_file(
                app=app,
                fname=task["logfile"],
                channel_id=task["channel"],
                delay=task["delay"],
                parser=PARSERS[task["parser"]],
            )
        )