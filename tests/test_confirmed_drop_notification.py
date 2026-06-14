from __future__ import annotations

import unittest

from src.domain.chest_event import ChestEvent, ChestType
from src.domain.confirmed_drop_notification import ConfirmedDropNotification


class ConfirmedDropNotificationTests(unittest.TestCase):
    def test_notification_carries_resolved_chest_level(self) -> None:
        event = ChestEvent(
            item_key="920651",
            chest_type=ChestType.BOSS,
            count=2,
            raw_line="",
        )
        notification = ConfirmedDropNotification(
            event=event,
            stage_key=3205,
            chest_level=65,
            log_message="12:00:00 · Boss Chest Lv65",
        )

        self.assertEqual(notification.chest_level, 65)
        self.assertEqual(notification.event.item_key, "920651")


if __name__ == "__main__":
    unittest.main()
