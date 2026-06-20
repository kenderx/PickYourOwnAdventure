"""
audio_manager.py
Wraps pygame.mixer to provide background music and sound-effect playback.
Degrades gracefully if pygame is unavailable or audio initialisation fails.
"""
from __future__ import annotations

import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)


class AudioManager:
    """
    High-level audio interface used by the game.

    Music:
        play_music(path)  — start looping music, crossfading from previous track
        stop_music()      — fade out current music
        pause_music() / resume_music() — useful when pausing the game

    SFX:
        play_sfx(path)    — fire-and-forget sound effect (cached)

    Volume:
        music_volume / sfx_volume properties (0.0 – 1.0)
    """

    def __init__(self) -> None:
        self._available = False
        self._current_music: Optional[str] = None
        self._music_volume: float = 0.7
        self._sfx_volume: float = 1.0
        self._sfx_cache: dict[str, Any] = {}   # path → pygame.Sound

        try:
            import pygame
            pygame.mixer.pre_init(44100, -16, 2, 2048)
            pygame.mixer.init()
            self._pygame = pygame
            self._available = True
            logger.info("Audio system initialised (pygame).")
        except Exception as exc:
            logger.warning("Audio unavailable: %s", exc)

    # ------------------------------------------------------------------
    # Volume properties
    # ------------------------------------------------------------------

    @property
    def music_volume(self) -> float:
        return self._music_volume

    @music_volume.setter
    def music_volume(self, value: float) -> None:
        self._music_volume = max(0.0, min(1.0, float(value)))
        if self._available:
            self._pygame.mixer.music.set_volume(self._music_volume)

    @property
    def sfx_volume(self) -> float:
        return self._sfx_volume

    @sfx_volume.setter
    def sfx_volume(self, value: float) -> None:
        self._sfx_volume = max(0.0, min(1.0, float(value)))
        # Update already-cached sounds so next play() uses the new volume.
        for sound in self._sfx_cache.values():
            sound.set_volume(self._sfx_volume)

    # ------------------------------------------------------------------
    # Music
    # ------------------------------------------------------------------

    def play_music(
        self,
        path: str,
        loop: bool = True,
        fade_ms: int = 1500,
    ) -> None:
        """
        Start playing *path* as background music.
        If the same file is already playing, does nothing.
        Crossfades from the previous track using *fade_ms* milliseconds.
        """
        if not self._available:
            return
        if not path or not os.path.isfile(path):
            logger.debug("Music file not found, skipping: %s", path)
            return
        if path == self._current_music:
            return   # already playing

        try:
            self._pygame.mixer.music.fadeout(fade_ms // 2)
            self._pygame.mixer.music.load(path)
            self._pygame.mixer.music.set_volume(self._music_volume)
            self._pygame.mixer.music.play(-1 if loop else 0, fade_ms=fade_ms // 2)
            self._current_music = path
        except Exception as exc:
            logger.warning("Failed to play music '%s': %s", path, exc)

    def stop_music(self, fade_ms: int = 800) -> None:
        """Fade out and stop current music."""
        if self._available:
            self._pygame.mixer.music.fadeout(fade_ms)
        self._current_music = None

    def pause_music(self) -> None:
        if self._available:
            self._pygame.mixer.music.pause()

    def resume_music(self) -> None:
        if self._available:
            self._pygame.mixer.music.unpause()

    # ------------------------------------------------------------------
    # Sound effects
    # ------------------------------------------------------------------

    def play_sfx(self, path: str) -> None:
        """Play a sound effect once. Results are cached for performance."""
        if not self._available:
            return
        if not path or not os.path.isfile(path):
            logger.debug("SFX file not found, skipping: %s", path)
            return
        try:
            if path not in self._sfx_cache:
                sound = self._pygame.mixer.Sound(path)
                sound.set_volume(self._sfx_volume)
                self._sfx_cache[path] = sound
            self._sfx_cache[path].play()
        except Exception as exc:
            logger.warning("Failed to play SFX '%s': %s", path, exc)

    # ------------------------------------------------------------------
    # Cleanup
    # ------------------------------------------------------------------

    def cleanup(self) -> None:
        """Shut down the mixer. Call when the application closes."""
        if self._available:
            try:
                self._pygame.mixer.quit()
            except Exception:
                pass
