# -*- coding: utf-8 -*-
"""
Created on Sun Sep 08 10:00 2024

Run the bot

@author: james
"""

import sys


try:
    from . import geologs
except ImportError:
    from geologs import geologs


def main():
    config_file = "config.toml"
    for arg in sys.argv[1:]:
        if arg.startswith("--conf="):
            config_file = arg[len("--conf="):]
    geologs.main(config_file)


if __name__ == "__main__":
    main()

