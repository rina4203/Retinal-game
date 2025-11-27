# RETINAL’ — Rhythm & Arcade Catcher

**RETINAL’** is a 2D arcade game that blends fast-paced object-catching mechanics with musical rhythm elements. Developed as a capstone project for the **Object-Oriented Programming (2025-2026)** course, it demonstrates advanced software engineering practices including design patterns, unit testing, and localization.

---

## 📖 About the Game

The game immerses players in a dual-atmosphere world (Day/Night) where reflexes and rhythm are key. Players control a basket/paddle at the bottom of the screen to catch falling stars and notes. The goal is to survive as long as possible or complete a song without missing too many beats.

---

## 🎮 Game Modes

### 🎵 Rhythm Mode
* **Concept:** Catch notes synchronized to the beat of a specific music track.
* **Selection:** Players choose from a playlist of songs (defined in `notes.json`).
* **Win/Loss:** The game tracks your combo. Missing **10 notes** results in a "Game Over".

### ♾️ Endless Mode
* **Concept:** A pure test of endurance without a specific melody.
* **Dynamic Difficulty:** The game speed increases progressively as you collect more points.
* **Economy:** Random "Currency" items fall alongside stars, allowing players to earn money for the shop.

---

## ✨ Key Features

* **Visual Themes:** Real-time transition between **Dark (Night)** and **Light (Day)** modes, affecting background assets and particle colors.
* **Internationalization (i18n):** Full support for **English (EN)** and **Ukrainian (UA)** languages, toggleable in settings.
* **In-Game Shop:** A functional economy system allowing players to purchase:
    * Paddle Colors
    * Paddle Sizes
    * Paddle Shapes
* **Persistence:** Uses JSON serialization to save:
    * High Scores
    * Currency Balance
    * Inventory & Equipped Items
* **Settings:** Adjustable Master Volume, SFX Volume, and Difficulty levels.

---

## 🏗️ Technical Architecture

This project strictly adheres to **OOP principles** and implements specific design patterns required by the course curriculum.

### Design Patterns
* **State Pattern:** Manages game screens (`MenuState`, `PlayingState`, `ShopState`, `SettingsState`), allowing for clean transitions and isolated logic.
* **Singleton Pattern:** Used for global managers such as `LocalizationManager` and `ThemeManager` to ensure consistent state across modules.
* **Factory / Object Pool:** Implemented via `ObjectManager` to efficiently handle the lifecycle of falling objects (Stars, Particles).
* **Decorator Pattern:** Used for **Microbenchmarking** (`@measure_time`) to analyze the performance of asset loading.

### Quality Assurance
* **Unit Tests:** A robust suite (`test_reti_full.py`) using `unittest.mock` to simulate Pygame interactions (Headless Testing).
* **Logging:** Integrated `logging` module to track runtime events, errors, and performance metrics in `game_log.log`.
* **Error Handling:** Robust `try-except` blocks for file I/O to prevent crashes if save data is corrupted.

---

## 🚀 Installation & Setup

### Prerequisites
* Python 3.8 or higher
* Pygame library

### Steps

1.  **Clone the Repository:**
    ```bash
    git clone [https://github.com/yourusername/RETINAL.git](https://github.com/yourusername/RETINAL.git)
    cd RETINAL
    ```

2.  **Create a Virtual Environment (Recommended):**
    ```bash
    python -m venv venv
    # Windows:
    venv\Scripts\activate
    # Mac/Linux:
    source venv/bin/activate
    ```

3.  **Install Dependencies:**
    ```bash
    pip install pygame
    ```

4.  **Run the Game:**
    ```bash
    python reti.py
    ```

> **Note:** If `notes.json` is missing, run `python note_editor.py` to generate the default level data.

---

## 🕹️ Controls

| Action | Primary Key | Alternative Key |
| :--- | :---: | :---: |
| **Move Left** | `←` Left Arrow | `A` |
| **Move Right** | `→` Right Arrow | `D` |
| **Pause Game** | `Space` | - |
| **Back / Menu** | `Esc` | - |
| **Interact** | `Left Mouse Button` | - |

---

## 🧪 Unit Testing

The project includes 55+ automated tests covering Logic, Physics, Economy, and Localization.

**To run the tests:**
```bash
python test_reti_full.py
