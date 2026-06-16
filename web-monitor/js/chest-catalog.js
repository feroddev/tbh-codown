/** @typedef {{ key: string, label: string, level: number }} BossChestDefinition */

/** @type {BossChestDefinition[]} */
let bossCatalog = [];

/** @type {BossChestDefinition[]} */
const NORMAL_CHEST_CATALOG = [
  { key: "910301", label: "Normal Monster Box Lv1", level: 1 },
  { key: "910351", label: "Normal Monster Box Lv2", level: 2 },
  { key: "920301", label: "Normal Monster Box Lv1", level: 1 },
  { key: "920351", label: "Normal Monster Box Lv2", level: 2 },
  { key: "920371", label: "Normal Monster Box Lv3", level: 3 },
  { key: "920381", label: "Normal Monster Box Lv4", level: 4 },
  { key: "920391", label: "Normal Monster Box Lv5", level: 5 },
];

const ACT_BOSS_KEY_PREFIX = "930";

export async function loadChestCatalog() {
  const response = await fetch("./data/boss_chests.json");
  if (!response.ok) {
    throw new Error("Failed to load boss_chests.json");
  }
  bossCatalog = await response.json();
  return bossCatalog;
}

export function loadChestCatalogFromData(data) {
  bossCatalog = data;
  return bossCatalog;
}

export function getBossCatalog() {
  return bossCatalog;
}

export function stageBossItemKeys() {
  return new Set(bossCatalog.map((item) => item.key));
}

export function isActBossItemKey(itemKey) {
  return itemKey.startsWith(ACT_BOSS_KEY_PREFIX);
}

export function isStageBossItemKey(itemKey) {
  return stageBossItemKeys().has(itemKey) && !isActBossItemKey(itemKey);
}

export function normalBrownItemKeys() {
  const bossKeys = stageBossItemKeys();
  return new Set(
    NORMAL_CHEST_CATALOG.filter((item) => !bossKeys.has(item.key)).map(
      (item) => item.key,
    ),
  );
}

export function isCommonChestItemKey(itemKey) {
  if (isStageBossItemKey(itemKey) || isActBossItemKey(itemKey)) {
    return false;
  }
  return normalBrownItemKeys().has(itemKey) || itemKey.startsWith("910");
}

/**
 * @returns {"boss" | "actBoss" | "common" | null}
 */
export function classifyChestItemKey(itemKey, { considerCommonChest = true } = {}) {
  if (isActBossItemKey(itemKey)) {
    return "actBoss";
  }
  if (isStageBossItemKey(itemKey)) {
    return "boss";
  }
  if (considerCommonChest && isCommonChestItemKey(itemKey)) {
    return "common";
  }
  return null;
}

export function bossChestLevelForKey(itemKey) {
  const match = bossCatalog.find((item) => item.key === itemKey);
  return match?.level ?? null;
}

export function catalogLabelForKey(itemKey) {
  for (const item of [...bossCatalog, ...NORMAL_CHEST_CATALOG]) {
    if (item.key === itemKey) {
      return item.label;
    }
  }
  return itemKey;
}

export function commonChestLevelForKey(itemKey) {
  for (const item of NORMAL_CHEST_CATALOG) {
    if (item.key === itemKey) {
      return item.level;
    }
  }
  if (itemKey.startsWith("910") && itemKey.length >= 6) {
    const bossLevel = bossChestLevelForKey(`92${itemKey.slice(2)}`);
    if (bossLevel !== null) {
      return bossLevel;
    }
  }
  return null;
}

export function commonChestTimerKey(chestLevel) {
  return -Math.abs(chestLevel);
}

export function buildWebWatchBossKeys() {
  return new Set(bossCatalog.map((item) => item.key));
}

export function buildWebWatchCommonKeys() {
  const keys = new Set(NORMAL_CHEST_CATALOG.map((item) => item.key));
  for (const item of bossCatalog) {
    if (item.key.startsWith("92") && item.key.length >= 6) {
      keys.add(`91${item.key.slice(2)}`);
    }
  }
  return keys;
}
