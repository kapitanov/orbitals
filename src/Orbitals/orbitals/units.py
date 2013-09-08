class MassUnits:
    """Утилитарный класс для удобного задания величин массы""" 

    def kg(self, x):
        """Значение в килограммах"""
        return x

    def g(self, x):
        """Значение в граммах"""
        return self.kg(x * 1E-3)

    def t(self, x):
        """Значение в тоннах"""
        return self.kg(x * 1E3)

    def kt(self, x):
        """Значение в килотоннах"""
        return self.kg(x * 1E6)

class ForceUnits:
    """Утилитарный класс для удобного задания величин силы""" 

    def N(self, x):
        """Значение в ньютонах"""
        return x

    def kN(self, x):
        """Значение в килоньютонах"""
        return self.N(x * 1E3)

    def MN(self, x):
        """Значение в меганьютонах"""
        return self.N(x * 1E6)

class DimentionUnits:
    """Утилитарный класс для удобного задания величин размерности"""

    def m(self, x):
        """Значение в метрах"""
        return x

    def km(self, x):
        """Значение в километрах"""
        return self.m(x * 1E3)

class TimeUnits:
    """Утилитарный класс для удобного задания величин времени""" 

    def seconds(self, x):
        """Значение в секундах"""
        return x

    def minutes(self, x):
        """Значение в минутах"""
        return self.seconds(x*60)

    def hours(self, x):
        """Значение в часах"""
        return self.minutes(x*60)

    def days(self, x):
        """Значение в днях"""
        return self.hours(x*24)

class UnitsFacade:
    """Утилитарный класс для удобного задания величин"""
    def __init__(self):
        self._mass      = MassUnits()
        self._force     = ForceUnits()
        self._dimention = DimentionUnits()
        self._time      = TimeUnits()

    @property
    def mass(self):
        """Масса"""
        return self._mass

    @property
    def force(self):
        """Сила"""
        return self._force

    @property
    def dimention(self):
        """Размер"""
        return self._dimention

    @property
    def time(self):
        """Время"""
        return self._time

factory = UnitsFacade()