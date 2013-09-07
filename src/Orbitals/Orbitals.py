# -*- coding: utf-8 -*-
import orbitals
import math

earth = orbitals.SpaceObject('Earth', mass = 5.97219E24, radius = 6.371E6);
earth.isStatic = True

satellite = orbitals.SpaceObject('satellite', mass = 1, radius = 1);
satellite.position = orbitals.Vector(0, earth.radius + 2.5E5)
satellite.velocity = orbitals.Vector(9E3, 0)

moon = orbitals.SpaceObject('Moon', mass = 5.97219E24, radius = 1);
moon.position = orbitals.Vector(0, 4.05696E8)
moon.velocity = orbitals.Vector(1.023E3, 0)

solver = orbitals.Solver()
solver.addObject(earth)
solver.addObject(satellite)
solver.addObject(moon)
solver.timeRange = orbitals.TimeRange(orbitals.Time.days(1)).withIterations(10000)

solver.run()

renderer = orbitals.Renderer(solver)
renderer.renderAnimation()
renderer.renderTrajectories()