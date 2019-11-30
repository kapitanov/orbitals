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

    def force(force):
        if force >= 1E6:
            return '{0:0.1f} МН'.format(force / 1E6)        
        if force >= 1E3:
            return '{0:0.1f} кН'.format(force / 1E3)
        if force <= 1E-3:
            return '{0:0.1f} мН'.format(force / 1E-3)

        return '{0:0.1f} Н'.format(force / 1E3)

    def mass(mass):
        if mass >= 1E6:
            return '{0:0.1f} кт'.format(mass / 1E6)        
        if mass >= 1E3:
            return '{0:0.1f} т'.format(mass / 1E3)
        if mass <= 1E-3:
            return '{0:0.1f} г'.format(mass / 1E-3)

        return '{0:0.1f} кг'.format(mass / 1E3)

    def speed(mass):
        if mass >= 1E6:
            return '{0:0.1f} тыс. км/с'.format(mass / 1E6)        
        if mass >= 1E3:
            return '{0:0.1f} км/с'.format(mass / 1E3)

        return '{0:0.1f} м/с'.format(mass / 1E3)


