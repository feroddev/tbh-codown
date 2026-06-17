/** @typedef {{ key: string, label: string, level: number }} BossChestDefinition */

/** @type {BossChestDefinition[]} */
let bossCatalog = [];

/** @type {BossChestDefinition[]} */
let commonCatalog = [];

const ACT_BOSS_KEY_PREFIX = "930";

export async function loadChestCatalog() {
  const [bossResponse, commonResponse] = await Promise.all([
    fetch("./data/boss_chests.json"),
    fetch("./data/common_chests.json"),
  ]);
  if (!bossResponse.ok) {
    throw new Error("Failed to load boss_chests.json");
  }
  if (!commonResponse.ok) {
    throw new Error("Failed to load common_chests.json");
  }
  bossCatalog = await bossResponse.json();
  commonCatalog = await commonResponse.json();
  return bossCatalog;
}

export function loadChestCatalogFromData(data, commonData = []) {
  bossCatalog = data;
  commonCatalog = commonData;
  return bossCatalog;
}

export function getBossCatalog() {
  return bossCatalog;
}

export function getCommonCatalog() {
  return commonCatalog;
}

export function stageBossItemKeys() {
  return new Set(
    bossCatalog
      .filter((item) => !isActBossItemKey(item.key))
      .map((item) => item.key),
  );
}

export function isActBossItemKey(itemKey) {
  return itemKey.startsWith(ACT_BOSS_KEY_PREFIX);
}

export function isStageBossItemKey(itemKey) {
  return stageBossItemKeys().has(itemKey);
}

export function normalBrownItemKeys() {
  return new Set(commonCatalog.map((item) => item.key));
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
  for (const item of [...bossCatalog, ...commonCatalog]) {
    if (item.key === itemKey) {
      return item.label;
    }
  }
  return itemKey;
}

export function commonChestLevelForKey(itemKey) {
  for (const item of commonCatalog) {
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
  return new Set(commonCatalog.map((item) => item.key));
}
