#!/usr/bin/env python3

import json
import sys
import openpyxl
from openpyxl.styles import PatternFill, Color
from openpyxl.comments import Comment
import re
from calendar import Calendar
from datetime import time, timedelta, datetime
from math import ceil
from os.path import dirname, join
from copy import copy

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

def getDate(year, month, day):
    if day < 21:
        return datetime(year, month, day)
    
    lastMonth = month - 1 if month > 1 else 12
    lastYear = year if month > 1 else year - 1
    return datetime(lastYear, lastMonth, day)

def isWeekend(date):
        return date.weekday() > 4