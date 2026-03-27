import random
from entities import Star, GoldenGlow
from strategies import LinearFall, SineFall

class EntityFactory:
    @staticmethod
    def create_falling_object():
        x = random.randint(50, 750)
        y = -50
        strat = random.choice([LinearFall(), SineFall()])
        star = Star(x, y, strat)
        
        # Шанс 20% на GoldenGlow (патерн DECORATOR)
        if random.random() > 0.8:
            return GoldenGlow(star)
        return star