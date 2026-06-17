import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";
import { ChestDetector, filterInventorySyncBurst } from "./chest-detector.js";
import {
  buildWebWatchBossKeys,
  buildWebWatchCommonKeys,
  loadChestCatalogFromData,
} from "./chest-catalog.js";

const root = dirname(fileURLToPath(import.meta.url));
const catalog = JSON.parse(
  readFileSync(join(root, "../data/boss_chests.json"), "utf8"),
);
const commonCatalog = JSON.parse(
  readFileSync(join(root, "../data/common_chests.json"), "utf8"),
);
loadChestCatalogFromData(catalog, commonCatalog);

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

function testPollBatchCollectsEvents() {
  const detector = new ChestDetector({
    considerCommonChest: true,
    watchBossKeys: buildWebWatchBossKeys(),
    watchCommonKeys: buildWebWatchCommonKeys(),
    flatCountDropGate: () => true,
  });
  detector.enableCountTracking(true);
  detector.seedLine("GetBoxCount Success Count : 2 // ItemKey : 920501");

  const batchEvents = [];
  const event = detector.processLine(
    "GetBoxCount Success Count : 3 // ItemKey : 920501",
  );
  if (event) {
    batchEvents.push(event);
  }
  const filtered = filterInventorySyncBurst(batchEvents);
  assert(filtered.length === 1, "expected one event in poll batch");
}

function testActBossLv70Drop() {
  const detector = new ChestDetector({
    considerCommonChest: true,
    watchBossKeys: buildWebWatchBossKeys(),
    watchCommonKeys: buildWebWatchCommonKeys(),
    flatCountDropGate: () => true,
  });
  detector.enableCountTracking(true);

  const event = detector.processLine(
    "GetBoxCount Success Count : 1 // ItemKey : 930701",
  );
  assert(event !== null, "expected act boss Lv70 drop");
  assert(event.chestType === "actBoss", "expected actBoss chest type");
  assert(event.itemKey === "930701", "unexpected act boss item key");
}

testFreshDropAfterLogReset();
testCountIncreaseWhenSeeded();
testFirstSeenDropWithoutSeed();
testPollBatchCollectsEvents();
testActBossLv70Drop();
testInventoryBurstPreservesCountIncrease();
console.log("detector tests passed");

function testInventoryBurstPreservesCountIncrease() {
  const detector = new ChestDetector({
    considerCommonChest: true,
    watchBossKeys: buildWebWatchBossKeys(),
    watchCommonKeys: buildWebWatchCommonKeys(),
    flatCountDropGate: () => true,
  });
  detector.enableCountTracking(true);
  detector.seedLine("GetBoxCount Success Count : 2 // ItemKey : 910501");
  detector.seedLine("GetBoxCount Success Count : 1 // ItemKey : 920301");
  detector.seedLine("GetBoxCount Success Count : 1 // ItemKey : 920401");

  const batchEvents = [];
  for (const line of [
    "GetBoxCount Success Count : 3 // ItemKey : 910501",
    "GetBoxCount Success Count : 1 // ItemKey : 920301",
    "GetBoxCount Success Count : 1 // ItemKey : 920401",
    "GetBoxCount Success Count : 1 // ItemKey : 920501",
  ]) {
    const event = detector.processLine(line);
    if (event) {
      batchEvents.push(event);
    }
  }

  const filtered = filterInventorySyncBurst(batchEvents);
  assert(filtered.length === 1, "expected real increment to survive inventory burst");
  assert(filtered[0].itemKey === "910501", "unexpected preserved item key");
  assert(filtered[0].countIncreased, "expected countIncreased flag");
}
