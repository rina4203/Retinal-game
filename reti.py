import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

import pygame
import random
import math
import json
from abc import ABC, abstractmethod
from typing import List, TypeVar, Generic, Optional

# --- ШЛЯХИ ДО ФАЙЛІВ ---
SOUND_FOLDER = "sound"
HIGHSCORE_FILE = "highscore.txt"
SAVE_FILE = "save_data.json"
FONT_FILE = "font.otf"

# --- НАЛАШТУВАННЯ ПІСЕНЬ ---
SONG_LIST = [
    {
        "name": "My Track",       
        "file": "song.mp3",       
        "bpm": 120,               
        "offset": 0.0,            
        "difficulty": "Custom"
    }
]

pygame.init()

# --- КОНСТАНТИ ---
WIDTH, HEIGHT = 500, 800
FPS = 60
MAX_PLATFORM_SPEED = 14
NUM_BG_STARS = 200
MAX_MISSED_STARS = 10

# Зони для ритм гри
LANE_WIDTH = WIDTH // 3
LANE_CENTERS = [LANE_WIDTH * 0.5, LANE_WIDTH * 1.5, LANE_WIDTH * 2.5]

# --- КОЛЬОРИ ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED_ERROR = (215, 80, 80)
GOLD = (240, 200, 80)
GREEN_BUY = (100, 200, 120)
PASTEL_CREAM = (255, 253, 208)

# Бохо палітра (для фону)
BOHO_BG = (135, 206, 250) # Небесно-блакитний

# Кольори для магазину
SHOP_COLORS = {
    "Default": None,
    "Red": (230, 100, 100),
    "Orange": (240, 160, 100),
    "Yellow": (240, 220, 100),
    "Green": (120, 180, 120),
    "Cyan": (100, 200, 200),
    "Blue": (100, 140, 200),
    "Purple": (160, 120, 200),
    "Pink": (230, 150, 180)
}

# --- ДОПОМІЖНІ ФУНКЦІЇ ---
def clamp(value, min_val, max_val):
    return max(min_val, min(value, max_val))

def draw_text(surf, text, font, x, y, color, align="center"):
    text_surface = font.render(str(text), True, color)
    text_rect = text_surface.get_rect()
    if align == "center":
        text_rect.midtop = (x, y)
    elif align == "topleft":
        text_rect.topleft = (x, y)
    elif align == "topright":
        text_rect.topright = (x, y)
    elif align == "left":
        text_rect.midleft = (x, y)
    surf.blit(text_surface, text_rect)

# --- МЕНЕДЖЕР ТЕМ ---
class ThemeManager:
    def __init__(self):
        self.current_theme = "dark"
        self.transition_alpha = 0
        self.is_transitioning = False
        self.target_theme = ""
        self.transition_speed = 15

        self.light_clouds = []
        
        # 1. МАЛЕНЬКІ ХМАРИНКИ (ФОН) - Додаємо їх першими
        # Вони маленькі, дуже прозорі і повільні
        for _ in range(15):
             self.light_clouds.append({
                "type": "cloud",
                "x": random.randint(0, WIDTH),
                "y": random.randint(-150, HEIGHT),
                "size": random.randint(15, 35),    # <-- МАЛЕНЬКИЙ РОЗМІР
                "speed": random.uniform(0.2, 0.6), # Повільніші
                "alpha": random.randint(40, 90),   # Дуже прозорі
                "sway_speed": random.uniform(0.5, 1.5),
                "sway_amp": random.randint(5, 15)
            })

        # 2. ВЕЛИКІ ХМАРИНКИ (ПЕРЕДНІЙ ПЛАН) - Ті, що були раніше
        # Вони великі, яскравіші і швидші
        for _ in range(7): 
            self.light_clouds.append({
                "type": "cloud",
                "x": random.randint(0, WIDTH),
                "y": random.randint(-150, HEIGHT), 
                "size": random.randint(60, 120),   # <-- ВЕЛИКИЙ РОЗМІР
                "speed": random.uniform(0.6, 1.3), # Швидші
                "alpha": random.randint(120, 200), # Яскравіші
                "sway_speed": random.uniform(0.5, 1.5),
                "sway_amp": random.randint(10, 40)
            })

        self.themes = {
            "dark": {
                "bg_color": (20, 20, 45),
                "text_color": (240, 240, 250),
                "platform_color": (100, 149, 237),
                "particle_color": (255, 255, 204),
                "btn_color": (60, 40, 90),
                "btn_hover": (80, 60, 110),
                "btn_active": (100, 70, 140),
                "btn_text_color": (255, 255, 255),
                "slider_line": (150, 150, 180),
                "slider_knob": (255, 255, 255),
                "modal_bg": (30, 30, 60),
                # Темна тема: Хвилі
                "bg_elements": [
                    {"type": "wave", "color": (60, 20, 80, 100), "amp": 70, "freq": 0.012, "speed": 0.3, "y": 610},
                    {"type": "wave", "color": (80, 60, 140, 100), "amp": 50, "freq": 0.007, "speed": -0.45, "y": 620},
                    {"type": "wave", "color": (40, 40, 100, 100), "amp": 30, "freq": 0.01, "speed": 0.6, "y": 600}
                ],
                "has_bg_stars": True,
                "star_style": "glow" 
            },
            "light": {
                "bg_color": BOHO_BG, 
                "text_color": (255, 255, 255),
                "platform_color": (20, 50, 100),
                "particle_color": None,
                "btn_color": (20, 50, 100),
                "btn_hover": (40, 70, 130),
                "btn_active": (65, 105, 225),
                "btn_text_color": (255, 255, 255),
                "slider_line": (255, 255, 255),
                "slider_knob": (20, 50, 100),
                "modal_bg": (135, 206, 250),
                # Світла тема: Хмаринки (Всі разом)
                "bg_elements": self.light_clouds,
                "has_bg_stars": False,
                "star_style": "ball"
            }
        }
        
        self.light_theme_star_colors = [
            (255, 105, 180), # Pink
            (50, 205, 50),   # Green
            (255, 215, 0),   # Gold
            (255, 69, 0)     # Red-Orange
        ]
        
        self.shop_colors = {
            "Default": None,
            "Red": (220, 60, 60), "Orange": (255, 140, 0), "Yellow": (255, 215, 0),
            "Green": (50, 205, 50), "Cyan": (0, 255, 255), "Blue": (30, 144, 255),
            "Purple": (138, 43, 226), "Pink": (255, 105, 180)
        }

    def get(self, key):
        return self.themes[self.current_theme][key]

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

# --- АБСТРАКТНІ КЛАСИ ---

class GameObject(ABC):
    @abstractmethod
    def update(self, dt, **kwargs): pass
    @abstractmethod
    def draw(self, surface): pass

class UIElement(GameObject):
    def __init__(self, x, y, w, h):
        self._rect = pygame.Rect(x, y, w, h)
    def update(self, dt, **kwargs): pass

