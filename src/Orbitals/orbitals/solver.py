# -*- coding: utf-8 -*-
import orbitals.basicTypes as basicTypes
import orbitals.types as types
import orbitals.tools as tools
import math

# гравитационная постоянная
G = 6.67384 * math.pow(10, -11) # м^3 кг^-1 с^-2

class Time:
    def __init__(self, seconds):
        self._seconds = seconds
    
    @property
    def seconds(self):
        return self._seconds

    def minutes(x):
        return Time(x*60)
    def hours(x):
        return Time.minutes(x*60)
    def days(x):
        return Time.hours(x*24)

class TimeRange:
    """Диапазон расчета траекторий"""

    def __init__(self, duration):        
        self._from          = 0         # Начальное время
        self._step          = 1         # Шаг времени
        self._iterations    = 1         # Число итераций

        if type(duration) == Time:
            self._to            = duration.seconds  # Конечное время
        else:
            self._to            = duration          # Конечное время

    def withTimeStep(self, step):
        """Задать шаг расчета"""
        self._iterations = (self._to - self._from) / step
        self._step       = step
        return self

    def withIterations(self, iterations):
        """Задать число итераций"""
        self._step       = (self._to - self._from) / iterations
        self._iterations = iterations
        return self

    @property
    def beginTime(self):
        """Начальное время расчета"""
        return self._from

    @property
    def endTime(self):
        """Конечное время расчета"""
        return self._to

    @property
    def timeStep(self):
        """Шаг расчета"""
        return self._step

    @property
    def iterations(self):
        """Число итераций"""
        return self._iterations

class Solver:
    """Вычислитель орбитальных траекторий"""
    def __init__(self):
        self._objects            = []
        self._times              = []
        self._range              = TimeRange(1)
        self._historyInterval    = 1

    @property
    def objects(self):
        """Список небесных тел"""
        return self._objects

    @property
    def times(self):
        """Список точек оси времени"""
        return self._times

    @property
    def historyInterval(self):
        """Интервал записи точек"""
        return self._historyInterval
    @historyInterval.setter
    def historyInterval(self, historyInterval):
        self._historyInterval = historyInterval
    
    def addObject(self, body):
        """Добавить небесное тело к расчету"""
        self._objects.append(body)

    @property
    def timeRange(self):
        """Диапазон расчета траекторий"""
        return self._range
    @timeRange.setter
    def timeRange(self, range):
        self._range = range

    def run(self):
        """Запустить расчет"""
        print ('Расчет траекторий\n')
        bar = tools.ProgressBar()
        bar.update(0, self._range.iterations)

        t = self._range.beginTime
        for i in range(self._range.iterations):
            self._beginStep(t)
            self._runStep(t)
            self._endStep(t, i)

            t = t + self. _range.timeStep
            bar.update(i, self._range.iterations)

        bar.end()
        print ('Расчет траекторий завершен\n')

    def _beginStep(self, t):
        """Начать шаг расчета"""
        for obj in self._objects:
            obj.beginStep(t)

    def _runStep(self, t):
        """Выполнить шаг расчета"""
        for objA in self._objects:
            for objB in self._objects:
                if objA != objB and not objA.isStatic:
                    rVector = objB.position - objA.position
                    distance = rVector.length
                    if distance > 0:
                        g = G * objA.mass * objB.mass
                        h = 1. / distance**3
                        force = rVector * g * h
                        objA.force = objA.force + force
                                
    def _endStep(self, t, i):
        """Завершить шаг расчета"""
        putIntoHistory = divmod(i, self._historyInterval)[1] == 0
        for obj in self._objects:
            if not obj.isStatic:
                obj.acceleration = obj.force * (1. / obj.mass)
                obj.velocity     = obj.velocity + obj.acceleration * self._range.timeStep
                obj.position     = obj.position + obj.velocity * self._range.timeStep
                        
            obj.endStep(t, putIntoHistory)

        if putIntoHistory:
                self._times.append(t)