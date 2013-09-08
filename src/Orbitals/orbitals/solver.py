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
    
class SolverLogEntry:
    """Запись в логе вычислителя"""
    def __init__(self, time, message):
        self._time    = time
        self._message = message

    def print(self):
        """Вывод записи в консоль"""
        print ('{0}:   {1}'.format(tools.Formatter.time(self._time), self._message))

class SolverLog:
    """Лог вычислителя"""


    def __init__(self):
        self._events = []

    def write(self, time, message):
        """Добавить запись в лог"""
        self._events.append(SolverLogEntry(time, message))

    def print(self):
        """Вывод лога в консоль"""
        for event in self._events:
            event.print()

class Solver:
    """Вычислитель орбитальных траекторий"""
    def __init__(self):
        self._objects            = []
        self._times              = []
        self._range              = TimeRange(1)
        self._historyInterval    = 1
        self._log                = SolverLog()

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
        self._log.write(t, 'Запуск симуляции');
        for i in range(self._range.iterations):
            self._beginStep(t)
            self._runStep(t)
            self._endStep(t, i)

            t = t + self._range.timeStep
            bar.update(i, self._range.iterations)

        bar.end()
        self._log.write(t, 'Симуляция завершена');
        print ('Расчет траекторий завершен\n')
        self._log.print()

    def _beginStep(self, t):
        """Начать шаг расчета"""
        for obj in self._objects:
            obj.beginStep(t, self._range.timeStep)

    def _runStep(self, t):
        """Выполнить шаг расчета"""
        for objA in self._objects:
            for objB in self._objects:
                # 1. Объект не влияет сам на себя
                # 2. Объект должен быть подвержен действию сил (втч сил гравитации)
                #    Напр. объект, столкнувшийся с другим, более не подвержен действию внешних сил
                if objA != objB and objA.controller.isAffectedByForces:
                    rVector = objB.position - objA.position
                    distance = rVector.length

                    # расчет коллизий - меньший по массе объект может столкнуться с большим по массе
                    if objA.mass < objB.mass and distance <= objA.radius + objB.radius:
                       # Объект A столкнулся с объектом B
                       types.CollidedSpaceObjectController(objB, -rVector).attach(objA)
                       objA.beginStep(t, self._range.timeStep)
                       self._log.write(t, 'Объект {0} столкнулся с объектом {1}'.format(objA.name, objB.name))
                       continue

                    # расчет гравитации
                    if distance > 0:
                        g = G * objA.mass * objB.mass
                        h = 1. / distance**3
                        force = rVector * g * h
                        objA.force = objA.force + force
                                
    def _endStep(self, t, i):
        """Завершить шаг расчета"""
        putIntoHistory = divmod(i, self._historyInterval)[1] == 0
        for obj in self._objects:
            obj.endStep(t, self._range.timeStep, putIntoHistory)

        if putIntoHistory:
                self._times.append(t)