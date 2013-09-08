# -*- coding: utf-8 -*-
import math
import sys

max_count = 25;

class ProgressBar:
    def __init__(self):
        self._value = -1

    def update(self, value, max):
        progress = int(value * 100 / max + 1)
        if self._value == progress:
            return

        self._value = progress
        count = int(max_count * progress  / 100.0 )

        sys.stdout.write('\r[')
        for i in range(count):
            sys.stdout.write('#')

        for i in range(max_count - count):
            sys.stdout.write(' ')

        sys.stdout.write('] {0}%'.format(progress))
        sys.stdout.flush()

    def end(self):
        sys.stdout.write('\r ')
        for i in range(max_count):
            sys.stdout.write(' ')
        sys.stdout.write('       \r')
        sys.stdout.flush()

class Formatter:
    """Утилитарный класс для форматирования значений величин"""
    def time(totalSeconds):
        totalMinutes, seconds = divmod(totalSeconds, 60)
        hours,   minutes      = divmod(totalMinutes, 60)
        formatted             = 'T+ {0:02d}:{1:02d}:{2:02d}'.format(int(hours), int(minutes), int(seconds))
        return formatted

