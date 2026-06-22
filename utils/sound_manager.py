"""Менеджер звуков и фоновой музыки."""

import pygame
import logging
from typing import Dict

logger = logging.getLogger(__name__)


class SoundManager:
    """Менеджер звуковых эффектов и фоновой музыки.

    Attributes:
        sound_volume: Громкость звуковых эффектов (0.0–1.0).
        music_volume: Громкость музыки (0.0–1.0).
    """

    MUSIC_FILES = [
        "media/music_1.mp3",
        "media/music_2.mp3",
        "media/music_3.mp3",
    ]

    def __init__(
        self,
        sound_volume: float = 0.7,
        music_volume: float = 0.5,
    ) -> None:
        self._sound_volume: float = sound_volume
        self._music_volume: float = music_volume
        self._sounds: Dict[str, pygame.mixer.Sound] = {}
        self._music_enabled: bool = False
        self._current_track_index: int = 0
        if not pygame.mixer.get_init():
            pygame.mixer.init()

        self._load_sounds()

    def _load_sounds(self) -> None:
        """Загружает все звуковые эффекты из папки media."""
        sound_files = {
            "click_error": "media/click-error.wav",
            "close_toolbar": "media/close-toolbar-cound.wav",
            "upgrade": "media/upgrade-sound.wav",
        }
        for key, path in sound_files.items():
            try:
                sound = pygame.mixer.Sound(path)
                sound.set_volume(self._sound_volume)
                self._sounds[key] = sound
                logger.info("Загружен звук: %s -> %s", key, path)
            except pygame.error as exc:
                logger.warning("Не удалось загрузить звук %s: %s", path, exc)

    @property
    def sound_volume(self) -> float:
        """Громкость звуковых эффектов."""
        return self._sound_volume

    @sound_volume.setter
    def sound_volume(self, value: float) -> None:
        """Устанавливает громкость звуковых эффектов."""
        self._sound_volume = max(0.0, min(1.0, value))
        for sound in self._sounds.values():
            sound.set_volume(self._sound_volume)

    @property
    def music_volume(self) -> float:
        """Громкость фоновой музыки."""
        return self._music_volume

    @music_volume.setter
    def music_volume(self, value: float) -> None:
        """Устанавливает громкость фоновой музыки."""
        self._music_volume = max(0.0, min(1.0, value))
        pygame.mixer.music.set_volume(self._music_volume)

    def play_sound(self, name: str) -> None:
        """Воспроизводит звуковой эффект по имени.

        Args:
            name: Ключ звука ('click_error', 'close_toolbar', 'upgrade').
        """
        sound = self._sounds.get(name)
        if sound is not None:
            sound.play()
        else:
            logger.debug("Звук '%s' не загружен", name)

    def play_click_error(self) -> None:
        """Воспроизводит звук ошибки при клике на недоступную кнопку."""
        self.play_sound("click_error")

    def play_close_toolbar(self) -> None:
        """Воспроизводит звук закрытия тулбара."""
        self.play_sound("close_toolbar")

    def play_upgrade(self) -> None:
        """Воспроизводит звук успешного улучшения."""
        self.play_sound("upgrade")

    def start_music(self) -> None:
        """Запускает циклическое воспроизведение фоновой музыки."""
        if not self.MUSIC_FILES:
            logger.warning("Нет файлов для фоновой музыки")
            return

        self._music_enabled = True
        self._current_track_index = 0
        self._play_current_track()

    def stop_music(self) -> None:
        """Останавливает фоновую музыку."""
        self._music_enabled = False
        pygame.mixer.music.stop()

    def _play_current_track(self) -> None:
        """Воспроизводит текущий трек и устанавливает callback на его окончание."""
        if not self._music_enabled:
            return

        track_path = self.MUSIC_FILES[self._current_track_index]
        try:
            pygame.mixer.music.load(track_path)
            pygame.mixer.music.set_volume(self._music_volume)
            pygame.mixer.music.play()
            pygame.mixer.music.set_endevent(pygame.USEREVENT + 2)
            logger.info("Играет трек %d: %s", self._current_track_index + 1, track_path)
        except pygame.error as exc:
            logger.warning("Не удалось воспроизвести трек %s: %s", track_path, exc)

    def next_track(self) -> None:
        """Переключает на следующий трек (вызывается по событию окончания)."""
        if not self._music_enabled:
            return

        self._current_track_index = (self._current_track_index + 1) % len(
            self.MUSIC_FILES
        )
        self._play_current_track()

    def handle_music_event(self, event: pygame.event.Event) -> bool:
        """Обрабатывает событие окончания музыкального трека.

        Args:
            event: Событие pygame.

        Returns:
            True если событие было обработано как конец трека.
        """
        if event.type == pygame.USEREVENT + 2:
            self.next_track()
            return True
        return False
