# -*- coding: utf-8 -*-
import orbitals.basicTypes as basicTypes
import orbitals.tools as tools
import numpy
import math

def renderCircle(plot, position, radius, name = None, fill = False, color = None):
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

    @property
    def isAffectedByForces(self):
        """Является ли данный объект участником динамического расчета"""
        return True

    def attach(self, object):
        """Привязать контроллер к космическому объекту"""
        self._object      = object
        object.controller = self

    def beginStep(self, ctx):
        """Обновление шага расчета"""
        self._object.acceleration = basicTypes.Vector.zero()
        self._object.force        = basicTypes.Vector.zero()
        self._clearDependents()
        self._beginStepCore(self._object, ctx)

    def endStep(self, ctx, isDependencyCall = False):
        """Завершение шага расчета"""
        self._object.acceleration = self._object.force * (1. / self._object.mass)
        self._object.velocity     = self._object.velocity + self._object.acceleration * ctx.dt
        self._object.position     = self._object.position + self._object.velocity * ctx.dt
        self._invokeDependents(ctx)

    def _beginStepCore(self, object, ctx):
        """Обновление шага расчета"""
        raise Exception('SpaceObjectController._beginStepCore() is not implemented')

    def putDependent(self, ctx, dependent):
        """Добавить зависимый контролллер.
           Контроллер dependent будет вызван после завершения расчета данного контроллера
        """
        if self._isUpToDate:
            dependent.endStep(ctx, isDependencyCall = True)
        else:
            self._dependents.append(dependent)

    def _clearDependents(self):
        """Очистить список зависимых контроллеров"""
        self._dependents.clear()
        self._isUpToDate = False

    def _invokeDependents(self, ctx):
        """Вызвать зависимые контроллеры"""
        self._isUpToDate = True
        for dependent in self._dependents:
            dependent.endStep(ctx, isDependencyCall = True)

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

    def beginStep(self, ctx):
        """Обновление шага расчета"""
        self._object.acceleration = basicTypes.Vector.zero()
        self._object.force = basicTypes.Vector.zero()
        self._clearDependents()

        # Вызываем предыдущий контроллер
        if self._nextController != None:
            self._nextController._beginStepCore(self._object, ctx)
        self._beginStepCore(self._object, ctx)
        
class GravitySpaceObjectController(ChainedSpaceObjectController):
    """Гравитационный контроллер"""
    def _beginStepCore(self, object, ctx):
        """Обновление шага расчета"""
        # Никаких действий не требуется
        return

class DynamicSpaceObjectController(ChainedSpaceObjectController):
    """Динамический контроллер"""
    def __init__(self):
        super().__init__()
                
    def _beginStepCore(self, object, ctx):
        """Обновление шага расчета"""
        for event in object.events:
            event.apply(object, ctx)

class StaticSpaceObjectController(SpaceObjectController):
    """Контроллер для статического объекта"""
    def __init__(self):
        super().__init__()

    @property
    def isAffectedByForces(self):
        """Является ли данный объект участником динамического расчета"""
        return False
        
    def beginStep(self, ctx):
        """Обновление шага расчета"""
        self._object.acceleration = basicTypes.Vector.zero()
        self._object.force = basicTypes.Vector.zero()
        self._clearDependents()
    
    def endStep(self, ctx, isDependencyCall = False):
        """Завершение шага расчета"""
        self._invokeDependents(ctx)

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
        
    def _beginStepCore(self, object, ctx):
        """Обновление шага расчета"""
        self._object.acceleration = basicTypes.Vector.zero()
        self._object.force = basicTypes.Vector.zero()
        self._clearDependents()
    
    def endStep(self, ctx, isDependencyCall = False):
        """Завершение шага расчета"""
        if isDependencyCall:
            self._object.position = self._collider.position + self._relativePosition
            self._invokeDependents(ctx)
        else:
            self._collider.controller.putDependent(ctx, self)

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

    def beginStep(self, ctx):
        """Инициализация шага расчета"""
        self._controller.beginStep(ctx)

    def endStep(self, ctx):
        """Завершение шага расчета"""
        self._controller.endStep(ctx)
        if ctx.putIntoHistory:
            self._position.put(ctx.t)
            self._velocity.put(ctx.t)
            self._acceleration.put(ctx.t)
            self._force.put(ctx.t)

    def renderStatic(self, plot):
        """Отрисовка объекта как статического тела"""
        return renderCircle(plot, self.position, self.radius, fill = True)

    def renderDynamic(self, plot, index):
        """Отрисовка объекта как динамического тела в момент времени t[index]"""
        position = basicTypes.Vector(self._position.history._xs[index], self._position.history._ys[index])
        return renderCircle(plot, position, self.radius, name = self.name, color = 'b')

class SpaceShipControlEvent:
    def __init__(self, start, end):
        self._start    = start
        self._end      = end
        self._isActive = False

    def apply(self, object, ctx):
        if self._start <= ctx.t and self._end > ctx.t:
            if not self._isActive:
                self._isActive = True
                self._onStart(object, ctx)
            self._applyCore(object, ctx)
        else:
            if self._isActive:
                self._isActive = False
                self._onEnd(object, ctx)

    def _applyCore(self, object, ctx):
        raise Exception('SpaceShipControlEvent._applyCore() not implemented')

    def _onStart(self, object, ctx):
        return

    def _onEnd(self, object, ctx):
        return

class BurnControlEvent(SpaceShipControlEvent):
    def __init__(self, force, fuelMass, start, end):
        super().__init__(start, end)
        self._force    = force
        self._fuelMass = fuelMass
        self._duration = end - start

    def _applyCore(self, object, ctx):
        # Сжигаем часть топлива
        burnedFuel = self._fuelMass * ctx.dt / self._duration
        object.mass = object.mass - burnedFuel

        # Добавляем импульс двигателя
        object.force = object.force + self._force
        
    def _onStart(self, object, ctx):
        ctx.log.info('Объект {0} - двигатель включен, тяга {1}'.format(object.name, tools.Formatter.force(self._force.length)))
        return

    def _onEnd(self, object, ctx):
        ctx.log.info('Объект {0} - двигатель выключен'.format(object.name))
        return

class StageSeparationControlEvent(SpaceShipControlEvent):
    def __init__(self, name, separatedMass, start, end):
        super().__init__(start, end)
        self._name      = name
        self._mass      = separatedMass
        self._separated = False

    def _applyCore(self, object, ctx):
        # Отделяем часть массы КА
        if not self._separated:
            ctx.log.info('Объект {0} - отделение ступени {1} массой {2}'.format(object.name, self._name,  tools.Formatter.mass(self._mass)))
            self._separated = True
            object.mass = object.mass - self._mass

class SpaceShipControlEventFactory:
    def burn(range, force, fuel = 0):
        return BurnControlEvent(force, fuel, range[0], range[1])
    def stageSeparation(range, name = '?', mass = 0):
        return StageSeparationControlEvent(name, mass, range[0], range[1])
    
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