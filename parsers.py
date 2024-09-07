# -*- coding: utf-8 -*-
"""
Created on Sat Sep 07 20:14 2024

Simple parsers to make the log files look pretty.

@author: james
"""


def basic(message: str):
    """Do nothing"""
    return message


PARSERS = {
    "basic": basic,
}