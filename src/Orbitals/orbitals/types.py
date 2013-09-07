# -*- coding: utf-8 -*-
import orbitals.basicTypes as basicTypes
import numpy
import math

def renderCircle(plot, position, radius, name, fill = False, color = None):
    ts = [math.radians(x) for x in numpy.arange(0, 360, 1)]
    xs = [position.x + radius * math.cos(x) for x in ts]
    ys = [position.y + radius * math.sin(x) for x in ts]
    p,  = plot.plot(xs, ys, label = name, color = color)

    if fill:
        plot.fill_between(xs, ys, color = color)
    return p
        
class SpaceObject:
    """Базовый класс космического объекта"""

    def __init__(self, name, mass, radius):
        self._name         = name
        self._mass         = mass
        self._radius       = radius
        self._position     = basicTypes.VectorWithHistory(name, "Position")
        self._velocity     = basicTypes.VectorWithHistory(name, "V")
        self._force        = basicTypes.VectorWithHistory(name, "F")
        self._acceleration = basicTypes.VectorWithHistory(name, "a")
        self._isStatic     = False

    @property
    def name(self):
        """Название объекта"""
        return self._name

    @property
    def mass(self):
        """Масса объекта"""
        return self._mass
    @mass.setter
    def mass(self, mass):
        self._mass = mass

    @property
    def radius(self):
        """Радиус объекта"""
        return self._radius

    @property
    def position(self):
        """Координаты объекта"""
        return self._position.value
    @position.setter
    def position(self, position):
        self._position.value = position

    @property
    def positionHistory(self):
        """История изменений координат"""
        return self._position.history

    @property
    def velocity(self):
        """Скорость"""
        return self._velocity.value
    @velocity.setter
    def velocity(self, velocity):
        self._velocity.value = velocity

    @property
    def velocityHistory(self):
        """История изменений скорости"""
        return self._velocity.history

    @property
    def acceleration(self):
        """Ускорение"""
        return self._acceleration.value
    @acceleration.setter
    def acceleration(self, acceleration):
        self._acceleration.value = acceleration

    @property
    def accelerationHistory(self):
        """История изменений ускорения"""
        return self._acceleration.history

    @property
    def force(self):
        """Суммарная сила"""
        return self._force.value
    @force.setter
    def force(self, force):
        self._force.value = force

    @property
    def forceHistory(self):
        """История изменений суммарной силы"""
        return self._force.history

    @property
    def isStatic(self):
        """Является ли объект статическим"""
        return self._isStatic
    @isStatic.setter
    def isStatic(self, isStatic):
        self._isStatic = isStatic

    def beginStep(self, t):
        """Инициализация шага расчета"""
        self.acceleration = basicTypes.Vector.zero()
        self.force = basicTypes.Vector.zero()

    def endStep(self, t, putIntoHistory = True):
        """Завершение шага расчета"""
        if putIntoHistory:
            self._position.put(t)
            self._velocity.put(t)
            self._force.put(t)

    def renderStatic(self, plot):
        """Отрисовка объекта как статического тела"""
        return renderCircle(plot, self.position, self.radius, name = self.name, fill = True)

    def renderDynamic(self, plot, index):
        """Отрисовка объекта как динамического тела в момент времени t[index]"""
        position = basicTypes.Vector(self._position.history._xs[index], self._position.history._ys[index])
        return renderCircle(plot, position, self.radius, name = self.name, color = 'b')