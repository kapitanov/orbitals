import orbitals.basicTypes as basicTypes
import orbitals.types as types
import orbitals.units as units

controlEvent = types.SpaceShipControlEventFactory

class EntityFactory:

    def earth():
        """Конструктор Земли (статической)"""
        earth = types.SpaceObject('Earth', mass = 5.97219E24, radius = 6.371E6)
        earth.isStatic = True
        types.StaticSpaceObjectController().attach(earth)
        return earth

    def moon():
        """Конструктор Луны"""
        moon = types.SpaceObject('Moon', mass = 5.97219E24, radius = 1.73814E6);
        moon.position = basicTypes.Vector(0, 4.05696E8)
        moon.velocity = basicTypes.Vector(1.023E3, 0)
        return moon

    def falcon9Stage1():
        """Конструктор 1 ступени Falcon9"""
        falcon9st1 = types.SpaceShip('Falcon9/St.1', mass = 2.585E5, radius = 30)
        falcon9st1.addEvent(controlEvent.burn([0, 180], force = basicTypes.Vector.fromPolar(4086E3, 90), fuel = 2.393E5))
        return falcon9st1

    def falcon9():
        """Конструктор Falcon9"""
        st1DryMass        = units.factory.mass.t(19.24)     # Ступень 1 - сухая масса
        st1PropellantMass = units.factory.mass.t(239.3)     # Ступень 1 - масса топлива
        st1Thrust         = units.factory.force.kN(4086)    # Ступень 1 - тяга
        st1BurnTime       = units.factory.time.seconds(180) # Ступень 1 - время работы двигателя
        
        st2DryMass        = units.factory.mass.t(3.1)       # Ступень 1 - сухая масса
        st2PropellantMass = units.factory.mass.t(48.9)      # Ступень 1 - масса топлива
        st2Thrust         = units.factory.force.kN(513)     # Ступень 1 - тяга
        st2BurnTime       = units.factory.time.seconds(346) # Ступень 2 - время работы двигателя

        cargoMass         = units.factory.mass.t(8.5)       # Масса полезной нагрузки (КК Дракон)

        separationTime    = units.factory.time.seconds(10)  # Время, необходимое на разделение ступеней

        mass = st1DryMass + st1PropellantMass + st2DryMass + st2PropellantMass + cargoMass
        falcon9 = types.SpaceShip('Falcon9/Dragon', mass = mass, radius = 30)

        # Запуск ступени 1 / до грав. маневра
        t = 0
        falcon9.addEvent(controlEvent.burn([t, t + st1BurnTime / 2], force = basicTypes.Vector.fromPolar(st1Thrust, 90), fuel = st1PropellantMass/2))
        t = t + st1BurnTime / 2

        # Запуск ступени 1 / грав. маневр
        falcon9.addEvent(controlEvent.burn([t, t + st1BurnTime / 2], force = basicTypes.Vector.fromPolar(st1Thrust, 45), fuel = st1PropellantMass/2))
        t = t + st1BurnTime / 2

        # Отделение ступени 1 
        falcon9.addEvent(controlEvent.stageSeparation([t, t + separationTime], name = '1', mass = st1DryMass))
        t = t + separationTime

        # Запуск ступени 2 
        falcon9.addEvent(controlEvent.burn([t, t + st2BurnTime], force = basicTypes.Vector.fromPolar(st2Thrust, 0), fuel = st2PropellantMass))
        t = t + st2BurnTime

        # Отделение ступени 2
        falcon9.addEvent(controlEvent.stageSeparation([t, t + separationTime], name = '2', mass = st2DryMass))
        t = t + separationTime
        
        # Свободный полет 
        
        return falcon9