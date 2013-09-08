# -*- coding: utf-8 -*-
import orbitals
import math

# earth = orbitals.SpaceObject('Earth', mass = 5.97219E24, radius = 6.371E6);
# earth.isStatic = True
earth = orbitals.EntityFactory.earth()

satellite = orbitals.SpaceObject('satellite', mass = 1, radius = 1);
satellite.position = orbitals.Vector(0, earth.radius + 2.5E5)
satellite.velocity = orbitals.Vector(9E3, 0)

#moon = orbitals.SpaceObject('Moon', mass = 5.97219E24, radius = 1.73814E6);
#moon.position = orbitals.Vector(0, 4.05696E8)
#moon.velocity = orbitals.Vector(1.023E3, 0)

moon = orbitals.EntityFactory.moon()

rocket = orbitals.SpaceShip('Rocket', mass = 1, radius = 1)
rocket.position = orbitals.Vector(0, earth.radius + 100)
rocket.velocity = orbitals.Vector(0, 0)

# старт с Земли, 1я ступень
rocket.addEvent(orbitals.ControlEvent.burn(orbitals.Vector.fromPolar(15, 90), [0, 100]))   
# гравитационный маневр, 2я ступень
rocket.addEvent(orbitals.ControlEvent.burn(orbitals.Vector.fromPolar(25, 30), [100, 350]))
# гравитационный маневр-2, 3я ступень
rocket.addEvent(orbitals.ControlEvent.burn(orbitals.Vector.fromPolar(0, -30), [350, 500]))

solver = orbitals.Solver()
solver.addObject(earth)
solver.addObject(rocket)
#solver.addObject(satellite)
#solver.addObject(moon)
solver.timeRange = orbitals.TimeRange(orbitals.Time.minutes(1000)).withIterations(10000)
solver.historyInterval = 1

solver.run()

renderer = orbitals.Renderer(solver)
renderer.renderCharts().show()
renderer.renderTrajectories().show()

renderer.display()

#renderer.renderAnimation().show()