# PythonGame_Project
acman Nova
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
