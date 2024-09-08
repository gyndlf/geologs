# -*- coding: utf-8 -*-
"""
Created on Sun Sep 08 10:00 2024

Run the bot

@author: james
"""

import os


try:
    from . import geologs
except ImportError:
    from geologs import geologs


def main():
    geologs.main("config.toml")


if __name__ == "__main__":
    main()

