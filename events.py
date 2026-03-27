"""
@file events.py
@brief Design pattern implementations for the Retinal game.
@details Contains: Observer, Command, Template Method, Memento, Facade, Composite, Builder.

Design Pattern Reference
========================
Behavioral : Observer, Command, Template Method, Memento
Structural  : Facade, Composite
Creational  : Builder
"""

import copy
import json
import logging
from abc import ABC, abstractmethod


# =============================================================================
# 1. OBSERVER PATTERN (Behavioral)
# Decouples event producers from consumers.
# Used for: score changes, combo streaks, game-over events.
# =============================================================================
class GameEventListener(ABC):
    """Interface every observer must implement."""
    @abstractmethod
    def on_event(self, event_type: str, data: dict) -> None: ...


class EventManager:
    """
    @class EventManager
    @brief Central pub/sub hub (Observer pattern).
    @details Any object can subscribe to named events.
             Producers call notify(); consumers implement on_event().
    """
    def __init__(self):
        self._listeners: list[GameEventListener] = []

    def subscribe(self, listener: GameEventListener) -> None:
        self._listeners.append(listener)

    def unsubscribe(self, listener: GameEventListener) -> None:
        self._listeners = [l for l in self._listeners if l is not listener]

    def notify(self, event_type: str, data: dict = None) -> None:
        for listener in self._listeners:
            try:
                listener.on_event(event_type, data or {})
            except Exception as exc:
                logging.warning(f"EventManager: listener error — {exc}")


# Convenience singleton used by game states
event_bus = EventManager()


# =============================================================================
# 2. COMMAND PATTERN (Behavioral)
# Encapsulates actions as objects, enabling undo/redo and macro recording.
# Used for: basket movement, score updates, state transitions.
# =============================================================================
class Command(ABC):
    """Abstract command — every concrete command must implement execute/undo."""
    @abstractmethod
    def execute(self) -> None: ...

    def undo(self) -> None:
        """Optional: override to support undo."""
        pass


class MoveBasketCommand(Command):
    """
    @class MoveBasketCommand
    @brief Moves the basket left or right by a fixed step.
    @details Supports undo() so the movement can be reversed.
    """
    def __init__(self, basket, dx: float):
        self._basket = basket
        self._dx = dx

    def execute(self) -> None:
        self._basket._x += self._dx

    def undo(self) -> None:
        self._basket._x -= self._dx


class UpdateScoreCommand(Command):
    """
    @class UpdateScoreCommand
    @brief Adds points to the current score.  Undo subtracts them back.
    """
    def __init__(self, state, points: int):
        self._state = state
        self._points = points

    def execute(self) -> None:
        self._state._score += self._points

    def undo(self) -> None:
        self._state._score -= self._points


class CommandHistory:
    """
    @class CommandHistory
    @brief Maintains an undo stack for Commands (time-machine feature).
    """
    def __init__(self, max_size: int = 100):
        self._stack: list[Command] = []
        self._max = max_size

    def push(self, cmd: Command) -> None:
        cmd.execute()
        self._stack.append(cmd)
        if len(self._stack) > self._max:
            self._stack.pop(0)

    def undo_last(self) -> bool:
        if not self._stack:
            return False
        self._stack.pop().undo()
        return True

    def clear(self) -> None:
        self._stack.clear()


# =============================================================================
# 3. TEMPLATE METHOD PATTERN (Behavioral)
# Defines the skeleton of a game-update cycle; subclasses fill in the steps.
# Used for: PlayingState and RhythmGameState share the same update skeleton.
# =============================================================================
class GameLoopTemplate(ABC):
    """
    @class GameLoopTemplate
    @brief Template Method — fixed update skeleton, variable steps.
    @details Subclasses override spawn(), check_collisions(), on_game_over()
             while the overall sequence is locked in run_one_frame().
    """

    def run_one_frame(self, dt: float, keys) -> None:
        """Invariant sequence every game-mode frame follows."""
        self.handle_input(keys)
        self.spawn(dt)
        self.move_objects(dt)
        self.check_collisions()
        self.update_hud(dt)

    # --- Steps with default (no-op) implementations ---
    def handle_input(self, keys) -> None:  pass
    def update_hud(self, dt: float) -> None: pass

    # --- Steps subclasses MUST override ---
    @abstractmethod
    def spawn(self, dt: float) -> None: ...

    @abstractmethod
    def move_objects(self, dt: float) -> None: ...

    @abstractmethod
    def check_collisions(self) -> None: ...


