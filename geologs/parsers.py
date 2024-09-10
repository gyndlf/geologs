# -*- coding: utf-8 -*-
"""
Created on Sat Sep 07 20:14 2024

Simple parsers to make the log files look pretty.

@author: james
"""


def _log_level_to_emoji(level: str) -> str:
    """Conver the log level to an emoji"""
    l = level.lower().strip()
    if l == "debug":
        return ":bug: "
    elif l == "info":
        return ":mag: "
    elif l == "warning" or l == "warn":
        return ":warning: "
    elif l == "error":
        return ":x: "
    else:
        return ":grey_question: "


def basic(message: str) -> str:
    """Do nothing"""
    return message


def monty(message: str) -> str:
    """Parse message output from monty"""
    comps = message.split(" ")
    if len(comps) < 4:
        return message  # corrupted format
    if "start" in message.lower():
        return _log_level_to_emoji(comps[2]) + ":large_green_circle: " + " ".join(comps[3:])
    elif "end" in message.lower() or "finish" in message.lower():
        return _log_level_to_emoji(comps[2]) + ":octagonal_sign: " + " ".join(comps[3:])
    else:
        return _log_level_to_emoji(comps[2]) + " ".join(comps[3:])


PARSERS = {
    "basic": basic,
    "monty": monty,
}


if __name__ == "__main__":
    print(monty("[2024-09-10 11:28:44,276] INFO Run finished and took 3 seconds"))
