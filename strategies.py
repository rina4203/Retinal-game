import math
from abc import ABC, abstractmethod

class MovementStrategy(ABC):
    @abstractmethod
    def move(self, obj, dt):
        pass

class LinearFall(MovementStrategy):
    def move(self, obj, dt):
        obj.y += obj.velocity * dt

class SineFall(MovementStrategy):
    def move(self, obj, dt):
        obj.y += obj.velocity * dt
        obj.x += math.sin(obj.y * 0.05) * 3