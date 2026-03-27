import pygame
import random
from config import *
from engine import GameState, Button, Slider, ConfirmationModal, ShopItemButton, loc, theme_mgr, draw_text, ObjectManager, GameObject
from entities import Basket, Currency, Star, Particle
from events import session_caretaker, GameMemento, event_bus, audio

class MenuState(GameState):
    def __init__(self, game):
        super().__init__(game)
        self._btn_start = Button(WIDTH//2 - 100, 250, 200, 60, "START", "normal", game.FONT_MEDIUM)
        self._btn_rhythm = Button(30, 340, 200, 60, "RHYTHM", "normal", game.FONT_MEDIUM)
        self._btn_theme = Button(30, 420, 200, 60, "", "normal", game.FONT_MEDIUM)
        self._btn_shop = Button(270, 340, 200, 60, "SHOP", "normal", game.FONT_MEDIUM)
        self._btn_settings = Button(270, 420, 200, 60, "SETTINGS", "normal", game.FONT_MEDIUM)
        self._btn_quit = Button(WIDTH//2 - 100, 520, 200, 60, "QUIT", "normal", game.FONT_MEDIUM)
        self._buttons = [self._btn_start, self._btn_rhythm, self._btn_shop, self._btn_settings, self._btn_theme, self._btn_quit]
        self._confirm_modal = None; self._update_theme_btn()

    def _update_theme_btn(self): self._btn_theme.set_text_key("LIGHT" if theme_mgr.current_theme == "dark" else "DARK")
    def handle_event(self, event):
        if self._confirm_modal:
            res = self._confirm_modal.handle_event(event)
            if res is True: self._game.stop()
            elif res is False: self._confirm_modal = None
            return
        if self._btn_start.check_click(event): self._game.change_state(PlayingState(self._game))
        elif self._btn_rhythm.check_click(event): self._game.change_state(RhythmSelectionState(self._game))
        elif self._btn_shop.check_click(event): self._game.change_state(ShopState(self._game))
        elif self._btn_settings.check_click(event): self._game.change_state(SettingsState(self._game))
        elif self._btn_theme.check_click(event): theme_mgr.start_transition()
        elif self._btn_quit.check_click(event): self._confirm_modal = ConfirmationModal(self._game)
        self._update_theme_btn()

    def update(self, dt):
        if self._confirm_modal: self._confirm_modal.update(); return
        mouse_pos = pygame.mouse.get_pos()
        for btn in self._buttons: btn.update(dt, mouse_pos=mouse_pos)

    def draw(self, surface):
        draw_text(surface, "Retinal", self._game.FONT_BIG, WIDTH // 2, 150, color=theme_mgr.get("text_color"))
        for btn in self._buttons: btn.draw(surface)
        if self._confirm_modal: self._confirm_modal.draw(surface)

class ShopState(GameState):
    def __init__(self, game):
        super().__init__(game); self._current_tab = "Colors"
        self._btn_back = Button(WIDTH//2 - 100, 720, 200, 50, "BACK", "normal", game.FONT_MEDIUM)
        self._btn_tab_colors = Button(20, 100, 140, 40, "TAB_COLORS", "normal", game.FONT_SMALL)
        self._btn_tab_sizes = Button(180, 100, 140, 40, "TAB_SIZES", "normal", game.FONT_SMALL)
        self._btn_tab_shapes = Button(340, 100, 140, 40, "TAB_SHAPES", "normal", game.FONT_SMALL)
        self._btn_reset = Button(WIDTH//2 - 100, 650, 200, 40, "RESET", "normal", game.FONT_SMALL)
        self._tabs = [self._btn_tab_colors, self._btn_tab_sizes, self._btn_tab_shapes]
        self._create_item_buttons()
        
    def _create_item_buttons(self):
        self._items = []; game = self._game
        if self._current_tab == "Colors":
            for i, (name, price) in enumerate([("Red", 10), ("Orange", 20), ("Yellow", 30), ("Green", 40), ("Cyan", 50), ("Blue", 60), ("Purple", 70), ("Pink", 80)]):
                self._items.append(ShopItemButton(50 if i % 2 == 0 else 260, 180 + (i // 2) * 120, 190, 100, name, price, "color", game))
        elif self._current_tab == "Sizes":
            for i, (name, price, val) in enumerate([("Large", 100, 1), ("Huge", 250, 2), ("Gigantic", 500, 3)]):
                self._items.append(ShopItemButton(100, 180 + i * 120, 300, 100, name, price, "size", game, val=val))
        elif self._current_tab == "Shapes":
            for i, (name, price) in enumerate([("Square", 200), ("Triangle", 300)]):
                self._items.append(ShopItemButton(100, 180 + i * 120, 300, 100, name, price, "shape", game))

    def handle_event(self, event):
        if self._btn_back.check_click(event): self._game.change_state(MenuState(self._game))
        if self._btn_reset.check_click(event): self._game.equip_item("color", "Default"); self._game.equip_item("size", 0); self._game.equip_item("shape", "Star")
        if self._btn_tab_colors.check_click(event): self._current_tab = "Colors"; self._create_item_buttons()
        elif self._btn_tab_sizes.check_click(event): self._current_tab = "Sizes"; self._create_item_buttons()
        elif self._btn_tab_shapes.check_click(event): self._current_tab = "Shapes"; self._create_item_buttons()
        for item in self._items: item.handle_event(event)

    def update(self, dt):
        mouse_pos = pygame.mouse.get_pos(); self._btn_back.update(dt, mouse_pos=mouse_pos); self._btn_reset.update(dt, mouse_pos=mouse_pos)
        for tab in self._tabs: tab.update(dt, mouse_pos=mouse_pos)
        for item in self._items: item.update(dt, mouse_pos=mouse_pos)

    def draw(self, surface):
        txt_col = theme_mgr.get("text_color")
        draw_text(surface, f"{loc.get('SHOP')} - {loc.get(f'TAB_{self._current_tab.upper()}')}", self._game.FONT_MEDIUM, WIDTH // 2, 30, color=txt_col)
        draw_text(surface, f"{loc.get('CURRENCY')} {self._game.get_currency()}", self._game.FONT_SMALL, WIDTH - 100, 30, GOLD)
        self._btn_back.draw(surface); self._btn_reset.draw(surface)
        for tab in self._tabs: tab.draw(surface)
        for item in self._items: item.draw(surface)

class RhythmSelectionState(GameState):
    def __init__(self, game):
        super().__init__(game); self._buttons = []
        for i, song in enumerate(SONG_LIST): self._buttons.append(Button(WIDTH//2 - 150, 250 + i * 80, 300, 60, song["name"], "normal", game.FONT_SMALL))
        self._btn_back = Button(WIDTH//2 - 100, 650, 200, 50, "BACK", "normal", game.FONT_MEDIUM); self._buttons.append(self._btn_back)

    def handle_event(self, event):
        if self._btn_back.check_click(event): self._game.change_state(MenuState(self._game))
        for i, btn in enumerate(self._buttons[:-1]):
            if btn.check_click(event): self._game.change_state(RhythmGameState(self._game, SONG_LIST[i]))

    def update(self, dt):
        mouse_pos = pygame.mouse.get_pos()
        for btn in self._buttons: btn.update(dt, mouse_pos=mouse_pos)

    def draw(self, surface):
        draw_text(surface, loc.get("SELECT_SONG"), self._game.FONT_MEDIUM, WIDTH // 2, 150, color=theme_mgr.get("text_color"))
        for btn in self._buttons: btn.draw(surface)

class SettingsState(GameState):
    def __init__(self, game):
        super().__init__(game); self._current_view = "main"
        self._btn_to_audio = Button(WIDTH//2 - 100, 300, 200, 50, "AUDIO", "normal", game.FONT_MEDIUM)
        self._btn_to_diff = Button(WIDTH//2 - 100, 370, 200, 50, "DIFFICULTY", "normal", game.FONT_MEDIUM)
        self._btn_lang = Button(WIDTH//2 - 100, 440, 200, 50, "LANG", "normal", game.FONT_MEDIUM)
        self._btn_back_main = Button(WIDTH//2 - 100, 600, 200, 50, "BACK", "normal", game.FONT_MEDIUM)
        self._slider_music = Slider(100, 300, 300, 20, 0.0, 1.0, pygame.mixer.music.get_volume(), game.FONT_TINY)
        self._slider_sfx = Slider(100, 400, 300, 20, 0.0, 1.0, game.sfx_volume, game.FONT_TINY)
        self._btn_back_sub = Button(WIDTH//2 - 100, 600, 200, 50, "BACK", "normal", game.FONT_MEDIUM)
        self._btn_easy = Button(WIDTH//2 - 100, 300, 200, 50, "EASY", "normal", game.FONT_SMALL)
        self._btn_medium = Button(WIDTH//2 - 100, 370, 200, 50, "NORMAL", "normal", game.FONT_SMALL)
        self._btn_hard = Button(WIDTH//2 - 100, 440, 200, 50, "HARD", "normal", game.FONT_SMALL)

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
            elif self._btn_lang.check_click(event): loc.toggle_lang(); self._game._load_fonts(); self._btn_lang.set_text_key("LANG")
            elif self._btn_back_main.check_click(event): self._game.change_state(MenuState(self._game))
        elif self._current_view == "audio":
            self._slider_music.handle_event(event); self._slider_sfx.handle_event(event)
            vol = self._slider_music.get_value()
            audio.set_music_volume(vol)          # FACADE — single call updates both facade + pygame
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
            for btn in [self._btn_to_audio, self._btn_to_diff, self._btn_lang, self._btn_back_main]: btn.update(dt, mouse_pos=mouse_pos)
        elif self._current_view == "audio": self._btn_back_sub.update(dt, mouse_pos=mouse_pos)
        elif self._current_view == "difficulty":
            for btn in [self._btn_easy, self._btn_medium, self._btn_hard, self._btn_back_sub]: btn.update(dt, mouse_pos=mouse_pos)

    def draw(self, surface):
        txt_col = theme_mgr.get("text_color")
        if self._current_view == "main":
            draw_text(surface, loc.get("SETTINGS"), self._game.FONT_BIG, WIDTH // 2, 150, color=txt_col)
            self._btn_to_audio.draw(surface); self._btn_to_diff.draw(surface); self._btn_lang.draw(surface); self._btn_back_main.draw(surface)
        elif self._current_view == "audio":
            draw_text(surface, loc.get("AUDIO"), self._game.FONT_MEDIUM, WIDTH // 2, 150, color=txt_col); draw_text(surface, loc.get("MUSIC_VOL"), self._game.FONT_SMALL, WIDTH // 2, 270, color=txt_col)
            self._slider_music.draw(surface); draw_text(surface, loc.get("SFX_VOL"), self._game.FONT_SMALL, WIDTH // 2, 370, color=txt_col); self._slider_sfx.draw(surface)
            self._btn_back_sub.draw(surface)
        elif self._current_view == "difficulty":
            draw_text(surface, loc.get("DIFFICULTY"), self._game.FONT_MEDIUM, WIDTH // 2, 150, color=txt_col)
            self._btn_easy.draw(surface); self._btn_medium.draw(surface); self._btn_hard.draw(surface); self._btn_back_sub.draw(surface)

class GameOverState(GameState):
    def __init__(self, game, score, song_data=None):
        super().__init__(game); self._score = score; self._game.update_high_score(score); self._high_score = self._game.get_high_score()
        self._btn_retry = Button(WIDTH//2 - 100, 400, 200, 50, "RETRY", "normal", game.FONT_MEDIUM)
        self._btn_menu = Button(WIDTH//2 - 100, 470, 200, 50, "MENU", "normal", game.FONT_MEDIUM); self._song_data = song_data
    def handle_event(self, event):
        if self._btn_retry.check_click(event): self._game.change_state(RhythmGameState(self._game, self._song_data) if self._song_data else PlayingState(self._game))
        elif self._btn_menu.check_click(event): self._game.change_state(MenuState(self._game))
    def update(self, dt):
        mouse_pos = pygame.mouse.get_pos(); self._btn_retry.update(dt, mouse_pos=mouse_pos); self._btn_menu.update(dt, mouse_pos=mouse_pos)
    def draw(self, surface):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA); overlay.fill((0, 0, 0, 200)); surface.blit(overlay, (0, 0))
        draw_text(surface, loc.get("GAME_OVER"), self._game.FONT_BIG, WIDTH // 2, 150, RED_ERROR)
        draw_text(surface, f"{loc.get('SCORE')} {self._score}", self._game.FONT_MEDIUM, WIDTH // 2, 250, WHITE)
        draw_text(surface, f"{loc.get('HIGH_SCORE')} {self._high_score}", self._game.FONT_SMALL, WIDTH // 2, 300, (255, 215, 0))
        self._btn_retry.draw(surface); self._btn_menu.draw(surface)

class PausedState(GameState):
    def __init__(self, game, previous_state):
        super().__init__(game); self._previous_state = previous_state; self._font = game.FONT_BIG
        self._btn_resume = Button(WIDTH//2 - 100, HEIGHT//2 - 30, 200, 60, "RESUME", "normal", game.FONT_MEDIUM)
        self._btn_menu = Button(WIDTH//2 - 100, HEIGHT//2 + 50, 200, 60, "MENU", "normal", game.FONT_MEDIUM)
        # MEMENTO PATTERN — snapshot the current session so it can survive a restart
        self._save_memento(previous_state)

    def _save_memento(self, state):
        """Creates and persists a GameMemento from the active game state."""
        try:
            if isinstance(state, PlayingState):
                memento = GameMemento(
                    score=state._score, combo=state._combo,
                    missed=state._missed_stars, elapsed=0.0, mode="endless"
                )
                session_caretaker.save(memento)
            elif isinstance(state, RhythmGameState):
                memento = GameMemento(
                    score=state._score, combo=0,
                    missed=state._missed_notes, elapsed=state._timer,
                    mode="rhythm", song_data=state._song_data
                )
                session_caretaker.save(memento)
        except Exception:
            pass  # saving is best-effort; never crash the game
    def handle_event(self, event):
        if (event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE) or self._btn_resume.check_click(event): pygame.mixer.music.unpause(); self._game.change_state(self._previous_state)
        elif self._btn_menu.check_click(event): audio.set_music_volume(0.5); self._game.change_state(MenuState(self._game))
    def update(self, dt):
        mouse_pos = pygame.mouse.get_pos(); self._btn_resume.update(dt, mouse_pos=mouse_pos); self._btn_menu.update(dt, mouse_pos=mouse_pos)
    def draw(self, surface):
        self._previous_state.draw(surface); overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA); overlay.fill((0, 0, 0, 180)); surface.blit(overlay, (0, 0))
        draw_text(surface, loc.get("PAUSED"), self._font, WIDTH // 2, HEIGHT // 3, WHITE); self._btn_resume.draw(surface); self._btn_menu.draw(surface)

class PlayingState(GameState):
    def __init__(self, game):
        super().__init__(game); self._basket = Basket(game); self._star_manager = ObjectManager[GameObject](); self._particle_manager = ObjectManager[Particle](); self.reset_game()
    def reset_game(self):
        self._score = 0; self._combo = 0; self._missed_stars = 0; self._speed_multiplier = 1.0; self._star_add_counter = 0; self._current_add_rate = self._game.get_settings()["star_rate"]; self._star_manager.clear(); self._particle_manager.clear()
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE: self._game.change_state(PausedState(self._game, self))
    def _spawn_stars(self):
        self._star_add_counter += 1
        if self._star_add_counter >= self._current_add_rate:
            self._star_add_counter = 0
            if random.random() < 0.05: self._star_manager.add(Currency(self._speed_multiplier))
            else:
                for _ in range(3 if self._speed_multiplier > 3.5 else (2 if self._speed_multiplier > 2.0 else 1)): self._star_manager.add(Star(self._speed_multiplier, self._game))
    def _handle_collisions(self):
        basket_rect = self._basket.get_rect()
        for obj in self._star_manager.get_list()[:]:
            if obj.get_y() > HEIGHT:
                self._star_manager.remove(obj)
                if isinstance(obj, Star):
                    self._missed_stars += 1; self._combo = 0; self._score = max(0, self._score - 5)
                    event_bus.notify("miss", {"missed": self._missed_stars, "score": self._score})  # OBSERVER
                    if self._missed_stars >= MAX_MISSED_STARS:
                        self._game.update_high_score(self._score)
                        event_bus.notify("game_over", {"score": self._score, "mode": "endless"})  # OBSERVER
                        self._game.change_state(GameOverState(self._game, self._score)); return
            elif obj.get_rect().colliderect(basket_rect):
                if isinstance(obj, Currency): self._game.add_currency(1); self._game.play_catch_sound()
                elif isinstance(obj, Star):
                    self._game.play_catch_sound(); self._score += obj.get_points() + self._combo; self._combo += 1
                    event_bus.notify("score", {"score": self._score, "combo": self._combo})  # OBSERVER
                    if self._speed_multiplier < 5.0: self._speed_multiplier = min(self._speed_multiplier + 0.03, 5.0)
                    pos = obj.get_pos(); col = obj.get_color()
                    for _ in range(random.randint(8, 12)): self._particle_manager.add(Particle(pos[0], pos[1], col))
                self._star_manager.remove(obj)
    def update(self, dt):
        self._basket.update(dt, keys=pygame.key.get_pressed(), speed_multiplier=self._speed_multiplier); self._spawn_stars(); self._star_manager.update_all(dt, speed_multiplier=self._speed_multiplier); self._handle_collisions()
        for particle in self._particle_manager.get_list()[:]:
            if not particle.update(dt): self._particle_manager.remove(particle)
    def draw(self, surface):
        self._basket.draw(surface); self._star_manager.draw_all(surface); self._particle_manager.draw_all(surface); txt_col = theme_mgr.get("text_color")
        draw_text(surface, f"{loc.get('SCORE')} {self._score}", self._game.FONT_MEDIUM, 60, 20, color=txt_col, align="topleft")
        draw_text(surface, f"{loc.get('COMBO')} x{self._combo}", self._game.FONT_SMALL, 60, 60, color=txt_col, align="topleft")
        draw_text(surface, f"{loc.get('MISSED')} {self._missed_stars}/{MAX_MISSED_STARS}", self._game.FONT_SMALL, 60, 100, color=RED_ERROR, align="topleft")
        draw_text(surface, f"{loc.get('SPEED')} {self._speed_multiplier:.2f}x", self._game.FONT_TINY, WIDTH - 80, 20, color=txt_col, align="topright")
        draw_text(surface, f"{loc.get('PLATFORM')} {self._basket.get_vel():.1f}", self._game.FONT_TINY, WIDTH - 80, 50, color=txt_col, align="topright")

class RhythmGameState(GameState):
    def __init__(self, game, song_data):
        super().__init__(game); self._basket = Basket(game); self._star_manager = ObjectManager[Star](); self._particle_manager = ObjectManager[Particle]()
        self._song_data = song_data; self._bpm = song_data["bpm"]; self._beat_interval = 60.0 / self._bpm
        self._next_beat_time = 0; self._timer = 0.0; self._speed = 5.0; self._score = 0; self._is_playing = True
        self._missed_notes = 0; self._max_missed_notes = 5
        self._note_sequence = game.notes_data.get(song_data.get("note_id"), []); self._current_note_index = 0
        pygame.mixer.music.stop()

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE: self._game.change_state(MenuState(self._game))
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE: pygame.mixer.music.pause(); self._game.change_state(PausedState(self._game, self))

    def update(self, dt):
        self._basket.update(dt, keys=pygame.key.get_pressed(), speed_multiplier=1.2); self._timer += dt
        if self._timer >= self._next_beat_time: self._spawn_rhythm_note(); self._next_beat_time += self._beat_interval * 2
        self._star_manager.update_all(dt, speed_multiplier=1.0, speed=self._speed)
        basket_rect = self._basket.get_rect()
        for star in self._star_manager.get_list()[:]:
            if star.get_y() > HEIGHT:
                self._missed_notes += 1
                self._star_manager.remove(star)
                event_bus.notify("miss", {"missed": self._missed_notes, "mode": "rhythm"})  # OBSERVER
                if self._missed_notes >= self._max_missed_notes:
                    self._game.update_high_score(self._score)
                    event_bus.notify("game_over", {"score": self._score, "mode": "rhythm"})  # OBSERVER
                    self._game.change_state(GameOverState(self._game, self._score, self._song_data)); return
            elif star.get_rect().colliderect(basket_rect):
                if star.get_note_name(): self._game.play_note_sound(star.get_note_name())
                self._score += 10; pos = star.get_pos(); col = star.get_color()
                event_bus.notify("score", {"score": self._score, "mode": "rhythm"})  # OBSERVER
                for _ in range(10): self._particle_manager.add(Particle(pos[0], pos[1], col))
                self._star_manager.remove(star)
        for particle in self._particle_manager.get_list()[:]:
            if not particle.update(dt): self._particle_manager.remove(particle)

    def _spawn_rhythm_note(self):
        note_name = None
        if self._note_sequence: note_name = self._note_sequence[self._current_note_index]; self._current_note_index = (self._current_note_index + 1) % len(self._note_sequence)
        star = Star(self._speed, self._game, fixed_x=int(random.choice(LANE_CENTERS)), note_name=note_name); star.set_y(-50)
        self._star_manager.add(star)

    def draw(self, surface):
        self._basket.draw(surface); self._star_manager.draw_all(surface); self._particle_manager.draw_all(surface)
        draw_text(surface, f"Score: {self._score}", self._game.FONT_MEDIUM, 60, 20, color=theme_mgr.get("text_color"), align="topleft")
        draw_text(surface, f"{loc.get('MISSED')} {self._missed_notes}/{self._max_missed_notes}", self._game.FONT_SMALL, 60, 60, color=RED_ERROR, align="topleft")