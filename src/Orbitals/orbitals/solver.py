# -*- coding: utf-8 -*-
import orbitals.basicTypes as basicTypes
import orbitals.types as types
import orbitals.tools as tools
import math
from colorconsole import terminal

# гравитационная постоянная
G = 6.67384 * math.pow(10, -11) # м^3 кг^-1 с^-2

class TimeRange:
    """Диапазон расчета траекторий"""

    def __init__(self, duration):        
        self._from          = 0         # Начальное время
        self._step          = 1         # Шаг времени
        self._iterations    = 1         # Число итераций
        self._to            = duration  # Конечное время

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
    
class SolverLogLevel:
    info  = 1
    err   = 2
    trace = 3
    
class SolverLogEntry:
    """Запись в логе вычислителя"""
    def __init__(self, time, level, message):
        self._time    = time
        self._level   = level
        self._message = message

    def print(self, screen):
        """Вывод записи в консоль"""
        color = 'WHITE';
        if self._level == SolverLogLevel.err:
            color = 'LRED'
        else: 
            if self._level == SolverLogLevel.trace:
                color = 'DGRAY'
        screen.set_color(fg = terminal.colors[color])
        print ('{0}:   {1}'.format(tools.Formatter.time(self._time), self._message))

class SolverLog:
    """Лог вычислителя"""
    def __init__(self):
        self._events      = []
        self._enableTrace = True

    @property
    def enableTrace(self):
        return self._enableTrace
    @enableTrace.setter
    def enableTrace(self, enable):
        self._enableTrace = enable

    def info(self, time, message):
        """Добавить инф. запись в лог"""
        self._write(time, SolverLogLevel.info, message)

    def err(self, time, message):
        """Добавить запись об ошибке в лог"""
        self._write(time, SolverLogLevel.err, message)

    def trace(self, time, message):
        """Добавить отладочную запись в лог"""
        if self._enableTrace:
            self._write(time, SolverLogLevel.trace, message)

    def _write(self, time, level, message):
        """Добавить запись в лог"""
        self._events.append(SolverLogEntry(time, level, message))

    def print(self):
        """Вывод лога в консоль"""
        screen = terminal.get_terminal()
        for event in self._events:
            event.print(screen)
        screen.reset()

class SolverLogFacade:
    """Фасад лога вычислителя"""
    def __init__(self, ctx, log):
        self._ctx = ctx
        self._log = log

    def info(self, message):
        """Добавить инф. запись в лог"""
        self._log.info(self._ctx.t, message)

    def err(self, time, message):
        """Добавить запись об ошибке в лог"""
        self._log.err(self._ctx.t, message)

    def trace(self, time, message):
        """Добавить отладочную запись в лог"""
        self._log.trace(self._ctx.t, message)
        
class SolverCtx:
    """Контекст вычислителя"""
    def __init__(self, solver):
        self._solver         = solver
        self._t              = 0.
        self._putIntoHistory = False
        self._iteration      = 0     
        self._logFacade      = SolverLogFacade(self, solver._log)            

    def begin(self):
        """Инициализация расчета"""
        self._t              = self._solver._range.beginTime
        self._iteration      = 0
        self._putIntoHistory = divmod(self._iteration, self._solver._historyInterval)[1] == 0

    def next(self):
        """Переход к следующему шагу расчета"""
        self._t              = self._t + self.dt
        self._iteration      = self._iteration + 1
        self._putIntoHistory = divmod(self._iteration, self._solver._historyInterval)[1] == 0

    @property
    def t(self):
        """Текущее время"""
        return self._t

    @property
    def dt(self):
        """Шаг расчета"""
        return self._solver._range.timeStep

    @property
    def putIntoHistory(self):
        """Шаг расчета"""
        return self._putIntoHistory

    @property
    def log(self):
        """Лог вычислителя"""
        return self._logFacade
            
class Solver:
    """Вычислитель орбитальных траекторий"""
    def __init__(self):
        self._objects            = []
        self._times              = []
        self._range              = TimeRange(1)
        self._historyInterval    = 1
        self._log                = SolverLog()
        self._ctx                = SolverCtx(self)

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

    @property
    def enableTrace(self):
        return self._log._enableTrace
    @enableTrace.setter
    def enableTrace(self, enable):
        self._log._enableTrace = enable
    
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
        print ('Расчет траекторий')
        bar = tools.ProgressBar()
        bar.update(0, self._range.iterations)

        self._ctx.begin()
        self._log.info(self._ctx.t, 'Запуск симуляции');
        for i in range(self._range.iterations):
            self._beginStep()
            self._runStep()
            self._endStep()

            self._ctx.next()
            bar.update(i, self._range.iterations)

        bar.end()
        self._log.info(self._ctx.t, 'Симуляция завершена');
        print ('Расчет траекторий завершен')
        self._log.print()

    def _beginStep(self):
        """Начать шаг расчета"""
        for obj in self._objects:
            obj.beginStep(self._ctx)

    def _runStep(self):
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
                       objA.beginStep(self._ctx)
                       relativeVelocity = (objA.velocity - objB.velocity).length
                       self._log.err(self._ctx.t, 'Объект {0} столкнулся с объектом {1}, скорость столкновения {2}'.format(objA.name, objB.name, tools.Formatter.speed(relativeVelocity)))
                       continue

                    # расчет гравитации
                    if distance > 0:
                        g = G * objA.mass * objB.mass
                        h = 1. / distance**3
                        force = rVector * g * h
                        self._log.trace(self._ctx.t, 'Грав. сила для объекта {0} = {1} | {2}'.format(objA.name, force, force * (1. / objA.mass)))
                        self._log.trace(self._ctx.t, 'Сила тяги для объекта  {0} = {1} | {2}'.format(objA.name, objA.force, objA.force * (1. / objA.mass)))
                        objA.force = objA.force + force
                                
    def _endStep(self):
        """Завершить шаг расчета"""
        for obj in self._objects:
            obj.endStep(self._ctx)

        if self._ctx.putIntoHistory:
            self._times.append(self._ctx.t)