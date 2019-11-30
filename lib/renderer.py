# -*- coding: utf-8 -*-
import lib.basicTypes as basicTypes
import lib.types as types
import lib.solver as solver
import lib.tools as tools

import matplotlib.pylab as pylab
import math
import numpy
import matplotlib.animation

class RendererOutput:    
    def __init__(self, name):
        self._name = name

    def show(self):
        fig = pylab.gcf()
        fig.canvas.set_window_title(self._name)
        pylab.legend()

class RendererAnimationOutput(RendererOutput):
    def __init__(self, animation):
        super().__init__('Анимация')
        self._animation = animation

    def show(self):
        fig = pylab.gcf()
        fig.canvas.set_window_title(self._name)
        pylab.show()

    def save(path):
        print ('Отрисовка анимации завершена')
        self._animation.save('animation.mp4', fps = 30)
        print ('Запись анимации завершена')

class Renderer:
    """Рендерер графиков"""

    def __init__(self, solver):
        self._objects           = solver.objects
        self._times             = solver.times
        self._animationInterval = 1000
        
    @property
    def animationInterval(self):
        return self._animationInterval
    @animationInterval.setter
    def animationInterval(self, value):
        self._animationInterval = value

    def display(self):
        """Показать окна графиков"""
        pylab.show()

    def renderCharts(self):
        """Отрисовка графиков"""

        print ('Отрисовка графиков')
        
        f, axarr = pylab.subplots(2, 2)
        axarr[0, 0].set_title('F(t)')
        axarr[0, 1].set_title('a(t)')
        axarr[1, 0].set_title('V(t)')
        axarr[1, 1].set_title('Position(t)')
        
        for obj in self._objects:
            if not obj.isStatic:
                obj.forceHistory.plot(axarr[0, 0])
                obj.accelerationHistory.plot(axarr[0, 1])
                obj.velocityHistory.plot(axarr[1, 0])
                obj.positionHistory.plot(axarr[1, 1])
        
        print ('Отрисовка графиков завершена')
        return RendererOutput('Графики')


    def renderTrajectories(self):
        """Отрисовка траекторий"""

        print ('Отрисовка траекторий')

        figure = pylab.figure()
        plot = figure.add_subplot(111, aspect='equal')
        
        for obj in self._objects:
            if not obj.isStatic:
                obj.positionHistory.trajectory(plot)
                obj.positionHistory.quiver(obj.velocityHistory, plot, step = 100)
            else:
                obj.renderStatic(plot)

        print ('Отрисовка траекторий завершена')
        return RendererOutput('Траектории')

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
            if divmod(i, self._animationInterval)[1] == 0:
                frame = []
                for obj in self._objects:
                    part = obj.renderDynamic(plot, i)
                    frame.append(part)

                    part, = obj.positionHistory.trajectory(plot, i)
                    frame.append(part)

                frames.append(frame)

                pylab.draw()
                pylab.savefig("output/anim_{0}.png".format(i))

                bar.update(i, len(self._times))


        bar.end()

        animation = matplotlib.animation.ArtistAnimation(fig, frames, interval=10, blit=False)
        return RendererAnimationOutput(animation)