# =============================================================================
# 4. MEMENTO PATTERN (Behavioral)
# Captures and restores game state without exposing internal structure.
# Used for: saving mid-game progress so the player can resume later.
# =============================================================================
class GameMemento:
    """
    @class GameMemento
    @brief Snapshot of a game session's serialisable state.
    @details Stores score, combo, missed count, and elapsed time.
             Created by the Originator (PlayingState/RhythmGameState)
             and held by the Caretaker (Game).
    """
    def __init__(self, score: int, combo: int, missed: int, elapsed: float,
                 mode: str, song_data: dict | None = None):
        self._score   = score
        self._combo   = combo
        self._missed  = missed
        self._elapsed = elapsed
        self._mode    = mode
        self._song    = copy.deepcopy(song_data)

    # Read-only access — callers must not mutate the snapshot
    @property
    def score(self)   -> int:   return self._score
    @property
    def combo(self)   -> int:   return self._combo
    @property
    def missed(self)  -> int:   return self._missed
    @property
    def elapsed(self) -> float: return self._elapsed
    @property
    def mode(self)    -> str:   return self._mode
    @property
    def song(self)    -> dict | None: return copy.deepcopy(self._song)

    def to_dict(self) -> dict:
        return {"score": self._score, "combo": self._combo,
                "missed": self._missed, "elapsed": self._elapsed,
                "mode": self._mode, "song": self._song}

    @staticmethod
    def from_dict(d: dict) -> "GameMemento":
        return GameMemento(d["score"], d["combo"], d["missed"],
                           d["elapsed"], d["mode"], d.get("song"))


class MementoCaretaker:
    """
    @class MementoCaretaker
    @brief Stores and persists GameMemento objects.
    @details Saves to / loads from a JSON file so progress survives restarts.
    """
    def __init__(self, filepath: str = "session_save.json"):
        self._filepath = filepath
        self._memento: GameMemento | None = None

    def save(self, memento: GameMemento) -> None:
        self._memento = memento
        try:
            with open(self._filepath, "w", encoding="utf-8") as f:
                json.dump(memento.to_dict(), f)
            logging.info("MementoCaretaker: session saved.")
        except OSError as e:
            logging.error(f"MementoCaretaker: could not write save — {e}")

    def restore(self) -> GameMemento | None:
        if self._memento:
            return self._memento
        try:
            with open(self._filepath, "r", encoding="utf-8") as f:
                return GameMemento.from_dict(json.load(f))
        except (OSError, KeyError, json.JSONDecodeError):
            return None

    def clear(self) -> None:
        self._memento = None
        try:
            import os; os.remove(self._filepath)
        except OSError:
            pass


# Global caretaker used by Game class
session_caretaker = MementoCaretaker()


