#!/usr/bin/env python3

import json
import sys
import openpyxl
from openpyxl.styles import PatternFill, Color
from openpyxl.comments import Comment
import re
from calendar import Calendar
from datetime import time, timedelta
from math import ceil
from os.path import dirname, join
from copy import copy˝

def index_by(key_prop, array_of_dicts):
    indexed = {}
    for item in array_of_dicts:
        key = item[key_prop]
        if key in indexed:
            indexed[key].append(item)
        else:
            indexed[key] = [item]
    return indexed

def delta_from_time(t: time) -> timedelta:
    return timedelta(days=0,
        hours=t.hour, minutes=t.minute, seconds=t.second
    )

def delta_between_times(start: time, end: time) -> timedelta:
    return delta_from_time(end) - delta_from_time(start)