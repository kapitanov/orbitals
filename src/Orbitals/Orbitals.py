# -*- coding: utf-8 -*-
import orbitals
import math

earth = orbitals.EntityFactory.earth()
moon = orbitals.EntityFactory.moon()

falcon9 = orbitals.EntityFactory.falcon9()
falcon9.position = orbitals.Vector(0, earth.radius + orbitals.Units.dimension.m(100))

solver = orbitals.Solver()
solver.addObject(earth)
solver.addObject(falcon9)
solver.timeRange       = orbitals.TimeRange(orbitals.Units.time.seconds(10000)).withIterations(100000)
solver.enableTrace     = False
solver.historyInterval = 50

solver.run()

renderer = orbitals.Renderer(solver)
renderer.renderCharts().show()
renderer.renderTrajectories().show()

renderer.display()
#renderer.renderAnimation().show()