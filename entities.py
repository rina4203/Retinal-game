import pygame
import random
import math
from config import *
from engine import GameObject, theme_mgr, clamp

class ProceduralWave(GameObject):
    def __init__(self, index):
        self._index = index; self._phase = random.uniform(0, 2 * math.pi); self._wobble_speed = random.uniform(1.0, 2.0)
        self._update_params_from_theme()

    def _update_params_from_theme(self):
        elements = theme_mgr.get("bg_elements")
        if self._index < len(elements):
            params = elements[self._index]; self._type = params["type"]; self._speed = params["speed"]
            if self._type == "wave":
                self._color = params["color"]; self._amplitude = params["amp"]; self._frequency = params["freq"]
                self._y_offset = params["y"]; self._surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            elif self._type == "cloud":
                self._x_base = params["x"]; self._y_base = params["y"]; self._radius = params["size"]
                self._alpha = params.get("alpha", 100); self._float_speed = params.get("sway_speed", 1.0)
                self._float_amp = params.get("sway_amp", 20); self._draw_x = self._x_base; self._draw_y = self._y_base
        else:
            self._type = "none"; self._speed = 0

    def update(self, dt, **kwargs):
        if kwargs.get("theme_switched"): self._update_params_from_theme()
        self._phase += self._speed * dt
        if self._type == "cloud":
            self._y_base += self._speed * 60 * dt
            if self._y_base > HEIGHT + self._radius * 2: 
                self._y_base = -self._radius * 2; self._x_base = random.randint(0, WIDTH)
            current_time = pygame.time.get_ticks() / 1000.0
            sway_offset = math.sin(current_time * self._float_speed + self._index) * self._float_amp
            self._draw_x = self._x_base + sway_offset; self._draw_y = self._y_base

    def draw(self, surface):
        if self._type == "wave":
            self._surface.fill((0, 0, 0, 0))
            points = [(x, self._amplitude * math.sin(self._frequency * x + self._phase) + self._y_offset) for x in range(WIDTH + 1)]
            points.extend([(WIDTH, HEIGHT), (0, HEIGHT)])
            pygame.draw.polygon(self._surface, self._color, points)
            surface.blit(self._surface, (0, 0))
        elif self._type == "cloud":
            pulse = math.sin(self._phase * self._wobble_speed) * 3
            current_radius = self._radius + pulse; surf_size = int(current_radius * 3) 
            cloud_surf = pygame.Surface((surf_size, surf_size), pygame.SRCALPHA)
            center = (surf_size // 2, surf_size // 2)
            pygame.draw.circle(cloud_surf, (255, 255, 255, int(self._alpha * 0.4)), center, int(current_radius * 1.5))
            pygame.draw.circle(cloud_surf, (255, 255, 255, self._alpha), center, int(current_radius * 0.7))
            surface.blit(cloud_surf, (self._draw_x - surf_size // 2, self._draw_y - surf_size // 2))

class Particle(GameObject):
    def __init__(self, x, y, specific_color=None):
        self._x = x; self._y = y; self._vx = random.uniform(-150, 150); self._vy = random.uniform(-150, 150)
        self._size = random.uniform(2, 5)
        self._color = specific_color if specific_color else (theme_mgr.get("particle_color") or (255, 255, 255))
        self._lifetime = random.uniform(0.2, 0.5)

    def update(self, dt, **kwargs):
        self._x += self._vx * dt; self._y += self._vy * dt; self._lifetime -= dt; self._size -= 5 * dt
        return self._lifetime > 0 and self._size > 1

    def draw(self, surface):
        if self._size > 0: pygame.draw.circle(surface, self._color, (self._x, self._y), int(self._size))

class Basket(GameObject):
    def __init__(self, game):
        self._game = game; self._base_width = 150; self._height = 20
        self._x = WIDTH // 2 - self._base_width // 2; self._y = HEIGHT - 80
        self._base_vel = 9; self._vel = self._base_vel

    def _get_current_properties(self):
        size_mod = self._game.get_equipped("size"); color_name = self._game.get_equipped("color")
        width = self._base_width + (size_mod * 30)
        color = theme_mgr.shop_colors.get(color_name) or theme_mgr.get("platform_color")
        return width, color

    def update(self, dt, **kwargs):
        width, _ = self._get_current_properties(); keys = kwargs.get("keys"); speed_multiplier = kwargs.get("speed_multiplier", 1.0)
        if not keys: return
        self._vel = min(MAX_PLATFORM_SPEED, self._base_vel + (speed_multiplier - 1.0) * 3.0)
        if keys[pygame.K_LEFT] or keys[pygame.K_a]: 
            if self._x > 0: self._x -= self._vel
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: 
            if self._x < WIDTH - width: self._x += self._vel

    def get_vel(self) -> float: return self._vel
    def get_rect(self) -> pygame.Rect:
        width, _ = self._get_current_properties(); return pygame.Rect(self._x, self._y, width, self._height)
    def draw(self, surface):
        width, color = self._get_current_properties(); rect = pygame.Rect(self._x, self._y, width, self._height)
        pygame.draw.rect(surface, color, rect, border_radius=5)

class Currency(GameObject):
    def __init__(self, speed_multiplier):
        self._x = random.randint(50, WIDTH - 50); self._y = random.randint(-200, -20)
        self._speed = 3.0 * speed_multiplier; self._size = 20; self._angle = 0
    def update(self, dt, **kwargs):
        self._y += self._speed * kwargs.get("speed_multiplier", 1.0); self._angle += 2
    def get_y(self) -> float: return self._y
    def get_rect(self) -> pygame.Rect: return pygame.Rect(self._x - self._size, self._y - self._size, self._size*2, self._size*2)
    def draw(self, surface):
        if theme_mgr.current_theme == "dark":
            points = [ (self._x, self._y - self._size), (self._x + self._size/2, self._y), (self._x, self._y + self._size), (self._x - self._size/2, self._y) ]
            pygame.draw.polygon(surface, (255, 255, 100), points)
            pygame.draw.circle(surface, (255, 255, 200, 100), (int(self._x), int(self._y)), int(self._size * 0.8))
        else:
            for i in range(5):
                angle_rad = math.radians(self._angle + i * 72)
                px = self._x + math.cos(angle_rad) * (self._size * 0.6); py = self._y + math.sin(angle_rad) * (self._size * 0.6)
                pygame.draw.circle(surface, (255, 180, 180), (int(px), int(py)), int(self._size * 0.5))
            pygame.draw.circle(surface, (255, 220, 100), (int(self._x), int(self._y)), int(self._size * 0.4))

class Star(GameObject):
    def __init__(self, speed_multiplier, game_ref, fixed_x=None, note_name=None):
        self._game = game_ref
        if fixed_x is not None: self._x = fixed_x; self._is_rhythm_note = True
        else: self._x = random.randint(100, WIDTH - 100); self._is_rhythm_note = False
            
        self._y = random.randint(-200, -20); self._z = random.uniform(0.1, 1.0)
        self._base_speed = random.uniform(1.4, 1.6); self._vel = self._base_speed * speed_multiplier
        self._base_size = 5 + self._z * 5; self._points = int(15 - (self._z * 10))
        self._blink_timer = random.uniform(0, 2 * math.pi); self._blink_speed = random.uniform(1.0, 3.0)
        self._trail = []; self._max_trail_length = 15; self._note_name = note_name

        if theme_mgr.current_theme == "light": self._specific_color = random.choice(theme_mgr.light_theme_star_colors); self._base_size = 20
        else: self._specific_color = None

    def get_note_name(self): return self._note_name
    def get_size_category(self) -> str: return 'large' if self._z > 0.7 else ('medium' if self._z > 0.4 else 'small')
    def get_color(self): return self._specific_color if self._specific_color else PASTEL_CREAM
    def set_y(self, y): self._y = y

    def update(self, dt, **kwargs):
        speed_multiplier = kwargs.get("speed_multiplier", 1.0); rhythm_speed = kwargs.get("speed")
        if self._is_rhythm_note and rhythm_speed: self._vel = rhythm_speed * speed_multiplier
        else: self._vel = self._base_speed * speed_multiplier
        
        self._y += self._vel; self._blink_timer += self._blink_speed * dt
        if self._is_rhythm_note:
            self._trail.append((self._x, self._y))
            if len(self._trail) > self._max_trail_length: self._trail.pop(0)

    def get_y(self) -> float: return self._y
    def get_points(self) -> int: return self._points
    def get_pos(self) -> tuple[float, float]: return (self._x, self._y)
    def get_rect(self) -> pygame.Rect: return pygame.Rect(self._x - self._base_size, self._y - self._base_size, self._base_size * 2, self._base_size * 2)

    def draw(self, surface):
        shape = self._game.get_equipped("shape"); p = clamp((math.sin(self._blink_timer) * 0.5 + 0.5), 0, 1)
        current_size = self._base_size * (0.8 + p * 0.4) 
        if theme_mgr.current_theme == "light": base_color = self._specific_color; halo_color = (255, 255, 255); halo_alpha_base = 150 
        else: base_color = (255, 229, 180); halo_color = (255, 255, 204); halo_alpha_base = 100

        if self._is_rhythm_note:
             if len(self._trail) > 1:
                for i, (tx, ty) in enumerate(self._trail):
                    alpha = int(150 * (i / len(self._trail))); t_size = max(1, int(self._base_size * (i / len(self._trail)) * 0.8))
                    s_trail = pygame.Surface((t_size*2, t_size*2), pygame.SRCALPHA)
                    pygame.draw.circle(s_trail, (*base_color, alpha), (t_size, t_size), t_size)
                    surface.blit(s_trail, (tx - t_size, ty - t_size))
             s = pygame.Surface((int(current_size*4), int(current_size*4)), pygame.SRCALPHA)
             pygame.draw.circle(s, (*halo_color, halo_alpha_base), (int(current_size*2), int(current_size*2)), int(current_size*1.6))
             pygame.draw.circle(s, (*base_color, 255), (int(current_size*2), int(current_size*2)), int(current_size))
             surface.blit(s, (self._x - current_size*2, self._y - current_size*2))
        else:
            if shape == "Square": pygame.draw.rect(surface, base_color, pygame.Rect(self._x - current_size, self._y - current_size, current_size*2, current_size*2))
            elif shape == "Triangle": pygame.draw.polygon(surface, base_color, [(self._x, self._y - current_size), (self._x + current_size, self._y + current_size), (self._x - current_size, self._y + current_size)])
            else: 
                s = pygame.Surface((int(current_size*4), int(current_size*4)), pygame.SRCALPHA)
                pygame.draw.circle(s, (*halo_color, int(halo_alpha_base * (0.7 + p * 0.3))), (int(current_size*2), int(current_size*2)), int(current_size*1.6))
                pygame.draw.circle(s, (*base_color, 255), (int(current_size*2), int(current_size*2)), int(current_size))
                surface.blit(s, (self._x - current_size*2, self._y - current_size*2))

# =============================================================================
# DECORATOR PATTERN (Structural)
# Wraps a Star object and adds a golden glow visual effect + bonus points.
# Conforms to the same GameObject interface so callers treat it identically.
# =============================================================================
class GoldenGlow(GameObject):
    """
    @class GoldenGlow
    @brief Decorator that wraps a Star and adds a golden glow effect.
    @details Implements the Decorator (Wrapper) structural pattern.
             Adds visual golden aura and multiplies point value without
             modifying the original Star class.
    """

    GLOW_COLOR = (255, 215, 0)    # gold
    GLOW_ALPHA = 80
    POINT_MULTIPLIER = 3

    def __init__(self, wrapped: Star):
        """
        @param wrapped  The Star instance to decorate.
        """
        self._wrapped = wrapped
        self._pulse_timer = 0.0

    # --- Forward all Star-specific getters to the wrapped object ---
    def get_y(self) -> float:           return self._wrapped.get_y()
    def get_points(self) -> int:        return self._wrapped.get_points() * self.POINT_MULTIPLIER
    def get_pos(self) -> tuple:         return self._wrapped.get_pos()
    def get_rect(self) -> pygame.Rect:  return self._wrapped.get_rect()
    def get_color(self):                return self.GLOW_COLOR
    def get_note_name(self):            return self._wrapped.get_note_name()
    def get_size_category(self) -> str: return self._wrapped.get_size_category()
    def set_y(self, y):                 self._wrapped.set_y(y)

    def update(self, dt, **kwargs):
        self._wrapped.update(dt, **kwargs)
        self._pulse_timer += dt * 4.0   # pulse speed

    def draw(self, surface):
        # 1. Draw the base star first
        self._wrapped.draw(surface)

        # 2. Draw golden halo on top
        x, y = self._wrapped.get_pos()
        rect = self._wrapped.get_rect()
        radius = max(rect.width, rect.height) // 2

        pulse = math.sin(self._pulse_timer) * 0.3 + 1.0   # oscillates 0.7 – 1.3
        glow_radius = int(radius * 2.0 * pulse)

        if glow_radius > 0:
            glow_surf = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(
                glow_surf,
                (*self.GLOW_COLOR, self.GLOW_ALPHA),
                (glow_radius, glow_radius),
                glow_radius
            )
            surface.blit(glow_surf, (x - glow_radius, y - glow_radius))
