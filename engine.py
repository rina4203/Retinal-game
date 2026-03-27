import pygame
import random
import math
import logging
import time
import functools
from abc import ABC, abstractmethod
from typing import List, TypeVar, Generic
from config import *

# --- UTILS ---
def clamp(value, min_val, max_val): return max(min_val, min(value, max_val))

def draw_text(surf, text, font, x, y, color, align="center"):
    text_surface = font.render(str(text), True, color)
    text_rect = text_surface.get_rect()
    if align == "center": text_rect.midtop = (x, y)
    elif align == "topleft": text_rect.topleft = (x, y)
    elif align == "topright": text_rect.topright = (x, y)
    elif align == "left": text_rect.midleft = (x, y)
    surf.blit(text_surface, text_rect)

def measure_time(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        execution_time = (end_time - start_time) * 1000
        logging.info(f"Performance: {func.__name__} took {execution_time:.4f} ms")
        return result
    return wrapper

# --- MANAGERS ---
class LocalizationManager:
    def __init__(self):
        self.current_lang = "EN"
        self.translations = {
            "EN": {
                "START": "START", "RHYTHM": "RHYTHM", "SHOP": "SHOP", "SETTINGS": "SETTINGS", "QUIT": "QUIT",
                "LANG": "LANGUAGE: EN", "LIGHT": "LIGHT", "DARK": "DARK", "BACK": "BACK", "RESET": "RESET", 
                "GAME_OVER": "GAME OVER", "SCORE": "Score:", "HIGH_SCORE": "High Score:", "RETRY": "RETRY", 
                "MENU": "MENU", "PAUSED": "PAUSED", "RESUME": "RESUME", "NO_MUSIC": "NO MUSIC FILE", 
                "ARE_YOU_SURE": "Are you sure?", "YES": "YES", "NO": "NO", "AUDIO": "AUDIO", "DIFFICULTY": "DIFFICULTY",
                "MUSIC_VOL": "Music:", "SFX_VOL": "SFX:", "EASY": "Easy", "NORMAL": "Normal", "HARD": "Hard",
                "TAB_COLORS": "Colors", "TAB_SIZES": "Sizes", "TAB_SHAPES": "Shapes", "CURRENCY": "Cash:", 
                "OWNED": "OWNED", "EQUIPPED": "EQUIPPED", "Red": "Red", "Orange": "Orange", "Yellow": "Yellow", 
                "Green": "Green", "Cyan": "Cyan", "Blue": "Blue", "Purple": "Purple", "Pink": "Pink",
                "Large": "Large", "Huge": "Huge", "Gigantic": "Gigantic", "Square": "Square", "Triangle": "Triangle",
                "COMBO": "Combo:", "MISSED": "Missed:", "SPEED": "Speed:", "PLATFORM": "Platform:", "SELECT_SONG": "Select Song"
            },
            "UA": {
                "START": "ГРАТИ", "RHYTHM": "РИТМ", "SHOP": "МАГАЗИН", "SETTINGS": "ОПЦІЇ", "QUIT": "ВИХІД",
                "LANG": "МОВА: UA", "LIGHT": "СВІТЛА", "DARK": "ТЕМНА", "BACK": "НАЗАД", "RESET": "СКИНУТИ", 
                "GAME_OVER": "КІНЕЦЬ ГРИ", "SCORE": "Рахунок:", "HIGH_SCORE": "Рекорд:", "RETRY": "ЗНОВУ", 
                "MENU": "МЕНЮ", "PAUSED": "ПАУЗА", "RESUME": "ДАЛІ", "NO_MUSIC": "НЕМАЄ МУЗИКИ", 
                "ARE_YOU_SURE": "Ви впевнені?", "YES": "ТАК", "NO": "НІ", "AUDIO": "АУДІО", "DIFFICULTY": "РІВЕНЬ",
                "MUSIC_VOL": "Музика:", "SFX_VOL": "Звуки:", "EASY": "Легко", "NORMAL": "Норм", "HARD": "Важко",
                "TAB_COLORS": "Кольори", "TAB_SIZES": "Розмір", "TAB_SHAPES": "Форми", "CURRENCY": "Гроші:", 
                "OWNED": "Є ВЖЕ", "EQUIPPED": "ВЗЯТО", "Red": "Червоний", "Orange": "Оранж", "Yellow": "Жовтий", 
                "Green": "Зелений", "Cyan": "Блакитний", "Blue": "Синій", "Purple": "Фіолет", "Pink": "Рожевий",
                "Large": "Великий", "Huge": "Велет", "Gigantic": "Гігант", "Square": "Квадрат", "Triangle": "Трикутник",
                "COMBO": "Комбо:", "MISSED": "Пропуск:", "SPEED": "Швидк.:", "PLATFORM": "Платф.:", "SELECT_SONG": "Обери пісню"
            }
        }
    def get(self, key: str) -> str: return self.translations[self.current_lang].get(key, key)
    def toggle_lang(self):
        self.current_lang = "UA" if self.current_lang == "EN" else "EN"
        logging.info(f"Language switched to {self.current_lang}")

loc = LocalizationManager()

class ThemeManager:
    def __init__(self):
        self.current_theme = "dark"
        self.transition_alpha = 0
        self.is_transitioning = False
        self.target_theme = ""
        self.transition_speed = 15
        self.light_clouds = []
        for _ in range(15): self.light_clouds.append({ "type": "cloud", "x": random.randint(0, WIDTH), "y": random.randint(-150, HEIGHT), "size": random.randint(15, 35), "speed": random.uniform(0.2, 0.6), "alpha": random.randint(40, 90), "sway_speed": random.uniform(0.5, 1.5), "sway_amp": random.randint(5, 15) })
        for _ in range(7): self.light_clouds.append({ "type": "cloud", "x": random.randint(0, WIDTH), "y": random.randint(-150, HEIGHT), "size": random.randint(60, 120), "speed": random.uniform(0.6, 1.3), "alpha": random.randint(120, 200), "sway_speed": random.uniform(0.5, 1.5), "sway_amp": random.randint(10, 40) })

        self.themes = {
            "dark": {
                "bg_color": (20, 20, 45), "text_color": (240, 240, 250), "platform_color": (100, 149, 237), "particle_color": (255, 255, 204),
                "btn_color": (60, 40, 90), "btn_hover": (80, 60, 110), "btn_active": (100, 70, 140), "btn_text_color": (255, 255, 255),
                "slider_line": (150, 150, 180), "slider_knob": (255, 255, 255), "modal_bg": (30, 30, 60),
                "bg_elements": [ {"type": "wave", "color": (60, 20, 80, 100), "amp": 70, "freq": 0.012, "speed": 0.3, "y": 610}, {"type": "wave", "color": (80, 60, 140, 100), "amp": 50, "freq": 0.007, "speed": -0.45, "y": 620}, {"type": "wave", "color": (40, 40, 100, 100), "amp": 30, "freq": 0.01, "speed": 0.6, "y": 600} ],
                "has_bg_stars": True, "star_style": "glow" 
            },
            "light": {
                "bg_color": BOHO_BG, "text_color": (255, 255, 255), "platform_color": (20, 50, 100), "particle_color": None,
                "btn_color": (20, 50, 100), "btn_hover": (40, 70, 130), "btn_active": (65, 105, 225), "btn_text_color": (255, 255, 255),
                "slider_line": (255, 255, 255), "slider_knob": (20, 50, 100), "modal_bg": (135, 206, 250),
                "bg_elements": self.light_clouds, "has_bg_stars": False, "star_style": "ball"
            }
        }
        self.light_theme_star_colors = [ (255, 105, 180), (50, 205, 50), (255, 215, 0), (255, 69, 0) ]
        self.shop_colors = SHOP_COLORS

    def get(self, key): return self.themes[self.current_theme][key]
    def start_transition(self):
        self.target_theme = "light" if self.current_theme == "dark" else "dark"
        self.is_transitioning = True
        self.transition_alpha = 0
    def update(self):
        switched = False
        if self.is_transitioning:
            if self.current_theme != self.target_theme:
                self.transition_alpha += self.transition_speed
                if self.transition_alpha >= 255:
                    self.transition_alpha = 255
                    self.current_theme = self.target_theme
                    switched = True
            else:
                self.transition_alpha -= self.transition_speed
                if self.transition_alpha <= 0:
                    self.transition_alpha = 0
                    self.is_transitioning = False
        return switched
    def draw_transition(self, surface):
        if self.is_transitioning:
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.fill(BLACK)
            overlay.set_alpha(self.transition_alpha)
            surface.blit(overlay, (0, 0))

theme_mgr = ThemeManager()

# --- BASE CLASSES ---
class GameObject(ABC):
    @abstractmethod
    def update(self, dt, **kwargs): pass
    @abstractmethod
    def draw(self, surface): pass

class UIElement(GameObject):
    def __init__(self, x, y, w, h): self._rect = pygame.Rect(x, y, w, h)
    def update(self, dt, **kwargs): pass

class GameState(ABC):
    def __init__(self, game): self._game = game
    @abstractmethod
    def handle_event(self, event): pass
    @abstractmethod
    def update(self, dt): pass
    @abstractmethod
    def draw(self, surface): pass

T = TypeVar('T', bound=GameObject)
class ObjectManager(Generic[T]):
    def __init__(self): self._objects: List[T] = []
    def add(self, obj: T): self._objects.append(obj)
    def remove(self, obj: T): 
        if obj in self._objects: self._objects.remove(obj)
    def get_list(self) -> List[T]: return self._objects[:]
    def clear(self): self._objects.clear()
    def update_all(self, dt, **kwargs):
        for obj in self._objects[:]: obj.update(dt, **kwargs)
    def draw_all(self, surface):
        for obj in self._objects: obj.draw(surface)

# --- UI CLASSES ---
class Button(UIElement):
    def __init__(self, x, y, w, h, text_key, btn_type, font, color_override=None):
        super().__init__(x, y, w, h)
        self._text_key = text_key
        self._btn_type = btn_type; self._is_hovered = False; self._font = font; self._color_override = color_override
    def update(self, dt, **kwargs):
        mouse_pos = kwargs.get("mouse_pos")
        self._is_hovered = self._rect.collidepoint(mouse_pos) if mouse_pos else False
    def draw(self, surface):
        if self._color_override:
             color = self._color_override
             if self._is_hovered: color = (min(255, color[0]+20), min(255, color[1]+20), min(255, color[2]+20))
        else:
            if self._btn_type == "active": color = theme_mgr.get("btn_active")
            elif self._is_hovered: color = theme_mgr.get("btn_hover")
            else: color = theme_mgr.get("btn_color")
        pygame.draw.rect(surface, color, self._rect, border_radius=10)
        text_y = self._rect.centery - self._font.get_height() // 2
        text_col = theme_mgr.get("btn_text_color")
        draw_text(surface, loc.get(self._text_key), self._font, self._rect.centerx, text_y, color=text_col)
    def check_click(self, event) -> bool: return event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self._is_hovered
    def set_type(self, btn_type): self._btn_type = btn_type
    def set_text_key(self, key): self._text_key = key

class Slider(UIElement):
    def __init__(self, x, y, w, h, min_val, max_val, initial_val, font):
        super().__init__(x, y, w, h)
        self._min_val = min_val; self._max_val = max_val; self._current_val = initial_val; self._font = font; self._is_dragging = False
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self._rect.collidepoint(event.pos): self._is_dragging = True; self._update_val_from_pos(event.pos[0])
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1: self._is_dragging = False
        elif event.type == pygame.MOUSEMOTION and self._is_dragging: self._update_val_from_pos(event.pos[0])
    def _update_val_from_pos(self, mouse_x):
        rel_x = mouse_x - self._rect.x; pct = clamp(rel_x / self._rect.w, 0.0, 1.0)
        self._current_val = self._min_val + pct * (self._max_val - self._min_val)
    def get_value(self): return self._current_val
    def draw(self, surface):
        line_col = theme_mgr.get("slider_line"); line_y = self._rect.centery
        pygame.draw.line(surface, line_col, (self._rect.left, line_y), (self._rect.right, line_y), 4)
        pct = (self._current_val - self._min_val) / (self._max_val - self._min_val)
        knob_x = self._rect.left + pct * self._rect.w; knob_col = theme_mgr.get("slider_knob")
        pygame.draw.circle(surface, knob_col, (int(knob_x), int(line_y)), 10)
        txt_col = theme_mgr.get("text_color"); val_percent = int(pct * 100)
        draw_text(surface, f"{val_percent}", self._font, self._rect.right + 15, self._rect.y, color=txt_col, align="left")

class ConfirmationModal:
    def __init__(self, game):
        self._game = game; self._rect = pygame.Rect(50, 300, 400, 200)
        self._btn_yes = Button(100, 420, 100, 50, "YES", "normal", game.FONT_SMALL) 
        self._btn_no = Button(300, 420, 100, 50, "NO", "normal", game.FONT_SMALL)
    def handle_event(self, event):
        mouse_pos = pygame.mouse.get_pos()
        self._btn_yes.update(0, mouse_pos=mouse_pos); self._btn_no.update(0, mouse_pos=mouse_pos)
        if self._btn_yes.check_click(event): return True
        elif self._btn_no.check_click(event): return False
        return None
    def update(self):
        mouse_pos = pygame.mouse.get_pos()
        self._btn_yes.update(0, mouse_pos=mouse_pos); self._btn_no.update(0, mouse_pos=mouse_pos)
    def draw(self, surface):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA); overlay.fill((0,0,0, 150)); surface.blit(overlay, (0,0))
        bg_col = theme_mgr.get("modal_bg"); border_col = theme_mgr.get("platform_color"); text_col = theme_mgr.get("text_color")
        if theme_mgr.current_theme == "dark": text_col = WHITE
        pygame.draw.rect(surface, bg_col, self._rect, border_radius=15)
        pygame.draw.rect(surface, border_col, self._rect, width=3, border_radius=15)
        draw_text(surface, loc.get("ARE_YOU_SURE"), self._game.FONT_MEDIUM, WIDTH//2, 330, text_col) 
        self._btn_yes.draw(surface); self._btn_no.draw(surface)

class ShopItemButton(UIElement):
    def __init__(self, x, y, w, h, name, price, category, game, val=None):
        super().__init__(x, y, w, h)
        self._name = name; self._price = price; self._category = category; self._game = game; self._val = val if val is not None else name; self._is_hovered = False
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self._is_hovered:
            if self._game.has_item(self._category, self._val): self._game.equip_item(self._category, self._val)
            else: self._game.buy_item(self._category, self._val, self._price)
    def update(self, dt, **kwargs):
        mouse_pos = kwargs.get("mouse_pos")
        self._is_hovered = self._rect.collidepoint(mouse_pos) if mouse_pos else False
    def draw(self, surface):
        color = (50, 50, 80); 
        if self._is_hovered: color = (70, 70, 100)
        pygame.draw.rect(surface, color, self._rect, border_radius=10)
        owned = self._game.has_item(self._category, self._val); equipped = self._game.is_equipped(self._category, self._val)
        status_text = f"{self._price}"; status_color = WHITE
        if equipped: status_text = loc.get("EQUIPPED"); status_color = GREEN_BUY
        elif owned: status_text = loc.get("OWNED"); status_color = (150, 255, 150)
        elif self._game.get_currency() < self._price: status_color = RED_ERROR
        draw_text(surface, loc.get(self._name), self._game.FONT_SMALL, self._rect.centerx, self._rect.top + 20, WHITE)
        draw_text(surface, status_text, self._game.FONT_TINY, self._rect.centerx, self._rect.bottom - 30, status_color)