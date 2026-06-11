from __future__ import annotations

import threading
import time


def _play_tone_sequence(tones: list[tuple[int, int]]) -> None:
    try:
        import winsound

        for index, (frequency, duration_ms) in enumerate(tones):
            winsound.Beep(frequency, duration_ms)
            if index < len(tones) - 1:
                time.sleep(0.03)
    except Exception:
        pass


def _play_async(tones: list[tuple[int, int]]) -> None:
    threading.Thread(
        target=_play_tone_sequence,
        args=(tones,),
        daemon=True,
    ).start()


def play_chest_drop_sound() -> None:
    """Soft ascending tone when a boss chest drop starts the timer."""
    _play_async([(523, 55), (659, 70)])


def play_timer_expired_sound() -> None:
    """Soft descending tone when the countdown reaches zero."""
    _play_async([(440, 90), (349, 110)])