# =============================================================================
# 5. FACADE PATTERN (Structural)
# Single entry-point that hides the complexity of audio subsystem.
# Used for: clean audio API instead of scattered pygame.mixer calls.
# =============================================================================
class AudioFacade:
    """
    @class AudioFacade
    @brief Simplifies access to pygame's audio subsystem.
    @details Clients call play_music() / play_sfx() / set_volume() —
             no knowledge of mixer channels or file formats required.
    """
    def __init__(self):
        self._music_volume = 0.5
        self._sfx_volume   = 0.8
        self._sfx_cache: dict = {}

    def play_music(self, path: str, volume: float | None = None,
                   loops: int = -1) -> None:
        try:
            import pygame
            pygame.mixer.music.load(path)
            pygame.mixer.music.set_volume(
                volume if volume is not None else self._music_volume)
            pygame.mixer.music.play(loops)
        except Exception as e:
            logging.warning(f"AudioFacade.play_music: {e}")

    def stop_music(self) -> None:
        try:
            import pygame; pygame.mixer.music.stop()
        except Exception: pass

    def set_music_volume(self, v: float) -> None:
        self._music_volume = max(0.0, min(1.0, v))
        try:
            import pygame; pygame.mixer.music.set_volume(self._music_volume)
        except Exception: pass

    def play_sfx(self, path: str) -> None:
        try:
            import pygame
            if path not in self._sfx_cache:
                self._sfx_cache[path] = pygame.mixer.Sound(path)
            snd = self._sfx_cache[path]
            snd.set_volume(self._sfx_volume)
            snd.play()
        except Exception as e:
            logging.warning(f"AudioFacade.play_sfx: {e}")

    def set_sfx_volume(self, v: float) -> None:
        self._sfx_volume = max(0.0, min(1.0, v))


audio = AudioFacade()   # module-level singleton


# =============================================================================
# 6. COMPOSITE PATTERN (Structural)
# Treats a group of GameObjects identically to a single object.
# Used for: background layer (waves + stars) updated/drawn as one unit.
# =============================================================================
class SceneNode(ABC):
    """
    @class SceneNode
    @brief Component interface for the Composite pattern.
    """
    @abstractmethod
    def update(self, dt: float, **kwargs) -> None: ...

    @abstractmethod
    def draw(self, surface) -> None: ...


class SceneLeaf(SceneNode):
    """
    @class SceneLeaf
    @brief Wraps a single GameObject as a SceneNode.
    """
    def __init__(self, game_object):
        self._obj = game_object

    def update(self, dt, **kwargs): self._obj.update(dt, **kwargs)
    def draw(self, surface):        self._obj.draw(surface)


class SceneGroup(SceneNode):
    """
    @class SceneGroup
    @brief Composite node — holds child SceneNodes and delegates to all.
    @details Allows treating a group of objects (e.g. entire background layer)
             as a single drawable/updatable unit.
    """
    def __init__(self, name: str = ""):
        self._name     = name
        self._children: list[SceneNode] = []

    def add(self, node: SceneNode) -> "SceneGroup":
        self._children.append(node)
        return self

    def remove(self, node: SceneNode) -> None:
        self._children = [c for c in self._children if c is not node]

    def update(self, dt, **kwargs):
        for child in self._children:
            child.update(dt, **kwargs)

    def draw(self, surface):
        for child in self._children:
            child.draw(surface)

    def __len__(self): return len(self._children)


# =============================================================================
# 7. BUILDER PATTERN (Creational)
# Constructs a SceneGroup step by step from individual parts.
# Used for: assembling the background scene without knowing implementation.
# =============================================================================
class BackgroundSceneBuilder:
    """
    @class BackgroundSceneBuilder
    @brief Builder that assembles a layered background SceneGroup.
    @details Director (Game.__init__) calls add_waves() / add_particles() /
             add_static_stars() then calls build() to obtain the finished
             SceneGroup. No 'new' calls spread across the codebase.
    """
    def __init__(self):
        self._reset()

    def _reset(self):
        self._scene = SceneGroup("background")

    def add_waves(self, wave_objects: list) -> "BackgroundSceneBuilder":
        for w in wave_objects:
            self._scene.add(SceneLeaf(w))
        return self

    def add_particles(self, particle_objects: list) -> "BackgroundSceneBuilder":
        for p in particle_objects:
            self._scene.add(SceneLeaf(p))
        return self

    def add_static_stars(self, star_objects: list) -> "BackgroundSceneBuilder":
        """Adds decorative (non-gameplay) background stars."""
        group = SceneGroup("static_stars")
        for s in star_objects:
            group.add(SceneLeaf(s))
        self._scene.add(group)
        return self

    def build(self) -> SceneGroup:
        result = self._scene
        self._reset()          # builder is ready for reuse
        return result
