import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";
import { ChestDetector } from "./chest-detector.js";
import {
  buildWebWatchBossKeys,
  buildWebWatchCommonKeys,
  loadChestCatalogFromData,
} from "./chest-catalog.js";

const root = dirname(fileURLToPath(import.meta.url));
const catalog = JSON.parse(
  readFileSync(join(root, "../data/boss_chests.json"), "utf8"),
);
loadChestCatalogFromData(catalog);

function assert(condition, message) {
  if (!condition) {
    throw new Error(message);
  }
}

function testFreshDropAfterLogReset() {
  const detector = new ChestDetector({
    considerCommonChest: true,
    watchBossKeys: buildWebWatchBossKeys(),
    watchCommonKeys: buildWebWatchCommonKeys(),
    flatCountDropGate: () => true,
  });
  detector.enableCountTracking(true);

  detector.seedLine("GetBoxCount Success Count : 4 // ItemKey : 920501");
  detector.resetState();
  detector.seedLine("GetBoxCount Success Count : 1 // ItemKey : 920501");

  const event = detector.processLine(
    "GetBoxCount Success Count : 1 // ItemKey : 920501",
  );
  assert(event !== null, "expected flat drop after log reset with watch keys");
  assert(event.itemKey === "920501", "unexpected item key");
}

function testCountIncreaseWhenSeeded() {
  const detector = new ChestDetector({
    considerCommonChest: true,
    watchBossKeys: buildWebWatchBossKeys(),
    watchCommonKeys: buildWebWatchCommonKeys(),
  });
  detector.enableCountTracking(true);
  detector.seedLine("GetBoxCount Success Count : 2 // ItemKey : 920501");

  const event = detector.processLine(
    "GetBoxCount Success Count : 3 // ItemKey : 920501",
  );
  assert(event !== null, "expected count increase drop");
}

function testFirstSeenDropWithoutSeed() {
  const detector = new ChestDetector({
    considerCommonChest: true,
    watchBossKeys: buildWebWatchBossKeys(),
    watchCommonKeys: buildWebWatchCommonKeys(),
    flatCountDropGate: () => true,
  });
  detector.enableCountTracking(true);

  const event = detector.processLine(
    "GetBoxCount Success Count : 1 // ItemKey : 920501",
  );
  assert(event !== null, "expected first drop without prior seed");
}

testFreshDropAfterLogReset();
testCountIncreaseWhenSeeded();
testFirstSeenDropWithoutSeed();
console.log("detector tests passed");