class GameState(ABC):
    def __init__(self, game):
        self._game = game
    @abstractmethod
    def handle_event(self, event): pass
    @abstractmethod
    def update(self, dt): pass
    @abstractmethod
    def draw(self, surface): pass

T = TypeVar('T', bound=GameObject)
class ObjectManager(Generic[T]):
    def __init__(self):
        self._objects: List[T] = []
    def add(self, obj: T):
        self._objects.append(obj)
    def remove(self, obj: T):
        if obj in self._objects: self._objects.remove(obj)
    def get_list(self) -> List[T]:
        return self._objects[:]
    def clear(self):
        self._objects.clear()
    def update_all(self, dt, **kwargs):
        for obj in self._objects[:]: obj.update(dt, **kwargs)
    def draw_all(self, surface):
        for obj in self._objects: obj.draw(surface)

# --- ІГРОВІ ОБ'ЄКТИ ---

class ProceduralWave(GameObject):
    """Малює хвилі АБО хмаринки з оптимізацією."""
    def __init__(self, index):
        self._index = index
        self._phase = random.uniform(0, 2 * math.pi)
        
        # Для плавності хмаринок
        self._wobble_speed = random.uniform(1.0, 2.0)
        self._update_params_from_theme()

    def _update_params_from_theme(self):
        elements = theme_mgr.get("bg_elements")
        
        # Перевірка, щоб індекс не вийшов за межі списку (важливо!)
        if self._index < len(elements):
            params = elements[self._index]
            self._type = params["type"]
            self._speed = params["speed"]
            
            if self._type == "wave":
                self._color = params["color"]
                self._amplitude = params["amp"]
                self._frequency = params["freq"]
                self._y_offset = params["y"]
                # Для хвиль потрібна велика surface
                self._surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            elif self._type == "cloud":
                self._x_base = params["x"]
                self._y_base = params["y"]
                self._radius = params["size"]
                self._alpha = params.get("alpha", 100)
                # Зчитуємо параметри хитання
                self._float_speed = params.get("sway_speed", 1.0)
                self._float_amp = params.get("sway_amp", 20)
                
                self._draw_x = self._x_base
                self._draw_y = self._y_base
        else:
            self._type = "none"
            self._speed = 0

    def update(self, dt, **kwargs):
        if kwargs.get("theme_switched"):
            self._update_params_from_theme()
        
        self._phase += self._speed * dt

        if self._type == "cloud":
            # --- ВЕРТИКАЛЬНИЙ РУХ (Зверху вниз) ---
            self._y_base += self._speed * 60 * dt
            
            # Якщо хмарка вилетіла за нижній край
            if self._y_base > HEIGHT + self._radius * 2: 
                self._y_base = -self._radius * 2
                self._x_base = random.randint(0, WIDTH)

            # --- ГОРИЗОНТАЛЬНЕ ХИТАННЯ ---
            current_time = pygame.time.get_ticks() / 1000.0
            sway_offset = math.sin(current_time * self._float_speed + self._index) * self._float_amp
            
            self._draw_x = self._x_base + sway_offset
            self._draw_y = self._y_base
            
        elif self._type == "wave":
             pass # Фаза вже оновлена вище

    def draw(self, surface):
        if self._type == "wave":
            self._surface.fill((0, 0, 0, 0))
            points = []
            for x in range(WIDTH + 1):
                y = self._amplitude * math.sin(self._frequency * x + self._phase) + self._y_offset
                points.append((x, y))
            points.append((WIDTH, HEIGHT))
            points.append((0, HEIGHT))
            pygame.draw.polygon(self._surface, self._color, points)
            surface.blit(self._surface, (0, 0))
            
        elif self._type == "cloud":
            # ОПТИМІЗОВАНЕ МАЛЮВАННЯ ХМАРИНКИ (маленька surface)
            pulse = math.sin(self._phase * self._wobble_speed) * 3
            current_radius = self._radius + pulse
            
            surf_size = int(current_radius * 3) 
            cloud_surf = pygame.Surface((surf_size, surf_size), pygame.SRCALPHA)
            center = (surf_size // 2, surf_size // 2)
            
            outer_radius = current_radius * 1.5
            inner_radius = current_radius * 0.7
            
            outer_color = (255, 255, 255, int(self._alpha * 0.4))
            inner_color = (255, 255, 255, self._alpha)
            
            pygame.draw.circle(cloud_surf, outer_color, center, int(outer_radius))
            pygame.draw.circle(cloud_surf, inner_color, center, int(inner_radius))
            
            blit_x = self._draw_x - surf_size // 2
            blit_y = self._draw_y - surf_size // 2
            surface.blit(cloud_surf, (blit_x, blit_y))

class Particle(GameObject):
    def __init__(self, x, y, specific_color=None):
        self._x = x
        self._y = y
        self._vx = random.uniform(-150, 150)
        self._vy = random.uniform(-150, 150)
        self._size = random.uniform(2, 5)
        
        if specific_color:
            self._color = specific_color
        else:
            self._color = theme_mgr.get("particle_color")
            if self._color is None: self._color = (255, 255, 255)
        self._lifetime = random.uniform(0.2, 0.5)

    def update(self, dt, **kwargs):
        self._x += self._vx * dt
        self._y += self._vy * dt
        self._lifetime -= dt
        self._size -= 5 * dt
        return self._lifetime > 0 and self._size > 1

    def draw(self, surface):
        if self._size > 0:
            pygame.draw.circle(surface, self._color, (self._x, self._y), int(self._size))

class Basket(GameObject):
    def __init__(self, game):
        self._game = game
        self._base_width = 150 
        self._height = 20
        self._x = WIDTH // 2 - self._base_width // 2
        self._y = HEIGHT - 80
        self._base_vel = 9
        self._vel = self._base_vel

    def _get_current_properties(self):
        size_mod = self._game.get_equipped("size") 
        color_name = self._game.get_equipped("color")
        width = self._base_width + (size_mod * 30)
        color = theme_mgr.shop_colors.get(color_name)
        if color is None:
            color = theme_mgr.get("platform_color")
        return width, color

    def update(self, dt, **kwargs):
        width, _ = self._get_current_properties()
        keys = kwargs.get("keys")
        speed_multiplier = kwargs.get("speed_multiplier", 1.0)
        if not keys: return

        calculated_vel = self._base_vel + (speed_multiplier - 1.0) * 3.0
        self._vel = min(MAX_PLATFORM_SPEED, calculated_vel)

        if keys[pygame.K_LEFT] and self._x > 0:
            self._x -= self._vel
        if keys[pygame.K_RIGHT] and self._x < WIDTH - width:
            self._x += self._vel

    def get_vel(self) -> float: return self._vel
    
    def get_rect(self) -> pygame.Rect:
        width, _ = self._get_current_properties()
        return pygame.Rect(self._x, self._y, width, self._height)

    def draw(self, surface):
        width, color = self._get_current_properties()
        rect = pygame.Rect(self._x, self._y, width, self._height)
        pygame.draw.rect(surface, color, rect, border_radius=5)

class Currency(GameObject):
    def __init__(self, speed_multiplier):
        self._x = random.randint(50, WIDTH - 50)
        self._y = random.randint(-200, -20)
        self._speed = 3.0 * speed_multiplier
        self._size = 20
        self._angle = 0

    def update(self, dt, **kwargs):
        speed_multiplier = kwargs.get("speed_multiplier", 1.0)
        self._y += self._speed * speed_multiplier
        self._angle += 2
        
    def get_y(self) -> float: return self._y
    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(self._x - self._size, self._y - self._size, self._size*2, self._size*2)

    def draw(self, surface):
        if theme_mgr.current_theme == "dark":
            points = [
                (self._x, self._y - self._size),
                (self._x + self._size/2, self._y),
                (self._x, self._y + self._size),
                (self._x - self._size/2, self._y)
            ]
            pygame.draw.polygon(surface, (255, 255, 100), points)
            pygame.draw.circle(surface, (255, 255, 200, 100), (int(self._x), int(self._y)), int(self._size * 0.8))
        else:
            # Квітка для світлої теми
            for i in range(5):
                angle_rad = math.radians(self._angle + i * 72)
                px = self._x + math.cos(angle_rad) * (self._size * 0.6)
                py = self._y + math.sin(angle_rad) * (self._size * 0.6)
                pygame.draw.circle(surface, (255, 180, 180), (int(px), int(py)), int(self._size * 0.5))
            pygame.draw.circle(surface, (255, 220, 100), (int(self._x), int(self._y)), int(self._size * 0.4))

class Star(GameObject):
    def __init__(self, speed_multiplier, game_ref, fixed_x=None):
        self._game = game_ref
        if fixed_x is not None:
            self._x = fixed_x
            self._is_rhythm_note = True
        else:
            self._x = random.randint(100, WIDTH - 100)
            self._is_rhythm_note = False
            
        self._y = random.randint(-200, -20)
        self._z = random.uniform(0.1, 1.0)
        self._base_speed = random.uniform(1.4, 1.6)
        self._vel = self._base_speed * speed_multiplier
        self._base_size = 5 + self._z * 5 
        self._points = int(15 - (self._z * 10))
        self._blink_timer = random.uniform(0, 2 * math.pi)
        self._blink_speed = random.uniform(1.0, 3.0)
        self._trail = [] 
        self._max_trail_length = 15 
        
        if theme_mgr.current_theme == "light":
            self._specific_color = random.choice(theme_mgr.light_theme_star_colors)
            self._base_size = 25  
        else:
            self._specific_color = None

    def get_size_category(self) -> str:
        if self._z > 0.7: return 'large'
        elif self._z > 0.4: return 'medium'
        else: return 'small'
    
    def get_color(self):
        if self._specific_color: return self._specific_color
        else: return PASTEL_CREAM

    def set_y(self, y):
        self._y = y

    def update(self, dt, **kwargs):
        speed_multiplier = kwargs.get("speed_multiplier", 1.0)
        rhythm_speed = kwargs.get("speed")
        if self._is_rhythm_note and rhythm_speed:
             self._vel = rhythm_speed * speed_multiplier
        else:
             self._vel = self._base_speed * speed_multiplier
        
        self._y += self._vel
        self._blink_timer += self._blink_speed * dt

        if self._is_rhythm_note:
            self._trail.append((self._x, self._y))
            if len(self._trail) > self._max_trail_length:
                self._trail.pop(0)

    def get_y(self) -> float: return self._y
    def get_points(self) -> int: return self._points
    def get_pos(self) -> tuple[float, float]: return (self._x, self._y)
    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(self._x - self._base_size, self._y - self._base_size,
                            self._base_size * 2, self._base_size * 2)

    def draw(self, surface):
        shape = self._game.get_equipped("shape")
        p = clamp((math.sin(self._blink_timer) * 0.5 + 0.5), 0, 1)
        current_size = self._base_size * (0.7 + p * 0.6)
        
        if theme_mgr.current_theme == "light":
            base_color = self._specific_color
            halo_color = (255, 255, 255)
        else:
            base_color = (255, 229, 180) 
            halo_color = (255, 255, 204) 

        if self._is_rhythm_note:
             if len(self._trail) > 1:
                for i, (tx, ty) in enumerate(self._trail):
                    alpha = int(150 * (i / len(self._trail)))
                    t_size = int(self._base_size * (i / len(self._trail)) * 0.8)
                    if t_size < 1: t_size = 1
                    s_trail = pygame.Surface((t_size*2, t_size*2), pygame.SRCALPHA)
                    pygame.draw.circle(s_trail, (*base_color, alpha), (t_size, t_size), t_size)
                    surface.blit(s_trail, (tx - t_size, ty - t_size))
             pygame.draw.circle(surface, base_color, (self._x, self._y), int(self._base_size))
        else:
            if shape == "Square":
                rect = pygame.Rect(self._x - current_size, self._y - current_size, current_size*2, current_size*2)
                pygame.draw.rect(surface, base_color, rect)
            elif shape == "Triangle":
                points = [
                    (self._x, self._y - current_size),
                    (self._x + current_size, self._y + current_size),
                    (self._x - current_size, self._y + current_size)
                ]
                pygame.draw.polygon(surface, base_color, points)
            else: 
                if theme_mgr.current_theme == "light":
                      pygame.draw.circle(surface, base_color, (self._x, self._y), int(self._base_size))
                      pygame.draw.circle(surface, (255,255,255), (self._x - self._base_size*0.3, self._y - self._base_size*0.3), int(self._base_size*0.2))
                else:
                      outer_alpha = int(100 * 0.5)
                      s = pygame.Surface((int(current_size*4), int(current_size*4)), pygame.SRCALPHA)
                      pygame.draw.circle(s, (*halo_color, outer_alpha), (int(current_size*2), int(current_size*2)), int(current_size*1.6))
                      pygame.draw.circle(s, (*base_color, 255), (int(current_size*2), int(current_size*2)), int(current_size))
                      surface.blit(s, (self._x - current_size*2, self._y - current_size*2))


# --- UI CLASSES ---

class Button(UIElement):
    def __init__(self, x, y, w, h, text, btn_type, font, color_override=None):
        super().__init__(x, y, w, h)
        self._text = text
        self._btn_type = btn_type
        self._is_hovered = False
        self._font = font
        self._color_override = color_override

    def update(self, dt, **kwargs):
        mouse_pos = kwargs.get("mouse_pos")
        if mouse_pos:
            self._is_hovered = self._rect.collidepoint(mouse_pos)
        else:
            self._is_hovered = False

    def draw(self, surface):
        if self._color_override:
             color = self._color_override
             if self._is_hovered:
                 color = (min(255, color[0]+20), min(255, color[1]+20), min(255, color[2]+20))
        else:
            if self._btn_type == "active":
                color = theme_mgr.get("btn_active")
            elif self._is_hovered:
                color = theme_mgr.get("btn_hover")
            else:
                color = theme_mgr.get("btn_color")
            
        pygame.draw.rect(surface, color, self._rect, border_radius=10)
        text_y = self._rect.centery - self._font.get_height() // 2
        text_col = theme_mgr.get("btn_text_color")
        draw_text(surface, self._text, self._font, self._rect.centerx, text_y, color=text_col)

    def check_click(self, event) -> bool:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self._is_hovered
        return False

    def set_type(self, btn_type):
        self._btn_type = btn_type
    def set_text(self, text):
        self._text = text

class Slider(UIElement):
    def __init__(self, x, y, w, h, min_val, max_val, initial_val, font):
        super().__init__(x, y, w, h)
        self._min_val = min_val
        self._max_val = max_val
        self._current_val = initial_val
        self._font = font
        self._is_dragging = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self._rect.collidepoint(event.pos):
                self._is_dragging = True
                self._update_val_from_pos(event.pos[0])
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self._is_dragging = False
        elif event.type == pygame.MOUSEMOTION:
            if self._is_dragging:
                self._update_val_from_pos(event.pos[0])

    def _update_val_from_pos(self, mouse_x):
        rel_x = mouse_x - self._rect.x
        pct = clamp(rel_x / self._rect.w, 0.0, 1.0)
        self._current_val = self._min_val + pct * (self._max_val - self._min_val)

    def get_value(self):
        return self._current_val

    def draw(self, surface):
        line_col = theme_mgr.get("slider_line")
        line_y = self._rect.centery
        pygame.draw.line(surface, line_col, (self._rect.left, line_y), (self._rect.right, line_y), 4)

        pct = (self._current_val - self._min_val) / (self._max_val - self._min_val)
        knob_x = self._rect.left + pct * self._rect.w
        knob_col = theme_mgr.get("slider_knob")
        pygame.draw.circle(surface, knob_col, (int(knob_x), int(line_y)), 10)
        txt_col = theme_mgr.get("text_color")
        val_percent = int(pct * 100)
        draw_text(surface, f"{val_percent}", self._font, self._rect.right + 15, self._rect.y, color=txt_col, align="left")

class ConfirmationModal:
    def __init__(self, game):
        self._game = game
        self._rect = pygame.Rect(50, 300, 400, 200)
        self._btn_yes = Button(100, 420, 100, 50, "YES", "normal", game.FONT_SMALL)
        self._btn_no = Button(300, 420, 100, 50, "NO", "normal", game.FONT_SMALL)

    def handle_event(self, event):
        if self._btn_yes.check_click(event): return True
        elif self._btn_no.check_click(event): return False
        return None

    def update(self):
        mouse_pos = pygame.mouse.get_pos()
        self._btn_yes.update(0, mouse_pos=mouse_pos)
        self._btn_no.update(0, mouse_pos=mouse_pos)

    def draw(self, surface):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0,0,0, 150))
        surface.blit(overlay, (0,0))
        bg_col = theme_mgr.get("modal_bg")
        border_col = theme_mgr.get("platform_color")
        text_col = theme_mgr.get("text_color")
        if theme_mgr.current_theme == "dark": text_col = WHITE
        pygame.draw.rect(surface, bg_col, self._rect, border_radius=15)
        pygame.draw.rect(surface, border_col, self._rect, width=3, border_radius=15)
        draw_text(surface, "Are you sure?", self._game.FONT_MEDIUM, WIDTH//2, 330, text_col)
        self._btn_yes.draw(surface)
        self._btn_no.draw(surface)

# --- СТАНИ ГРИ ---

class MenuState(GameState):
    def __init__(self, game):
        super().__init__(game)
        # START (Center Top)
        self._btn_start = Button(WIDTH//2 - 100, 250, 200, 60, "START", "normal", game.FONT_MEDIUM)
        
        # LEFT COLUMN (Rhythm, Theme)
        self._btn_rhythm = Button(30, 340, 200, 60, "RHYTHM", "normal", game.FONT_MEDIUM)
        self._btn_theme = Button(30, 420, 200, 60, "", "normal", game.FONT_MEDIUM) # Text set later
        
        # RIGHT COLUMN (Shop, Settings)
        self._btn_shop = Button(270, 340, 200, 60, "SHOP", "normal", game.FONT_MEDIUM)
        self._btn_settings = Button(270, 420, 200, 60, "SETTINGS", "normal", game.FONT_MEDIUM)
        
        # QUIT (Center Bottom)
        self._btn_quit = Button(WIDTH//2 - 100, 520, 200, 60, "QUIT", "normal", game.FONT_MEDIUM)
        
        self._buttons = [self._btn_start, self._btn_rhythm, self._btn_shop, self._btn_settings, self._btn_theme, self._btn_quit]
        self._confirm_modal = None
        
        self._update_theme_btn()

    def _update_theme_btn(self):
        # Button text shows the TARGET theme
        theme_text = "LIGHT" if theme_mgr.current_theme == "dark" else "DARK"
        self._btn_theme.set_text(theme_text)

    def handle_event(self, event):
        if self._confirm_modal:
            res = self._confirm_modal.handle_event(event)
            if res is True: self._game.stop()
            elif res is False: self._confirm_modal = None
            return

        if self._btn_start.check_click(event):
            self._game.change_state(PlayingState(self._game))
        elif self._btn_rhythm.check_click(event):
             self._game.change_state(RhythmSelectionState(self._game))
        elif self._btn_shop.check_click(event):
            self._game.change_state(ShopState(self._game))
        elif self._btn_settings.check_click(event):
            self._game.change_state(SettingsState(self._game))
        elif self._btn_theme.check_click(event):
            theme_mgr.start_transition()
        elif self._btn_quit.check_click(event):
            self._confirm_modal = ConfirmationModal(self._game)
            
        self._update_theme_btn()

    def update(self, dt):
        if self._confirm_modal:
            self._confirm_modal.update()
            return
        mouse_pos = pygame.mouse.get_pos()
        for btn in self._buttons: btn.update(dt, mouse_pos=mouse_pos)

    def draw(self, surface):
        draw_text(surface, "Retinal", self._game.FONT_BIG, WIDTH // 2, 150, color=theme_mgr.get("text_color"))
        for btn in self._buttons: btn.draw(surface)
        if self._confirm_modal: self._confirm_modal.draw(surface)

class ShopState(GameState):
    def __init__(self, game):
        super().__init__(game)
        self._current_tab = "Colors"
        self._btn_back = Button(WIDTH//2 - 100, 720, 200, 50, "BACK", "normal", game.FONT_MEDIUM)
        
        self._btn_tab_colors = Button(20, 100, 140, 40, "Colors", "normal", game.FONT_SMALL)
        self._btn_tab_sizes = Button(180, 100, 140, 40, "Sizes", "normal", game.FONT_SMALL)
        self._btn_tab_shapes = Button(340, 100, 140, 40, "Shapes", "normal", game.FONT_SMALL)
        
        # RESET BUTTON
        self._btn_reset = Button(WIDTH//2 - 100, 650, 200, 40, "RESET DEFAULTS", "normal", game.FONT_SMALL)
        
        self._tabs = [self._btn_tab_colors, self._btn_tab_sizes, self._btn_tab_shapes]
        self._items = []
        self._create_item_buttons()
        
    def _create_item_buttons(self):
        self._items = []
        game = self._game
        
        if self._current_tab == "Colors":
            items = [("Red", 10), ("Orange", 20), ("Yellow", 30), ("Green", 40), 
                     ("Cyan", 50), ("Blue", 60), ("Purple", 70), ("Pink", 80)]
            for i, (name, price) in enumerate(items):
                x = 50 if i % 2 == 0 else 260
                y = 180 + (i // 2) * 120
                self._items.append(ShopItemButton(x, y, 190, 100, name, price, "color", game))
        
        elif self._current_tab == "Sizes":
            items = [("Large", 100, 1), ("Huge", 250, 2), ("Gigantic", 500, 3)]
            for i, (name, price, val) in enumerate(items):
                y = 180 + i * 120
                self._items.append(ShopItemButton(100, y, 300, 100, name, price, "size", game, val=val))
                
        elif self._current_tab == "Shapes":
            items = [("Square", 200), ("Triangle", 300)]
            for i, (name, price) in enumerate(items):
                y = 180 + i * 120
                self._items.append(ShopItemButton(100, y, 300, 100, name, price, "shape", game))

    def handle_event(self, event):
        if self._btn_back.check_click(event):
            self._game.change_state(MenuState(self._game))
        
        if self._btn_reset.check_click(event):
            # Reset logic
            self._game.equip_item("color", "Default")
            self._game.equip_item("size", 0)
            self._game.equip_item("shape", "Star")
        
        if self._btn_tab_colors.check_click(event): self._current_tab = "Colors"; self._create_item_buttons()
        elif self._btn_tab_sizes.check_click(event): self._current_tab = "Sizes"; self._create_item_buttons()
        elif self._btn_tab_shapes.check_click(event): self._current_tab = "Shapes"; self._create_item_buttons()
        
        for item in self._items:
            item.handle_event(event)

    def update(self, dt):
        mouse_pos = pygame.mouse.get_pos()
        self._btn_back.update(dt, mouse_pos=mouse_pos)
        self._btn_reset.update(dt, mouse_pos=mouse_pos)
        for tab in self._tabs: tab.update(dt, mouse_pos=mouse_pos)
        for item in self._items: item.update(dt, mouse_pos=mouse_pos)

    def draw(self, surface):
        txt_col = theme_mgr.get("text_color")
        draw_text(surface, f"Shop - {self._current_tab}", self._game.FONT_MEDIUM, WIDTH // 2, 30, color=txt_col)
        draw_text(surface, f"Currency: {self._game.get_currency()}", self._game.FONT_SMALL, WIDTH - 100, 30, GOLD)
        
        self._btn_back.draw(surface)
        self._btn_reset.draw(surface)
        for tab in self._tabs: tab.draw(surface)
        for item in self._items: item.draw(surface)

class ShopItemButton(UIElement):
    def __init__(self, x, y, w, h, name, price, category, game, val=None):
        super().__init__(x, y, w, h)
        self._name = name
        self._price = price
        self._category = category
        self._game = game
        self._val = val if val is not None else name
        self._is_hovered = False
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self._is_hovered:
            if self._game.has_item(self._category, self._val):
                self._game.equip_item(self._category, self._val)
            else:
                self._game.buy_item(self._category, self._val, self._price)

    def update(self, dt, **kwargs):
        mouse_pos = kwargs.get("mouse_pos")
        if mouse_pos:
            self._is_hovered = self._rect.collidepoint(mouse_pos)
        else:
            self._is_hovered = False

    def draw(self, surface):
        color = (50, 50, 80)
        if self._is_hovered: color = (70, 70, 100)
        pygame.draw.rect(surface, color, self._rect, border_radius=10)
        
        owned = self._game.has_item(self._category, self._val)
        equipped = self._game.is_equipped(self._category, self._val)
        
        status_text = f"{self._price}"
        status_color = WHITE
        
        if equipped:
            status_text = "EQUIPPED"
            status_color = GREEN_BUY
        elif owned:
            status_text = "OWNED"
            status_color = (150, 255, 150)
        elif self._game.get_currency() < self._price:
            status_color = RED_ERROR
            
        draw_text(surface, self._name, self._game.FONT_SMALL, self._rect.centerx, self._rect.top + 20, WHITE)
        draw_text(surface, status_text, self._game.FONT_TINY, self._rect.centerx, self._rect.bottom - 30, status_color)

class RhythmSelectionState(GameState):
    def __init__(self, game):
        super().__init__(game)
        self._buttons = []
        start_y = 250
        for i, song in enumerate(SONG_LIST):
            btn = Button(WIDTH//2 - 150, start_y + i * 80, 300, 60, song["name"], "normal", game.FONT_SMALL)
            self._buttons.append(btn)
        self._btn_back = Button(WIDTH//2 - 100, 650, 200, 50, "BACK", "normal", game.FONT_MEDIUM)
        self._buttons.append(self._btn_back)

    def handle_event(self, event):
        if self._btn_back.check_click(event):
            self._game.change_state(MenuState(self._game))
        for i, btn in enumerate(self._buttons[:-1]):
            if btn.check_click(event):
                selected_song = SONG_LIST[i]
                self._game.change_state(RhythmGameState(self._game, selected_song))

    def update(self, dt):
        mouse_pos = pygame.mouse.get_pos()
        for btn in self._buttons: btn.update(dt, mouse_pos=mouse_pos)

    def draw(self, surface):
        txt_col = theme_mgr.get("text_color")
        draw_text(surface, "Select Song", self._game.FONT_MEDIUM, WIDTH // 2, 150, color=txt_col)
        for btn in self._buttons: btn.draw(surface)

class SettingsState(GameState):
    def __init__(self, game):
        super().__init__(game)
        self._current_view = "main"
        self._btn_to_audio = Button(WIDTH//2 - 100, 300, 200, 50, "AUDIO", "normal", game.FONT_MEDIUM)
        self._btn_to_diff = Button(WIDTH//2 - 100, 370, 200, 50, "DIFFICULTY", "normal", game.FONT_MEDIUM)
        self._btn_back_main = Button(WIDTH//2 - 100, 600, 200, 50, "BACK", "normal", game.FONT_MEDIUM)
        
        self._slider_music = Slider(100, 300, 300, 20, 0.0, 1.0, pygame.mixer.music.get_volume(), game.FONT_TINY)
        self._slider_sfx = Slider(100, 400, 300, 20, 0.0, 1.0, game.sfx_volume, game.FONT_TINY)
        self._btn_back_sub = Button(WIDTH//2 - 100, 600, 200, 50, "BACK", "normal", game.FONT_MEDIUM)
        
        self._btn_easy = Button(WIDTH//2 - 100, 300, 200, 50, "Easy", "normal", game.FONT_SMALL)
        self._btn_medium = Button(WIDTH//2 - 100, 370, 200, 50, "Normal", "normal", game.FONT_SMALL)
        self._btn_hard = Button(WIDTH//2 - 100, 440, 200, 50, "Hard", "normal", game.FONT_SMALL)
        self._update_button_states()

    def _update_button_states(self):
        settings = self._game.get_settings()
        self._btn_easy.set_type("active" if settings["star_rate_name"] == "Easy" else "normal")
        self._btn_medium.set_type("active" if settings["star_rate_name"] == "Normal" else "normal")
        self._btn_hard.set_type("active" if settings["star_rate_name"] == "Hard" else "normal")

    def handle_event(self, event):
        self._update_button_states()
        if self._current_view == "main":
            if self._btn_to_audio.check_click(event): self._current_view = "audio"
            elif self._btn_to_diff.check_click(event): self._current_view = "difficulty"
            elif self._btn_back_main.check_click(event): self._game.change_state(MenuState(self._game))
        elif self._current_view == "audio":
            self._slider_music.handle_event(event)
            self._slider_sfx.handle_event(event)
            pygame.mixer.music.set_volume(self._slider_music.get_value())
            self._game.sfx_volume = self._slider_sfx.get_value()
            if self._btn_back_sub.check_click(event): self._current_view = "main"
        elif self._current_view == "difficulty":
            settings = self._game.get_settings()
            if self._btn_easy.check_click(event): settings["star_rate"] = 130; settings["star_rate_name"] = "Easy"
            elif self._btn_medium.check_click(event): settings["star_rate"] = 100; settings["star_rate_name"] = "Normal"
            elif self._btn_hard.check_click(event): settings["star_rate"] = 80; settings["star_rate_name"] = "Hard"
            elif self._btn_back_sub.check_click(event): self._current_view = "main"

    def update(self, dt):
        mouse_pos = pygame.mouse.get_pos()
        if self._current_view == "main":
            for btn in [self._btn_to_audio, self._btn_to_diff, self._btn_back_main]: btn.update(dt, mouse_pos=mouse_pos)
        elif self._current_view == "audio": self._btn_back_sub.update(dt, mouse_pos=mouse_pos)
        elif self._current_view == "difficulty":
            for btn in [self._btn_easy, self._btn_medium, self._btn_hard, self._btn_back_sub]: btn.update(dt, mouse_pos=mouse_pos)

    def draw(self, surface):
        txt_col = theme_mgr.get("text_color")
        if self._current_view == "main":
            draw_text(surface, "Settings", self._game.FONT_BIG, WIDTH // 2, 150, color=txt_col)
            self._btn_to_audio.draw(surface); self._btn_to_diff.draw(surface); self._btn_back_main.draw(surface)
        elif self._current_view == "audio":
            draw_text(surface, "Audio Settings", self._game.FONT_MEDIUM, WIDTH // 2, 150, color=txt_col)
            draw_text(surface, "Music Volume:", self._game.FONT_SMALL, WIDTH // 2, 270, color=txt_col)
            self._slider_music.draw(surface)
            draw_text(surface, "SFX Volume:", self._game.FONT_SMALL, WIDTH // 2, 370, color=txt_col)
            self._slider_sfx.draw(surface)
            self._btn_back_sub.draw(surface)
        elif self._current_view == "difficulty":
            draw_text(surface, "Difficulty", self._game.FONT_MEDIUM, WIDTH // 2, 150, color=txt_col)
            self._btn_easy.draw(surface); self._btn_medium.draw(surface); self._btn_hard.draw(surface); self._btn_back_sub.draw(surface)

class GameOverState(GameState):
    def __init__(self, game, score):
        super().__init__(game)
        self._score = score
        self._game.save_high_score(score)
        self._high_score = self._game.get_high_score()
        self._btn_retry = Button(WIDTH//2 - 100, 400, 200, 50, "RETRY", "normal", game.FONT_MEDIUM)
        self._btn_menu = Button(WIDTH//2 - 100, 470, 200, 50, "MENU", "normal", game.FONT_MEDIUM)

    def handle_event(self, event):
        if self._btn_retry.check_click(event): self._game.change_state(PlayingState(self._game))
        elif self._btn_menu.check_click(event): self._game.change_state(MenuState(self._game))

    def update(self, dt):
        mouse_pos = pygame.mouse.get_pos()
        self._btn_retry.update(dt, mouse_pos=mouse_pos)
        self._btn_menu.update(dt, mouse_pos=mouse_pos)

    def draw(self, surface):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        surface.blit(overlay, (0, 0))
        draw_text(surface, "GAME OVER", self._game.FONT_BIG, WIDTH // 2, 150, RED_ERROR)
        draw_text(surface, f"Score: {self._score}", self._game.FONT_MEDIUM, WIDTH // 2, 250, WHITE)
        draw_text(surface, f"High Score: {self._high_score}", self._game.FONT_SMALL, WIDTH // 2, 300, (255, 215, 0))
        self._btn_retry.draw(surface)
        self._btn_menu.draw(surface)

class PausedState(GameState):
    def __init__(self, game, previous_state):
        super().__init__(game)
        self._previous_state = previous_state
        self._font = game.FONT_BIG
        # Кнопка RESUME
        self._btn_resume = Button(WIDTH//2 - 100, HEIGHT//2 - 30, 200, 60, "RESUME", "normal", game.FONT_MEDIUM)
        # Кнопка MENU
        self._btn_menu = Button(WIDTH//2 - 100, HEIGHT//2 + 50, 200, 60, "MENU", "normal", game.FONT_MEDIUM)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
             self._game.change_state(self._previous_state)
        
        if self._btn_resume.check_click(event):
            self._game.change_state(self._previous_state)
        elif self._btn_menu.check_click(event):
            # Скидаємо гучність музики перед виходом
            pygame.mixer.music.set_volume(0.5)
            self._game.change_state(MenuState(self._game))

    def update(self, dt):
        mouse_pos = pygame.mouse.get_pos()
        self._btn_resume.update(dt, mouse_pos=mouse_pos)
        self._btn_menu.update(dt, mouse_pos=mouse_pos)

    def draw(self, surface):
        # 1. Спочатку малюємо гру, яка була на фоні (застиглий кадр)
        self._previous_state.draw(surface)
        
        # 2. Малюємо напівпрозорий чорний прямокутник на весь екран
        # Це затемнить світлу тему і зробить текст видимим
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180)) # 180 - рівень прозорості (0-255)
        surface.blit(overlay, (0, 0))

        # 3. Малюємо текст і кнопки
        draw_text(surface, "PAUSED", self._font, WIDTH // 2, HEIGHT // 3, WHITE)
        self._btn_resume.draw(surface)
        self._btn_menu.draw(surface)

class PlayingState(GameState):
    def __init__(self, game):
        super().__init__(game)
        self._basket = Basket(game)
        self._star_manager = ObjectManager[GameObject]()
        self._particle_manager = ObjectManager[Particle]()
        self.reset_game()

    def reset_game(self):
        self._score = 0
        self._combo = 0
        self._missed_stars = 0
        self._speed_multiplier = 1.0
        self._star_add_counter = 0
        self._current_add_rate = self._game.get_settings()["star_rate"]
        self._star_manager.clear()
        self._particle_manager.clear()

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            self._game.change_state(PausedState(self._game, self))

    def _spawn_stars(self):
        self._star_add_counter += 1
        if self._star_add_counter >= self._current_add_rate:
            self._star_add_counter = 0
            if random.random() < 0.05: 
                self._star_manager.add(Currency(self._speed_multiplier))
            else:
                num_to_spawn = 1
                if self._speed_multiplier > 3.5: num_to_spawn = 3
                elif self._speed_multiplier > 2.0: num_to_spawn = 2
                for _ in range(num_to_spawn):
                    self._star_manager.add(Star(self._speed_multiplier, self._game))

    def _handle_collisions(self):
        missed_star = False
        basket_rect = self._basket.get_rect()
        for obj in self._star_manager.get_list()[:]:
            if obj.get_y() > HEIGHT:
                self._star_manager.remove(obj)
                if isinstance(obj, Star):
                    missed_star = True
                    self._missed_stars += 1
                    self._score = max(0, self._score - 5)
                    if self._missed_stars >= MAX_MISSED_STARS:
                        self._game.update_high_score(self._score)
                        self._game.change_state(GameOverState(self._game, self._score))
                        return
            elif obj.get_rect().colliderect(basket_rect):
                if isinstance(obj, Currency):
                    self._game.add_currency(1)
                    self._game.play_catch_sound() 
                elif isinstance(obj, Star):
                    self._game.play_catch_sound()
                    self._score += obj.get_points() + self._combo
                    self._combo += 1
                    if self._speed_multiplier < 5.0:
                        self._speed_multiplier = min(self._speed_multiplier + 0.03, 5.0)
                    num_particles = random.randint(8, 12)
                    star_pos = obj.get_pos()
                    star_color = obj.get_color()
                    for _ in range(num_particles):
                        self._particle_manager.add(Particle(star_pos[0], star_pos[1], star_color))
                self._star_manager.remove(obj)
        if missed_star: self._combo = 0

    def update(self, dt):
        keys = pygame.key.get_pressed()
        self._basket.update(dt, keys=keys, speed_multiplier=self._speed_multiplier)
        self._spawn_stars()
        self._star_manager.update_all(dt, speed_multiplier=self._speed_multiplier)
        self._handle_collisions()
        for particle in self._particle_manager.get_list()[:]:
            if not particle.update(dt):
                self._particle_manager.remove(particle)

    def draw(self, surface):
        self._basket.draw(surface)
        self._star_manager.draw_all(surface)
        self._particle_manager.draw_all(surface)
        txt_col = theme_mgr.get("text_color")
        draw_text(surface, f"Score: {self._score}", self._game.FONT_MEDIUM, 60, 20, color=txt_col, align="topleft")
        draw_text(surface, f"Combo: x{self._combo}", self._game.FONT_SMALL, 60, 60, color=txt_col, align="topleft")
        missed_text = f"Missed: {self._missed_stars}/{MAX_MISSED_STARS}"
        draw_text(surface, missed_text, self._game.FONT_SMALL, 60, 100, color=RED_ERROR, align="topleft")
        draw_text(surface, f"Speed: {self._speed_multiplier:.2f}x", self._game.FONT_TINY, WIDTH - 80, 20, color=txt_col, align="topright")
        draw_text(surface, f"Platform: {self._basket.get_vel():.1f}", self._game.FONT_TINY, WIDTH - 80, 50, color=txt_col, align="topright")

class RhythmGameState(GameState):
    def __init__(self, game, song_data):
        super().__init__(game)
        self._basket = Basket(game)
        self._star_manager = ObjectManager[Star]()
        self._particle_manager = ObjectManager[Particle]()
        self._song_data = song_data
        self._bpm = song_data["bpm"]
        self._beat_interval = 60.0 / self._bpm
        self._next_beat_time = song_data["offset"]
        self._timer = 0.0
        self._speed = 5.0
        self._score = 0
        self._is_playing = True
        self._audio_gate_timer = 0.0
        self._audio_gated = False
        
        pygame.mixer.music.stop()
        try:
            path = os.path.join(SOUND_FOLDER, song_data["file"])
            pygame.mixer.music.load(path)
            pygame.mixer.music.set_volume(0) 
            pygame.mixer.music.play()
        except Exception as e:
            print(f"Error loading rhythm song: {e}")

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            pygame.mixer.music.set_volume(0.5) 
            self._game.change_state(MenuState(self._game))

    def update(self, dt):
        if not self._is_playing: return
        if not pygame.mixer.music.get_busy():
             self._game.update_high_score(self._score)
             self._game.change_state(GameOverState(self._game, self._score))

        # --- GATING LOGIC ---
        if self._audio_gate_timer > 0:
            self._audio_gate_timer -= dt
        else:
            if not self._audio_gated:
                pygame.mixer.music.set_volume(0)
                self._audio_gated = True
        
        keys = pygame.key.get_pressed()
        self._basket.update(dt, keys=keys, speed_multiplier=1.2)
        self._timer += dt
        
        if self._timer >= self._next_beat_time:
            self._spawn_rhythm_note()
            self._next_beat_time += self._beat_interval * 2
            
        self._star_manager.update_all(dt, speed_multiplier=1.0)
        
        basket_rect = self._basket.get_rect()
        for star in self._star_manager.get_list()[:]:
            if star.get_y() > HEIGHT:
                pygame.mixer.music.set_volume(0.5)
                self._game.update_high_score(self._score)
                self._game.change_state(GameOverState(self._game, self._score))
                return
            elif star.get_rect().colliderect(basket_rect):
                pygame.mixer.music.set_volume(1.0)
                self._audio_gate_timer = 0.5 
                self._audio_gated = False
                self._score += 10
                star_pos = star.get_pos()
                star_color = star.get_color()
                for _ in range(10):
                    self._particle_manager.add(Particle(star_pos[0], star_pos[1], star_color))
                self._star_manager.remove(star)
        for particle in self._particle_manager.get_list()[:]:
            if not particle.update(dt):
                self._particle_manager.remove(particle)

    def _spawn_rhythm_note(self):
        lane_x = random.choice(LANE_CENTERS)
        star = Star(self._speed, self._game, fixed_x=int(lane_x))
        star.set_y(-50)
        self._star_manager.add(star)

    def draw(self, surface):
        self._basket.draw(surface)
        self._star_manager.draw_all(surface)
        self._particle_manager.draw_all(surface)
        txt_col = theme_mgr.get("text_color")
        draw_text(surface, f"Score: {self._score}", self._game.FONT_MEDIUM, 60, 20, color=txt_col, align="topleft")

class Game:
    def __init__(self):
        pygame.mixer.pre_init(44100, -16, 2, 512)
        pygame.init()
        self._window = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Retinal")
        self._clock = pygame.time.Clock()
        self._running = True
        self._settings = {"star_rate": 100, "star_rate_name": "Normal"}
        self.sfx_volume = 0.5
        self.data = {
            "high_score": 0,
            "currency": 0, 
            "inventory": ["Default", "Star", "Default_Size"],
            "equipped": {"color": "Default", "shape": "Star", "size": 0}
        }
        self._load_data()
        
        if self.data["currency"] < 10000:
             self.data["currency"] = 1000000
             self._save_data()

        self._load_fonts()
        self._create_background()
        self._menu_music_path = os.path.join(SOUND_FOLDER, "menu_sound.mp3")
        self._game_music_path = os.path.join(SOUND_FOLDER, "game_sound.mp3")
        self._sound_effect_paths = {"hight": os.path.join(SOUND_FOLDER, "hight.mp3")}
        self._current_music_path: Optional[str] = None
        self._catch_sound: Optional[pygame.mixer.Sound] = None
        self._sound_channel_star: Optional[pygame.mixer.Channel] = None
        self._load_audio()
        self._current_state: GameState = MenuState(self)
        self.play_music(self._menu_music_path, volume=0.5)

    def _load_data(self):
        if os.path.exists(SAVE_FILE):
            try:
                with open(SAVE_FILE, 'r') as f:
                    loaded_data = json.load(f)
                    for key in self.data:
                        if key in loaded_data:
                            self.data[key] = loaded_data[key]
            except:
                print("Error loading save file.")

    def _save_data(self):
        try:
            with open(SAVE_FILE, 'w') as f:
                json.dump(self.data, f)
        except:
            print("Error saving data.")

    def update_high_score(self, score):
        if score > self.data["high_score"]:
            self.data["high_score"] = score
            self._save_data()

    def get_high_score(self):
        return self.data["high_score"]

    def get_currency(self):
        return self.data["currency"]

    def add_currency(self, amount):
        self.data["currency"] += amount
        self._save_data()
        
    def has_item(self, category, item_id):
        if item_id == "Default" or item_id == "Star" or item_id == 0: return True
        return item_id in self.data["inventory"]
        
    def buy_item(self, category, item_id, price):
        if self.data["currency"] >= price:
            self.data["currency"] -= price
            self.data["inventory"].append(item_id)
            self._save_data()
            return True
        return False
        
    def equip_item(self, category, item_id):
        self.data["equipped"][category] = item_id
        self._save_data()

    def is_equipped(self, category, item_id):
        return self.data["equipped"].get(category) == item_id

    def get_equipped(self, category):
        return self.data["equipped"].get(category)

    def _load_fonts(self):
        try:
            self.FONT_BIG = pygame.font.Font(FONT_FILE, 70)
            self.FONT_MEDIUM = pygame.font.Font(FONT_FILE, 40)
            self.FONT_SMALL = pygame.font.Font(FONT_FILE, 30)
            self.FONT_TINY = pygame.font.Font(FONT_FILE, 24)
        except Exception:
            self.FONT_BIG = pygame.font.SysFont("Arial", 60, bold=True)
            self.FONT_MEDIUM = pygame.font.SysFont("Arial", 36)
            self.FONT_SMALL = pygame.font.SysFont("Arial", 28)
            self.FONT_TINY = pygame.font.SysFont("Arial", 22)

    def _create_background(self):
        # 1. СВІТЛА ТЕМА: Рахуємо скільки хмаринок у списку bg_elements
        # Зараз там 15 (малі) + 7 (великі) = 22
        num_clouds = len(theme_mgr.themes["light"]["bg_elements"])
        
        self._waves_manager = ObjectManager[ProceduralWave]()
        
        # Створюємо їх усі
        for i in range(num_clouds):
             self._waves_manager.add(ProceduralWave(i))
             
        # 2. ТЕМНА ТЕМА: Генеруємо зірки
        self._bg_stars = []
        for _ in range(NUM_BG_STARS):
            self._bg_stars.append({'pos': (random.randint(0, WIDTH), random.randint(0, HEIGHT)), 'radius': random.randint(1, 2)})

    def _load_audio(self):
        try:
            hight_path = self._sound_effect_paths.get("hight")
            if hight_path and os.path.exists(hight_path):
                 self._catch_sound = pygame.mixer.Sound(hight_path)
                 self._sound_channel_star = pygame.mixer.Channel(0)
            else:
                 self._catch_sound = None
                 self._sound_channel_star = None
        except pygame.error as e:
            self._catch_sound = None
            self._sound_channel_star = None

    def play_catch_sound(self):
        if self._sound_channel_star and self._catch_sound:
            self._catch_sound.set_volume(self.sfx_volume)
            self._sound_channel_star.play(self._catch_sound)

    def play_music(self, music_path: str, fade_ms: int = 1000, volume: float = 0.5):
        if not os.path.exists(music_path):
             self._current_music_path = None
             return
        if music_path == self._current_music_path and pygame.mixer.music.get_busy():
            pygame.mixer.music.set_volume(volume)
            return
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.fadeout(fade_ms)
        try:
            pygame.mixer.music.load(music_path)
            pygame.mixer.music.set_volume(volume)
            pygame.mixer.music.play(-1, fade_ms=fade_ms)
            self._current_music_path = music_path
        except pygame.error:
            self._current_music_path = None

    def run(self):
        while self._running:
            dt = self._clock.tick(FPS) / 1000.0
            switched = theme_mgr.update()
            self._handle_events()
            self._update(dt, theme_switched=switched)
            self._draw()
        pygame.quit()

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.stop()
            self._current_state.handle_event(event)

    def _update(self, dt, theme_switched=False):
        self._waves_manager.update_all(dt, theme_switched=theme_switched)
        self._current_state.update(dt)

    def _draw(self):
        self._window.fill(theme_mgr.get("bg_color"))
        if theme_mgr.get("has_bg_stars"):
            for star in self._bg_stars:
                pygame.draw.circle(self._window, WHITE, star['pos'], star['radius'])
        self._waves_manager.draw_all(self._window)
        self._current_state.draw(self._window)
        theme_mgr.draw_transition(self._window)
        pygame.display.flip()

    def change_state(self, new_state: GameState):
        self._current_state = new_state
        if isinstance(new_state, (MenuState, SettingsState, GameOverState, RhythmSelectionState, ShopState)):
             self.play_music(self._menu_music_path, volume=pygame.mixer.music.get_volume())
        elif isinstance(new_state, PlayingState):
            self.play_music(self._game_music_path, volume=0.3)

    def stop(self):
        self._running = False

    def get_settings(self) -> dict:
        return self._settings

if __name__ == "__main__":
    game = Game()
    game.run()