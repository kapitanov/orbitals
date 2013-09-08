# -*- coding: utf-8 -*-
import orbitals.basicTypes as basicTypes
import numpy
import math

def renderCircle(plot, position, radius, name, fill = False, color = None):
    ts = [math.radians(x) for x in numpy.arange(0, 360, 1)]
    xs = [position.x + radius * math.cos(x) for x in ts]
    ys = [position.y + radius * math.sin(x) for x in ts]

    if color != None:
        p,  = plot.plot(xs, ys, label = name, color = color)
    else:
        p,  = plot.plot(xs, ys, label = name)

    if fill:
        plot.fill_between(xs, ys)
    return p

class SpaceObjectController:
    """Контроллер космического объекта - базовый класс"""
    def __init__(self):
        self._object     = None
        self._dependents = []
        self._isUpToDate = True
        self._lastTime   = True
        self._lastDelta  = True

    @property
    def isAffectedByForces(self):
        """Является ли данный объект участником динамического расчета"""
        return True

    def attach(self, object):
        """Привязать контроллер к космическому объекту"""
        self._object      = object
        object.controller = self

    def beginStep(self, t, dt):
        """Обновление шага расчета"""
        self._object.acceleration = basicTypes.Vector.zero()
        self._object.force = basicTypes.Vector.zero()
        self._clearDependents()
        self._beginStepCore(self._object, t, dt)

    def endStep(self, t, dt, isDependencyCall = False):
        """Завершение шага расчета"""
        self._object.acceleration = self._object.force * (1. / self._object.mass)
        self._object.velocity     = self._object.velocity + self._object.acceleration * dt
        self._object.position     = self._object.position + self._object.velocity * dt
        self._invokeDependents(t, dt)

    def _beginStepCore(self, object, t, dt):
        """Обновление шага расчета"""
        raise Exception('SpaceObjectController._beginStepCore() is not implemented')

    def putDependent(self, dependent):
        """Добавить зависимый контролллер.
           Контроллер dependent будет вызван после завершения расчета данного контроллера
        """
        if self._isUpToDate:
            dependent.endStep(self._lastTime, self._lastDelta, isDependencyCall = True)
        else:
            self._dependents.append(dependent)

    def _clearDependents(self):
        """Очистить список зависимых контроллеров"""
        self._dependents.clear()
        self._isUpToDate = False

    def _invokeDependents(self, t, dt):
        """Вызвать зависимые контроллеры"""
        self._isUpToDate = True
        self._lastTime   = t
        self._lastDelta  = dt
        for dependent in self._dependents:
            dependent.endStep(t, dt, isDependencyCall = True)

class ChainedSpaceObjectController(SpaceObjectController):
    """Контроллер космического объекта с поддержкой цепочки контроллеров - базовый класс"""
    def __init__(self):
        super().__init__()
        self._nextController = None

    def attach(self, object):
        """Привязать контроллер к космическому объекту"""
        if object.controller != None:
            self._nextController = object.controller
        super().attach(object)

    def beginStep(self, t, dt):
        """Обновление шага расчета"""
        self._object.acceleration = basicTypes.Vector.zero()
        self._object.force = basicTypes.Vector.zero()
        self._clearDependents()

        # Вызываем предыдущий контроллер
        if self._nextController != None:
            self._nextController._beginStepCore(self._object, t, dt)
        self._beginStepCore(self._object, t, dt)
        
class GravitySpaceObjectController(ChainedSpaceObjectController):
    """Гравитационный контроллер"""
    def _beginStepCore(self, object, t, dt):
        """Обновление шага расчета"""
        # Никаких действий не требуется
        return

class DynamicSpaceObjectController(ChainedSpaceObjectController):
    """Динамический контроллер"""
    def __init__(self):
        super().__init__()
                
    def _beginStepCore(self, object, t, dt):
        """Обновление шага расчета"""
        for event in object.events:
            event.apply(object, t, dt)

class StaticSpaceObjectController(SpaceObjectController):
    """Контроллер для статического объекта"""
    def __init__(self):
        super().__init__()

    @property
    def isAffectedByForces(self):
        """Является ли данный объект участником динамического расчета"""
        return False
        
    def beginStep(self, t, dt):
        """Обновление шага расчета"""
        self._object.acceleration = basicTypes.Vector.zero()
        self._object.force = basicTypes.Vector.zero()
        self._clearDependents()
    
    def endStep(self, t, dt, isDependencyCall = False):
        """Завершение шага расчета"""
        self._invokeDependents(t, dt)

class CollidedSpaceObjectController(SpaceObjectController):
    """Контроллер для объекта, столкнувшегося с другим"""
    def __init__(self, collider, relativePosition):
        super().__init__()
        self._collider         = collider
        self._relativePosition = relativePosition

    @property
    def isAffectedByForces(self):
        """Является ли данный объект участником динамического расчета"""
        return False
        
    def _beginStepCore(self, object, t, dt):
        """Обновление шага расчета"""
        self._object.acceleration = basicTypes.Vector.zero()
        self._object.force = basicTypes.Vector.zero()
        self._clearDependents()
    
    def endStep(self, t, dt, isDependencyCall = False):
        """Завершение шага расчета"""
        if isDependencyCall:
            self._object.position = self._collider.position + self._relativePosition
            self._invokeDependents(t, dt)
        else:
            self._collider.controller.putDependent(self)

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
        self._controller   = None

        # Привязываем гравитационный контроллер
        GravitySpaceObjectController().attach(self)

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

    @property
    def controller(self):
        """Контроллер объекта"""
        return self._controller
    @controller.setter
    def controller(self, controller):
        self._controller = controller

    def beginStep(self, t, dt):
        """Инициализация шага расчета"""
        self._controller.beginStep(t, dt)

    def endStep(self, t, dt, putIntoHistory = True):
        """Завершение шага расчета"""
        self._controller.endStep(t, dt)
        if putIntoHistory:
            self._position.put(t)
            self._velocity.put(t)
            self._acceleration.put(t)
            self._force.put(t)

    def renderStatic(self, plot):
        """Отрисовка объекта как статического тела"""
        return renderCircle(plot, self.position, self.radius, name = self.name, fill = True)

    def renderDynamic(self, plot, index):
        """Отрисовка объекта как динамического тела в момент времени t[index]"""
        position = basicTypes.Vector(self._position.history._xs[index], self._position.history._ys[index])
        return renderCircle(plot, position, self.radius, name = self.name, color = 'b')

class SpaceShipControlEvent:
    def __init__(self, start, end):
        self._start = start
        self._end   = end

    def apply(self, object, t, dt):
        if self._start <= t and self._end > t:
            self._applyCore(object, t, dt)

    def _applyCore(self, object, t, dt):
        raise Exception('SpaceShipControlEvent._applyCore() not implemented')

class BurnControlEvent(SpaceShipControlEvent):
    def __init__(self, force, start, end):
        super().__init__(start, end)
        self._force = force
    def _applyCore(self, object, t, dt):
        object.force = object.force + self._force

class SpaceShipControlEventFactory:
    def burn(force, range):
        return BurnControlEvent(force, range[0], range[1])
    
class SpaceShip(SpaceObject):
    """Космический корабль"""

    def __init__(self, name, mass, radius):
        super().__init__(name, mass, radius)
        self._events     = []

        # меняем контроллер на динамический
        DynamicSpaceObjectController().attach(self)

    @property
    def events(self):
        return self._events

    def addEvent(self, event):
        self._events.append(event)