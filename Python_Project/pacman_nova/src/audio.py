"""
Audio tổng hợp bằng numpy: không cần asset âm thanh ngoài.
Tạo các hiệu ứng đơn giản: ăn điểm, power, trúng đòn, nổ, menu.
"""

import numpy as np
import pygame

SAMPLE_RATE = 44100


def _tone(freq: float, length: float, volume: float = 0.5, wave: str = "sine"):
    t = np.linspace(0, length, int(SAMPLE_RATE * length), False)
    if wave == "sine":
        y = np.sin(2 * np.pi * freq * t)
    elif wave == "square":
        y = np.sign(np.sin(2 * np.pi * freq * t))
    elif wave == "saw":
        y = 2.0 * (t * freq - np.floor(0.5 + t * freq))
    else:
        y = np.sin(2 * np.pi * freq * t)
    y = y * volume
    return (y * 32767).astype(np.int16)


def _envelope(samples: np.ndarray, attack: float = 0.01, release: float = 0.05):
    n = samples.shape[0]
    att = int(SAMPLE_RATE * attack)
    rel = int(SAMPLE_RATE * release)
    env = np.ones(n)
    if att > 0:
        env[:att] = np.linspace(0, 1, att)
    if rel > 0:
        env[-rel:] = np.linspace(1, 0, rel)
    out = samples.astype(np.float32) * env
    return out.astype(np.int16)


class SoundManager:
    def __init__(self, volume: float = 0.6):
        self.volume = volume
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.pre_init(SAMPLE_RATE, -16, 1, 512)
                pygame.mixer.init()
        except Exception:
            # Một số môi trường không hỗ trợ mixer (headless). Game vẫn chạy.
            pass

        self.cache = {}

    def _play(self, key: str, arr: np.ndarray):
        try:
            snd = self.cache.get(key)
            if snd is None:
                snd = pygame.sndarray.make_sound(arr.copy())
                snd.set_volume(self.volume)
                self.cache[key] = snd
            snd.play()
        except Exception:
            pass

    def eat(self):
        s = _tone(880, 0.06, 0.4, "sine")
        s = _envelope(s, 0.002, 0.03)
        self._play("eat", s)

    def power(self):
        s1 = _tone(300, 0.12, 0.35, "saw")
        s2 = _tone(600, 0.12, 0.25, "saw")
        s = _envelope((s1 * 0.6 + s2 * 0.4).astype(np.int16), 0.005, 0.07)
        self._play("power", s)

    def hit(self):
        noise = (np.random.rand(int(SAMPLE_RATE * 0.15)) * 2 - 1) * 0.6
        s = _envelope((noise * 32767).astype(np.int16), 0.001, 0.1)
        self._play("hit", s)

    def explosion(self):
        noise = (np.random.rand(int(SAMPLE_RATE * 0.3)) * 2 - 1)
        filt = np.convolve(noise, np.ones(200) / 200, mode="same")
        s = _envelope((filt * 0.7 * 32767).astype(np.int16), 0.005, 0.2)
        self._play("boom", s)

    def menu(self):
        s = _envelope(_tone(520, 0.08, 0.35, "square"), 0.001, 0.04)
        self._play("menu", s)