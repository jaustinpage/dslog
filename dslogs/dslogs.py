#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# builtins
import collections
import itertools
import logging
import re

from pathlib import Path

# not builtins
import arrow
import dslogparser


DS_LOG_DEFAULT = {
        'time': 0,
        'round_trip_time': 0,
        'packet_loss': 0, 
        'voltage': 0,
        'rio_cpu': 0,
        'can_usage': 0,
        'wifi_db': 0, 
        'bandwidth': 0,
        'robot_disabled': False,
        'robot_auto': False,
        'robot_tele': False,
        'ds_disabled': False,
        'ds_auto': False,
        'ds_tele': False,
        'watchdog': False,
        'brownout': False,
        'pdp_id': 0,
        'pdp_currents': [0 for _ in range(16)],
        'pdp_resistance': 0,
        'pdp_voltage': 0,
        'pdp_temp': 0,
        'pdp_total_current': 0,
        }
DSLog = collections.namedtuple('DSLog', DS_LOG_DEFAULT.keys(), defaults=DS_LOG_DEFAULT.values())


class DSlogs():
    def __init__(self, dslog_path, dsevent_path):
        self.logpath = Path(dslog_path)
        self.eventpath = Path(dsevent_path)
    
    @property
    def _log_parser(self):
        return dslogparser.DSLogParser(str(self.logpath))

    @property
    def _event_parser(self):
        return dslogparser.DSEventParser(str(self.eventpath))

    @staticmethod
    def _continuous(gen):
        last_time = None
        for item in gen:
            last_time = item['time']
            yield item
        while True:
            log = BLANK_LOG
            last_time = 
            yield BLANK_LOG

    @staticmethod
    def _fix_time(gen):
        for item in gen:
            item['time'] = arrow.get(item['time'])
            yield item

    def _slice(self, gen, start=None, end=None):
        if not start:
            start = arrow.get(0)
        if not end:
            end = arrow.get()
        for item in gen:
            if item['time'].is_between(start, end, '[]'):
                yield item

    def _window(self, gen, start, end, items_per_window):
        if not start:
            start = arrow.get(0)
        if not end:
            end = arrow.get()
        if not items_per_window:
            raise ValueError('Must provide a window size')
        window = collections.deque(maxlen=items_per_window)
        middle_index = items_per_window//2 # left of center if even, else absolute center
        for item in gen:
            window.append(item)
            if (len(window) < items_per_window):
                continue
            if not window[middle_index]['time'].is_between(start, end, '[]'):
                continue
            yield window

    def _items(self, gen, start=None, end=None, window=None):
        gen = self._fix_time(gen)
        if window:
            gen = self._window(gen, start=start, end=end, items_per_window=window)
            for item in gen:
                yield item

        elif (not start) and (not end):
            for item in gen:
                yield item
        else:
            gen = self._slice(gen, start, end)
            for item in gen:
                yield item

    def logs(self, start=None, end=None, window=None):
        return self._items(self._log_parser.read_records(), start, end, window)

    def events(self, start=None, end=None, window=None):
        return self._items(self._event_parser.read_records(), start, end, window)

    def match_info(self):
        field_time, match = self._event_parser.match_info
        if field_time:
            field_time = arrow.get(field_time)
        return field_time, match
