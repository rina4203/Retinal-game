import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# --- MOCKING PYGAME ---
# Ми імітуємо (мокаємо) pygame перед імпортом reti, 
# щоб тести не намагалися відкрити вікно або ініціалізувати аудіо драйвер.
sys.modules['pygame'] = MagicMock()
sys.modules['pygame.mixer'] = MagicMock()
sys.modules['pygame.font'] = MagicMock()
sys.modules['pygame.display'] = MagicMock()
sys.modules['pygame.time'] = MagicMock()
sys.modules['pygame.event'] = MagicMock()

# Тепер імпортуємо основний файл гри
import reti

class TestHelperFunctions(unittest.TestCase):
    """Тестування допоміжних функцій."""

    def test_clamp(self):
        """Перевіряє функцію clamp (обмеження значень)."""
        # Тест: значення в межах діапазону
        self.assertEqual(reti.clamp(5, 0, 10), 5)
        # Тест: значення менше мінімуму
        self.assertEqual(reti.clamp(-5, 0, 10), 0)
        # Тест: значення більше максимуму
        self.assertEqual(reti.clamp(15, 0, 10), 10)

class TestLocalization(unittest.TestCase):
    """Тестування системи перекладу (i18n)."""

    def setUp(self):
        # Скидаємо стан перед кожним тестом
        reti.loc.current_lang = "EN"

    def test_default_language(self):
        """Перевірка мови за замовчуванням."""
        self.assertEqual(reti.loc.current_lang, "EN")
        self.assertEqual(reti.loc.get("START"), "START")

    def test_toggle_language(self):
        """Перевірка перемикання мови."""
        reti.loc.toggle_lang()
        self.assertEqual(reti.loc.current_lang, "UA")
        self.assertEqual(reti.loc.get("START"), "ГРАТИ")
        
        reti.loc.toggle_lang()
        self.assertEqual(reti.loc.current_lang, "EN")

    def test_missing_key(self):
        """Якщо ключа немає, має повернутися сам ключ."""
        self.assertEqual(reti.loc.get("MISSING_KEY"), "MISSING_KEY")

class TestThemeManager(unittest.TestCase):
    """Тестування менеджера тем."""

    def setUp(self):
        self.mgr = reti.ThemeManager()

    def test_initial_theme(self):
        self.assertEqual(self.mgr.current_theme, "dark")
        # Перевірка, що темна тема має правильний колір фону (приклад)
        self.assertEqual(self.mgr.get("bg_color"), (20, 20, 45))

    def test_theme_transition_start(self):
        """Перевірка початку переходу."""
        self.mgr.start_transition()
        self.assertTrue(self.mgr.is_transitioning)
        self.assertEqual(self.mgr.target_theme, "light")

class TestGameLogic(unittest.TestCase):
    """Тестування логіки гри (економіка, збереження, рекорди)."""

    def setUp(self):
        # Ініціалізуємо гру в headless режимі (без вікна), 
        # хоча завдяки мокам вище це вже безпечно.
        self.game = reti.Game(headless=True)
        # Очищаємо дані для чистоти тесту
        self.game.data = {
            "high_score": 0, 
            "currency": 100, 
            "inventory": ["Default"], 
            "equipped": {"color": "Default"}
        }

    def test_highscore_logic(self):
        """Перевірка оновлення рекорду."""
        # 1. Новий рекорд
        self.game.update_high_score(500)
        self.assertEqual(self.game.get_high_score(), 500)

        # 2. Гірший результат не повинен перезаписати рекорд
        self.game.update_high_score(300)
        self.assertEqual(self.game.get_high_score(), 500)

        # 3. Кращий результат повинен оновити
        self.game.update_high_score(600)
        self.assertEqual(self.game.get_high_score(), 600)

    def test_currency_logic(self):
        """Перевірка додавання валюти."""
        initial = self.game.get_currency()
        self.game.add_currency(50)
        self.assertEqual(self.game.get_currency(), initial + 50)

    def test_shop_buying_success(self):
        """Купівля товару, коли грошей вистачає."""
        self.game.data["currency"] = 100
        item_price = 50
        item_id = "BlueColor"
        category = "color"

        result = self.game.buy_item(category, item_id, item_price)

        self.assertTrue(result, "Купівля мала пройти успішно")
        self.assertEqual(self.game.get_currency(), 50, "Гроші мали списатися")
        self.assertTrue(self.game.has_item(category, item_id), "Предмет має бути в інвентарі")

    def test_shop_buying_failure(self):
        """Купівля товару, коли грошей НЕ вистачає."""
        self.game.data["currency"] = 10
        item_price = 50
        item_id = "GoldColor"
        category = "color"

        result = self.game.buy_item(category, item_id, item_price)

        self.assertFalse(result, "Купівля не мала відбутися")
        self.assertEqual(self.game.get_currency(), 10, "Гроші не мали списатися")
        self.assertFalse(self.game.has_item(category, item_id), "Предмет не мав додатися")

    def test_equip_item(self):
        """Перевірка екіпірування предметів."""
        self.game.equip_item("color", "Red")
        self.assertTrue(self.game.is_equipped("color", "Red"))
        self.assertEqual(self.game.get_equipped("color"), "Red")

    @patch('builtins.open', new_callable=unittest.mock.mock_open)
    @patch('json.dump')
    def test_save_data(self, mock_json_dump, mock_open):
        """Перевірка, чи викликається збереження файлу."""
        self.game._save_data()
        mock_open.assert_called_with(reti.SAVE_FILE, 'w')
        self.assertTrue(mock_json_dump.called)

class TestGameObjects(unittest.TestCase):
    """Тестування логіки ігрових об'єктів (без рендерингу)."""

    def setUp(self):
        self.game_mock = MagicMock()
        # Повертаємо дефолтні налаштування
        self.game_mock.get_equipped.return_value = "Default" 

    def test_star_logic(self):
        """Перевірка логіки зірки/ноти."""
        star = reti.Star(speed_multiplier=1.0, game_ref=self.game_mock)
        
        initial_y = star.get_y()
        # Емулюємо проходження 1 секунди
        star.update(dt=1.0, speed_multiplier=1.0)
        
        self.assertGreater(star.get_y(), initial_y, "Зірка мала впасти вниз (y має збільшитися)")
        self.assertIn(star.get_size_category(), ['small', 'medium', 'large'])

    def test_basket_movement(self):
        """Перевірка логіки руху кошика."""
        basket = reti.Basket(game=self.game_mock)
        initial_x = basket._x
        
        # Імітуємо натискання клавіші вправо
        keys_mock = MagicMock()
        keys_mock.__getitem__.side_effect = lambda k: True if k == reti.pygame.K_RIGHT else False
        
        basket.update(dt=1.0, keys=keys_mock, speed_multiplier=1.0)
        
        self.assertGreater(basket._x, initial_x, "Кошик мав зміститися вправо")

if __name__ == '__main__':
    unittest.main()