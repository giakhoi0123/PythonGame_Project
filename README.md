# PythonGame_Project
pacman Nova
===========

A fresh Pacman-inspired co-op game built from scratch in Python with Pygame.

Highlights
- Two-player co-op with distinct skill sets
- Upgrades between levels (speed, invisibility, magnet, max HP)
- Smarter ghost AI with coordinated tactics and a boss on harder stages
- Random item drops (health, trap, bomb, shield)
- Procedural audio effects (no external sound assets)
- Particle effects (explosions, trails, shield glow)
- Clean modular code: `main.py`, `player.py`, `enemy.py`, `map.py`, `items.py`, `ui.py`, `audio.py`, `particles.py`, `settings.py`, `utils.py`

Quick Start
1. Create a virtualenv (optional) and install requirements:
   ```bash
   python3 -m venv .venv && source .venv/bin/activate
   pip install -r requirements.txt
2. Run the game:
    ```bash
   python main.py
Controls

Player 1: Arrows to move, Right Shift = Speed Boost, Right Ctrl = Invisibility
Player 2: WASD to move, Space = Magnet Pulse, Left Shift = Dash
Menus: Up/Down or W/S to navigate, Enter to confirm, Esc to go back
Notes

This project is original work, written explicitly for this request.
No external assets are required; audio is synthesized at runtime.

```markdown
requirements.txt
pygame>=2.5.0
numpy>=1.24.0
settings.py
```
"""
Cấu hình và hằng số cho Pacman Nova.
Tách riêng để dễ chỉnh sửa tham số gameplay và UI.
"""
