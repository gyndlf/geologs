# -*- coding: utf-8 -*-
"""
Created on Sun Sep 08 10:00 2024

Run the bot

@author: james
"""

import os

try:
    from rocky import rocky
except ImportError:
    from ..rocky import rocky

rocky.main("config.toml")

