import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";
import {
  LineDropDetector,
  collectLineSignatures,
  lineSignature,
} from "./line-drop-detector.js";
import { loadChestCatalogFromData } from "./chest-catalog.js";

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

function testSeedIgnoresExistingLines() {
  const detector = new LineDropDetector({ considerCommonChest: true });
  const content = [
    "noise",
    "GetBoxCount Success Count : 1 // ItemKey : 920501",
    "GetBoxCount Success Count : 1 // ItemKey : 920401",
  ].join("\n");
  detector.seedFromContent(content);

  const result = detector.processContent(
    `${content}\nGetBoxCount Success Count : 1 // ItemKey : 920301`,
  );
  assert(result.events.length === 1, "expected only the new log line");
  assert(result.events[0].itemKey === "920301", "unexpected item key");
}

function testInventoryBurstAtConnectIsIgnored() {
  const detector = new LineDropDetector({ considerCommonChest: true });
  const burst = [
    "GetBoxCount Success Count : 1 // ItemKey : 920301",
    "GetBoxCount Success Count : 1 // ItemKey : 920401",
    "GetBoxCount Success Count : 1 // ItemKey : 920501",
  ].join("\n");
  detector.seedFromContent(burst);

  const result = detector.processContent(burst);
  assert(result.events.length === 0, "seeded burst must not emit events");
}

function testLogTruncationReseedsSignatures() {
  const detector = new LineDropDetector({ considerCommonChest: true });
  const original = [
    "GetBoxCount Success Count : 1 // ItemKey : 920501",
    "GetBoxCount Success Count : 1 // ItemKey : 920401",
  ].join("\n");
  detector.seedFromContent(original);
  detector.processContent(original);

  const rotated = "GetBoxCount Success Count : 1 // ItemKey : 920301";
  const truncateResult = detector.processContent(rotated);
  assert(truncateResult.truncated, "expected truncated log detection");
  assert(
    truncateResult.events.length === 0,
    "truncation reseed must not replay existing lines",
  );

  const appended = `${rotated}\nGetBoxCount Success Count : 1 // ItemKey : 920501`;
  const dropResult = detector.processContent(appended);
  assert(dropResult.events.length === 1, "expected one event after append");
  assert(dropResult.events[0].itemKey === "920501", "unexpected item key");
}

function testLineSignatureFormat() {
  assert(
    lineSignature(42, "920501") === "42:920501",
    "unexpected signature format",
  );
  const signatures = collectLineSignatures(
    "x\nGetBoxCount Success Count : 1 // ItemKey : 920501",
  );
  assert(signatures.has("2:920501"), "expected 1-based line signature");
}

function testSecondChestWithCountTwo() {
  const detector = new LineDropDetector({ considerCommonChest: true });
  const baseline = "GetBoxCount Success Count : 1 // ItemKey : 920501";
  detector.seedFromContent(baseline);
  detector.processContent(baseline);

  const result = detector.processContent(
    `${baseline}\nGetBoxCount Success Count : 2 // ItemKey : 920501`,
  );
  assert(result.events.length === 1, "expected second chest when count rises to 2");
  assert(result.events[0].itemKey === "920501", "unexpected item key");
  assert(result.events[0].count === 2, "expected count 2 on event");
}

function testFlatResyncLineIsIgnored() {
  const detector = new LineDropDetector({ considerCommonChest: true });
  const baseline = "GetBoxCount Success Count : 1 // ItemKey : 920501";
  detector.seedFromContent(baseline);
  detector.processContent(baseline);

  const result = detector.processContent(
    `${baseline}\nGetBoxCount Success Count : 1 // ItemKey : 920501`,
  );
  assert(result.events.length === 0, "flat count line must not emit another drop");
}

testSeedIgnoresExistingLines();
testInventoryBurstAtConnectIsIgnored();
testLogTruncationReseedsSignatures();
testLineSignatureFormat();
testSecondChestWithCountTwo();
testFlatResyncLineIsIgnored();
console.log("line-drop tests passed");
