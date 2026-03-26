import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# --- МОКИНГ PYGAME (До імпорту модулів гри) ---
mock_pygame = MagicMock()

def mock_rect_side_effect(*args, **kwargs):
    rect = MagicMock()
    rect.colliderect.return_value = False 
    rect.x = args[0] if len(args) > 0 else 0
    rect.y = args[1] if len(args) > 1 else 0
    rect.w = args[2] if len(args) > 2 else 0
    rect.h = args[3] if len(args) > 3 else 0
    rect.width, rect.height = rect.w, rect.h
    rect.left, rect.top = rect.x, rect.y
    rect.right, rect.bottom = rect.x + rect.w, rect.y + rect.h
    rect.collidepoint.return_value = False
    return rect

mock_pygame.Rect = MagicMock(side_effect=mock_rect_side_effect)
sys.modules['pygame'] = mock_pygame
sys.modules['pygame.mixer'] = MagicMock()
sys.modules['pygame.font'] = MagicMock()
sys.modules['pygame.display'] = MagicMock()
sys.modules['pygame.time'] = MagicMock()

# --- ІМПОРТ ОНОВЛЕНИХ МОДУЛІВ ---
# Додаємо шлях, щоб Python бачив файли в папці Desktop/retinal
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import main
import engine
import entities
import states
from config import *

class TestRetinalMegaSuite(unittest.TestCase):
    def setUp(self):
        """Налаштування перед кожним тестом"""
        # Створюємо екземпляр гри в headless режимі
        self.game = main.Game(headless=True)
        
        # Скидаємо глобальні менеджери (Singletons)
        engine.loc.current_lang = "EN"
        engine.theme_mgr.current_theme = "dark"
        
        # Налаштування тестових даних гравця
        self.game.data = {
            "high_score": 0,
            "currency": 1000,
            "inventory": ["Default", "Star"],
            "equipped": {"color": "Default", "shape": "Star", "size": 0}
        }

    # =========================================================================
    # BLOCK 1: Engine & Utils (Тестуємо engine.py та config.py)
    # =========================================================================
    
    def test_01_math_clamp(self):
        self.assertEqual(engine.clamp(150, 0, 100), 100)
        self.assertEqual(engine.clamp(-50, 0, 100), 0)

    def test_02_localization_toggle(self):
        self.assertEqual(engine.loc.get("START"), "START")
        engine.loc.toggle_lang()
        self.assertEqual(engine.loc.current_lang, "UA")
        self.assertEqual(engine.loc.get("START"), "ГРАТИ")

    def test_03_theme_manager_transition(self):
        engine.theme_mgr.start_transition()
        self.assertTrue(engine.theme_mgr.is_transitioning)
        self.assertEqual(engine.theme_mgr.target_theme, "light")

    # =========================================================================
    # BLOCK 2: Entities (Тестуємо entities.py)
    # =========================================================================

    def test_04_basket_movement(self):
        basket = entities.Basket(self.game)
        initial_x = basket._x
        # Емулюємо натискання клавіші "Вправо"
        keys = {mock_pygame.K_LEFT: False, mock_pygame.K_RIGHT: True}
        basket.update(0.1, keys=keys)
        self.assertGreater(basket._x, initial_x)

    def test_05_star_properties(self):
        star = entities.Star(1.0, self.game)
        # Колір може бути або з пастельних, або None (для темної теми)
        self.assertTrue(star.get_color() is not None)
        start_y = star.get_y()
        star.update(0.1)
        self.assertGreater(star.get_y(), start_y)

    def test_06_currency_logic(self):
        curr = entities.Currency(1.0)
        self.assertIsInstance(curr.get_rect(), MagicMock)
        self.game.add_currency(100)
        self.assertEqual(self.game.get_currency(), 1100)

    # =========================================================================
    # BLOCK 3: State Management (Тестуємо states.py)
    # =========================================================================

    def test_07_state_transitions(self):
        """Тест перемикання станів (State Pattern)"""
        # Оскільки в headless режимі стан не ставиться автоматично, 
        # ми встановлюємо його вручну для тесту
        self.game.change_state(states.MenuState(self.game))
        self.assertIsInstance(self.game._current_state, states.MenuState)
        
        # Перемикаємося на ігровий стан
        new_state = states.PlayingState(self.game)
        self.game.change_state(new_state)
        self.assertIsInstance(self.game._current_state, states.PlayingState)

    def test_08_shop_logic_integration(self):
        # Поповнюємо баланс для покупки
        self.game.data["currency"] = 500
        # Спроба купити колір "Red" за 10
        res = self.game.buy_item("color", "Red", 10)
        self.assertTrue(res)
        self.assertEqual(self.game.get_currency(), 490)
        self.assertTrue(self.game.has_item("color", "Red"))

    # =========================================================================
    # BLOCK 4: Persistence & HighScore (Тестуємо main.py)
    # =========================================================================

    def test_09_highscore_update(self):
        self.game.data["high_score"] = 100
        self.game.update_high_score(250)
        self.assertEqual(self.game.get_high_score(), 250)
        # Нижчий результат не має перезаписувати
        self.game.update_high_score(50)
        self.assertEqual(self.game.get_high_score(), 250)

    def test_10_object_manager_lifecycle(self):
        mgr = engine.ObjectManager()
        p = entities.Particle(0, 0)
        mgr.add(p)
        self.assertEqual(len(mgr.get_list()), 1)
        mgr.clear()
        self.assertEqual(len(mgr.get_list()), 0)

if __name__ == "__main__":
    unittest.main()