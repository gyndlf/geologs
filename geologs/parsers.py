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


def ssh(message: str) -> str:
    """Parse message from sshd."""
    comps = message.split(" ")
    date = " ".join(comps[0:3])
    log = " ".join(comps[5:])

    icon = " "
    if "accepted publickey" in message.lower():
        # Confirmation of public key
        icon = " :key: "
    elif "session opened" in message.lower():
        # Creation of a new session
        icon = " :satellite_antenna: "
    elif "error: kex_exchange_identification" in message.lower():
        # Probably malicious port scanning
        icon = " :warning: "
    elif "invalid format" in message.lower():
        # Most likely someone using HTTP scanning
        icon = " :military_helmet: "

    return date + icon + log


PARSERS = {
    "basic": basic,
    "monty": monty,
    "ssh": ssh,
}


if __name__ == "__main__":
    print(monty("[2024-09-10 11:28:44,276] INFO Run finished and took 3 seconds"))
    print(ssh("Sep 13 06:17:24 hostname sshd[281443]: Accepted publickey for user from 1.1.1.1 port 22 ssh2: RSA SHA256:HASH"))
    print(ssh("Sep 13 06:17:24 hostname sshd[281443]: pam_unix(sshd:session): session opened for user user(uid=1001) by (uid=0)"))
    print(ssh("Nov 22 11:08:36 hostname sshd[2700138]: error: kex_exchange_identification: banner line contains invalid characters"))
    print(ssh("Nov 25 06:20:08 hostname sshd[2834581]: banner exchange: Connection from 1.1.1.1 port 10301: invalid format"))
