import orbitals.basicTypes as basicTypes
import orbitals.types as types

class EntityFactory:

    def earth():
        earth = types.SpaceObject('Earth', mass = 5.97219E24, radius = 6.371E6)
        earth.isStatic = True
        types.StaticSpaceObjectController().attach(earth)
        return earth

    def moon():
        moon = types.SpaceObject('Moon', mass = 5.97219E24, radius = 1.73814E6);
        moon.position = basicTypes.Vector(0, 4.05696E8)
        moon.velocity = basicTypes.Vector(1.023E3, 0)
        return moon
