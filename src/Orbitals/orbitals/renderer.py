# -*- coding: utf-8 -*-
import orbitals.basicTypes as basicTypes
import orbitals.types as types
import orbitals.solver as solver
import orbitals.tools as tools

import pylab
import math
import numpy
import matplotlib.animation

class Renderer:
    """Рендерер графиков"""

    def __init__(self, solver):
        self._objects = solver.objects
        self._times = solver.times

    def renderTrajectories(self):
        """Отрисовка траекторий"""

        print ('Отрисовка траекторий')

        figure = pylab.figure()
        plot = figure.add_subplot(111, aspect='equal')
        
        for obj in self._objects:
            if not obj.isStatic:
                obj.positionHistory.trajectory(plot)
            else:
                obj.renderStatic(plot)

        fig = pylab.gcf()
        fig.canvas.set_window_title('Траектории')
        plot.legend()
        print ('Отрисовка траекторий завершена')
        pylab.show()

    def renderAnimation(self):  
        """Отрисовка анимации"""

        print ('Отрисовка анимации')

        fig = pylab.figure(figsize=(16,9),dpi=80)
        plot = fig.add_subplot(111, aspect='equal')
        frames = []

        bar = tools.ProgressBar()
        bar.update(0, len(self._times))

        pylab.ion()

        for i in range(len(self._times)):
            frame = []
            for obj in self._objects:
                part = obj.renderDynamic(plot, i)
                frame.append(part)
            frames.append(frame)

            pylab.draw()
            pylab.savefig("output/anim_{0}.png".format(i))

            bar.update(i, len(self._times))


        bar.end()

        animation = matplotlib.animation.ArtistAnimation(fig, frames, interval=1,blit=False)
        fig = pylab.gcf()
        fig.canvas.set_window_title('Анимация')
        print ('Отрисовка анимации завершена')
        #animation.save('animation.mp4', fps=30)
        #print ('Запись анимации завершена')