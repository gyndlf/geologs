# -*- coding: utf-8 -*-
"""
Created on Sat Sep 07 21:15 2024

Some basic commands to run on the server.

@author: james
"""

import asyncio


async def _run_cmd(*args, stdin='', code_block=False):
    """Helper function to run the command and get the result."""
    proc = await asyncio.create_subprocess_exec(
        *args,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        stdin=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate(input=stdin.encode())
    if stderr != b'':
        raise RuntimeError(stderr.decode('utf-8'))
    if code_block:
        return "```\n" + stdout.decode('utf-8') + "```"
    return stdout.decode('utf-8')


async def uptime(*args) -> str:
    """Get server uptime"""
    return await _run_cmd('uptime')


async def disk(*args) -> str:
    """Return information about disk usage"""
    return await _run_cmd('df', '-h', '/', code_block=True)


async def proc(*args) -> str:
    """Return the top 5 processes by CPU utilisation"""
    return await _run_cmd('ps', 'aux', '--sort=-pcpu', '|', 'head', '-n 6')


async def ping(*args) -> str:
    """Do a few pings to determine network speed"""
    ip = args[0] if len(args) > 0 else "1.1.1.1"
    return await _run_cmd('ping', '-c 4', ip, code_block=True)


async def logins(*args) -> str:
    """List the last 10 logins (or terminal sessions)"""
    return await _run_cmd('head', stdin=await _run_cmd('last'), code_block=True)


async def ip(*args) -> str:
    """Get the host external ip"""
    return await _run_cmd('curl', '-4sS', 'http://checkip.amazonaws.com')


async def throws(*args) -> str:
    """Always throws an error"""
    return await _run_cmd('nonexistent')


SYSTEM_COMMANDS = {
    "uptime": uptime,
    "disk": disk,
    "proc": proc,
    "ping": ping,
    "logins": logins,
    "ip": ip,
    "throws": throws,
}

if __name__ == "__main__":
    async def main():
        print(await uptime())
        print(await ip())
        #print(await ping("8.8.8.8"))
    asyncio.run(main())
