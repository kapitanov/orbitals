import orbitals.basicTypes as basicTypes
import orbitals.types as types
import orbitals.units as units

from orbitals.basicTypes import Vector
from orbitals.units import factory as unit
from orbitals.types import SpaceObject
from orbitals.types import SpaceShip
from orbitals.types import StaticSpaceObjectController
from orbitals.types import SpaceShipControlEventFactory

controlEvent = SpaceShipControlEventFactory

class EntityFactory:

    def earth():
        """Конструктор Земли (статической)"""
        earth = SpaceObject('Earth', mass = 5.97219E24, radius = unit.dimention.km(6371))
        earth.isStatic = True
        StaticSpaceObjectController().attach(earth)
        return earth

    def moon():
        """Конструктор Луны"""
        moon = SpaceObject('Moon', mass = 5.97219E24, radius = 1.73814E6);
        moon.position = Vector(0, 4.05696E8)
        moon.velocity = Vector(1.023E3, 0)
        return moon

    def falcon9Stage1():
        """Конструктор 1 ступени Falcon9"""
        falcon9st1 = SpaceShip('Falcon9/St.1', mass = 2.585E5, radius = 30)
        falcon9st1.addEvent(controlEvent.burn([0, 180], force = Vector.fromPolar(4086E3, 180), fuel = 2.393E5))
        return falcon9st1

    def protonM():
        """Конструктор Протон-М (который летает)"""
        st1DryMass        = unit.mass.t(30.6)      # Ступень 1 - сухая масса
        st1FueledMass     = unit.mass.t(458.9)     # Ступень 1 - стартовая масса
        st1PropellantMass = st1FueledMass - st1DryMass      # Ступень 1 - масса топлива
        st1Thrust         = unit.force.kN(10020)   # Ступень 1 - тяга
        st1BurnTime       = unit.time.seconds(121) # Ступень 1 - время работы двигателя
        
        st2DryMass        = unit.mass.t(11.0)      # Ступень 2 - сухая масса
        st2FueledMass     = unit.mass.t(168.3)     # Ступень 2 - стартовая масса
        st2PropellantMass = st2FueledMass - st2DryMass      # Ступень 1 - масса топлива
        st2Thrust         = unit.force.kN(2400)    # Ступень 2 - тяга
        st2BurnTime       = unit.time.seconds(215) # Ступень 2 - время работы двигателя

        st3DryMass        = unit.mass.t(3.5)       # Ступень 3 - сухая масса
        st3FueledMass     = unit.mass.t(46.562)    # Ступень 3 - стартовая масса
        st3PropellantMass = st3FueledMass - st3DryMass      # Ступень 1 - масса топлива
        st3Thrust         = unit.force.kN(583)     # Ступень 3 - тяга
        st3BurnTime       = unit.time.seconds(239)  # Ступень 3 - время работы двигателя

        cargoMass         = unit.mass.t(23.0)      # Масса полезной нагрузки (на LEO)

        separationTime    = unit.time.seconds(10)  # Время, необходимое на разделение ступеней
        
        mass = st1FueledMass + st2FueledMass + st3FueledMass + cargoMass
        protonM = SpaceShip('Proton-M', mass = mass, radius = 3000*100)

        # Запуск ступени 1 
        t = 0
        protonM.addEvent(controlEvent.burn([t, t + st1BurnTime], force = Vector.fromPolar(st1Thrust, 90), fuel = st1PropellantMass))
        t = t + st1BurnTime 

        # Отделение ступени 1 
        protonM.addEvent(controlEvent.stageSeparation([t, t + separationTime], name = '1', mass = st1DryMass))
        t = t + separationTime

        # Запуск ступени 2  / до грав. маневра
        protonM.addEvent(controlEvent.burn([t, t + st2BurnTime/2], force = Vector.fromPolar(st2Thrust, 45), fuel = st2PropellantMass))
        t = t + st2BurnTime/2
        # Запуск ступени 2  / грав. маневр
        protonM.addEvent(controlEvent.burn([t, t + st2BurnTime/2], force = Vector.fromPolar(st2Thrust, 0), fuel = st2PropellantMass/2))
        t = t + st2BurnTime/2

        # Отделение ступени 2
        protonM.addEvent(controlEvent.stageSeparation([t, t + separationTime], name = '2', mass = st2DryMass))
        t = t + separationTime

        # Запуск ступени 3
        protonM.addEvent(controlEvent.burn([t, t + st3BurnTime], force = Vector.fromPolar(st3Thrust, -45), fuel = st3PropellantMass))
        t = t + st3BurnTime

        # Отделение ступени 3
        protonM.addEvent(controlEvent.stageSeparation([t, t + separationTime], name = '2', mass = st3DryMass))
        t = t + separationTime
        
        # Свободный полет 
        
        return protonM

    def falcon9():
        """Конструктор Falcon9"""
        st1DryMass        = unit.mass.t(19.24)     # Ступень 1 - сухая масса
        st1PropellantMass = unit.mass.t(239.3)     # Ступень 1 - масса топлива
        st1Thrust         = unit.force.kN(4086)    # Ступень 1 - тяга
        st1BurnTime       = unit.time.seconds(180) # Ступень 1 - время работы двигателя
        
        st2DryMass        = unit.mass.t(3.1)       # Ступень 1 - сухая масса
        st2PropellantMass = unit.mass.t(48.9)      # Ступень 1 - масса топлива
        st2Thrust         = unit.force.kN(513)     # Ступень 1 - тяга
        st2BurnTime       = unit.time.seconds(346) # Ступень 2 - время работы двигателя

        cargoMass         = unit.mass.t(8.5)       # Масса полезной нагрузки (КК Дракон)

        separationTime    = unit.time.seconds(10)  # Время, необходимое на разделение ступеней

        mass = st1DryMass + st1PropellantMass + st2DryMass + st2PropellantMass + cargoMass
        falcon9 = SpaceShip('Falcon9/Dragon', mass = mass, radius = 30)

        # Запуск ступени 1 / до грав. маневра
        t = 0
        falcon9.addEvent(controlEvent.burn([t, t + st1BurnTime / 3], force = Vector.fromPolar(st1Thrust, 0), fuel = st1PropellantMass/3))
        t = t + st1BurnTime / 3

        # Запуск ступени 1 / грав. маневр
        falcon9.addEvent(controlEvent.burn([t, t + st1BurnTime / 3], force = Vector.fromPolar(st1Thrust, -8), fuel =  st1PropellantMass/3))
        t = t + st1BurnTime / 3

        # Запуск ступени 1 / грав. маневр
        falcon9.addEvent(controlEvent.burn([t, t + st1BurnTime / 3], force = Vector.fromPolar(st1Thrust, -8), fuel =  st1PropellantMass/3))
        t = t + st1BurnTime / 3

        # Отделение ступени 1 
        falcon9.addEvent(controlEvent.stageSeparation([t, t + separationTime], name = '1', mass = st1DryMass))
        t = t + separationTime

        # Запуск ступени 2 
        falcon9.addEvent(controlEvent.burn([t, t + st2BurnTime], force = Vector.fromPolar(st2Thrust, 0), fuel = st2PropellantMass))
        t = t + st2BurnTime

        # Отделение ступени 2
        falcon9.addEvent(controlEvent.stageSeparation([t, t + separationTime], name = '2', mass = st2DryMass))
        t = t + separationTime
        
        # Свободный полет 
        
        return falcon9