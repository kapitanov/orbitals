# -*- coding: utf-8 -*-
import math

class Vector:
    """2D вектор"""
    def __init__(self, x, y):
        self._x = x
        self._y = y
    
    @property
    def x(self):
        """Координата X"""
        return self._x
    @x.setter
    def x(self, x):
        self._x = x

    @property
    def y(self):
        """Координата Y"""
        return self._y
    @y.setter
    def y(self, y):
        self._y = y

    @property
    def length(self):
        """Длина вектора"""
        return math.sqrt(self._x*self._x + self._y*self._y)

    @property
    def angle(self):
        """Угол вектора относительно оси OX"""
        angle = math.atan2(self._y, self._x)
        return angle

    @property
    def angleDeg(self):
        """Угол вектора относительно оси OX, градусы"""
        return  math.degrees(self.angle)

    def __add__(self, v):
        """Оператор +"""
        return Vector(self.x + v.x, self.y + v.y)

    def __sub__(self, v):
        """Оператор -"""
        return Vector(self.x - v.x, self.y - v.y)

    def __mul__(self, k):
        """Оператор * - умножение на константу"""
        return Vector(self.x * k, self.y * k)

    def __neg__ (self):
        """Унарный минус"""
        return self * (-1.0)

    def __div__(self, k):
        """Оператор / - деление на константу"""
        return Vector(self.x / k, self.y / k)

    def __str__(self):
        """Преобразование в строку"""
        return ('({0}, {1})'.format(self._x, self._y))

    def __eq__(self, v):
        """Оператор =="""
        return self._x == v._x and self._y == v._y

    def normalize(self):
        """Нормализация вектора"""
        length = self.length
        if length == 0:
            return Vector.zero
        
        x = self._x / length
        y = self._y / length
        return Vector(x, y)

    def rotate(self, axis):
        """Повернуть вектор относительно оси OX'"""
        radius = self.length
        angle = axis.angle + self.angle
        return Vector(radius * math.cos(angle), radius * math.sin(angle))

    def toStr(self, format = 'c'):
        if format == 'c':
            return self.__str__()
        if format == 'r':
            return ('({0} ^ {1})'.format(self.length, math.degrees(self.angle)))
        return '?'
    
    @staticmethod
    def fromPolar(radius, angle):
        """Создание вектора из полярных координат"""
        angle = math.radians(angle)
        return Vector(radius * math.cos(angle), radius * math.sin(angle))
    
    zero  = None # Нулевой вектор
    unitX = None # Единичный вектор оси OX
    unitY = None # Единичный вектор оси OY
Vector.zero  = Vector(0, 0)
Vector.unitX = Vector(1, 0)
Vector.unitY = Vector(0, 1)

class VectorHistory:
    """История изменений значений вектора"""

    def __init__(self, ownerName, parameterName):
        self._ownerName = ownerName         # Название объекта, которому принадлежит величина
        self._parameterName = parameterName # Название величины
        self._ts = []                       # Время
        self._xs = []                       # Значения X
        self._ys = []                       # Значения Y
        self._rs = []                       # Значения модуля
        self._counter = 0

    def put(self, t, v):
        """Записать значение v в момент времени t"""
        self._ts.append(t)
        self._xs.append(v.x)
        self._ys.append(v.y)
        self._rs.append(v.length)

    def plot(self, plot):
        """Вывести историю на график"""
        plot.plot(self._ts, self._xs, '--', label = ('{0}/{1}x'.format(self._ownerName, self._parameterName)))
        plot.plot(self._ts, self._ys, '--', label = ('{0}/{1}y'.format(self._ownerName, self._parameterName)))
        plot.plot(self._ts, self._rs, '-',   label = ('{0}/|{1}|'.format(self._ownerName, self._parameterName)))
        
    def trajectory(self, plot, index = None):
        """Вывести траекторию на график"""
        if index == None:
            return plot.plot(self._xs, self._ys, '-', label = self._ownerName,linewidth = 2)
        else:
            indices = range(int(index)) 
            xs = [self._xs[i] for i in indices]
            ys = [self._ys[i] for i in indices]
            return plot.plot(xs, ys, '-',  color = 'r', linewidth = 2)

    def quiver(self,  vectors, plot, index  = None, step = 1):
        """Вывести на график поле векторов, используея self как XY и vectors как UV"""
        if index == None and step == 1:
            plot.quiver(self._xs, self._ys, vectors._xs, vectors._ys)
        else:
            if index == None:
                index = 0
            x, y, u, v = [], [], [], []
            for i in range(len(self._ts)):
                if i >= index and divmod(i, step)[1] == 0:
                    x.append(self._xs[i])
                    y.append(self._ys[i])
                    u.append(vectors._xs[i])
                    v.append(vectors._ys[i])
            plot.quiver(x, y, u, v)

class VectorWithHistory:
    """Вектор с историей изменений"""
    
    def __init__(self, ownerName, parameterName):
         self._value  = Vector.zero
         self._history = VectorHistory(ownerName, parameterName)

    @property
    def value(self):
        """Текущее значение"""
        return self._value;
    @value.setter
    def value(self, value):
        self._value = value;

    @property
    def history(self):
        """История значений"""
        return self._history

    def put(self, t):
        """Записать текущее значение в момент времени t"""
        self._history.put(t, self._value)