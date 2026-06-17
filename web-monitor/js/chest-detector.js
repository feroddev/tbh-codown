import { classifyChestItemKey } from "./chest-catalog.js";

export const GET_BOX_COUNT_PATTERN =
  /GetBoxCount Success Count\s*:\s*(\d+)\s*\/\/\s*ItemKey\s*:\s*(\d+)/;

const INVENTORY_BURST_MIN_KEYS = 3;

/**
 * @typedef {{ itemKey: string, chestType: "boss" | "actBoss" | "common", count: number, rawLine: string, countIncreased: boolean }} ChestEvent
 */

export function isInventorySyncBurst(events) {
  if (events.length < INVENTORY_BURST_MIN_KEYS) {
    return false;
  }
  const keyCounts = new Map();
  for (const event of events) {
    keyCounts.set(event.itemKey, (keyCounts.get(event.itemKey) ?? 0) + 1);
  }
  if (keyCounts.size < INVENTORY_BURST_MIN_KEYS) {
    return false;
  }
  return [...keyCounts.values()].every((count) => count === 1);
}

export function filterInventorySyncBurst(events, preserveItemKeys = new Set()) {
  if (!isInventorySyncBurst(events)) {
    return events;
  }
  const keyCounts = new Map();
  for (const event of events) {
    keyCounts.set(event.itemKey, (keyCounts.get(event.itemKey) ?? 0) + 1);
  }
  return events.filter(
    (event) =>
      event.countIncreased ||
      (keyCounts.get(event.itemKey) ?? 0) > 1 ||
      preserveItemKeys.has(event.itemKey),
  );
}

export class ChestDetector {
  /**
   * @param {{
   *   considerCommonChest?: boolean,
   *   watchBossKeys?: Set<string>,
   *   watchCommonKeys?: Set<string>,
   *   flatCountDropGate?: (itemKey: string) => boolean,
   * }} options
   */
  constructor({
    considerCommonChest = true,
    watchBossKeys = new Set(),
    watchCommonKeys = new Set(),
    flatCountDropGate = null,
  } = {}) {
    this.considerCommonChest = considerCommonChest;
    this.watchBossKeys = watchBossKeys;
    this.watchCommonKeys = watchCommonKeys;
    this.flatCountDropGate = flatCountDropGate;
    this.useCountTracking = false;
    /** @type {Record<string, number>} */
    this.lastCounts = {};
    /** @type {Record<string, number>} */
    this.lastEmittedCount = {};
  }

  enableCountTracking(enabled) {
    this.useCountTracking = enabled;
  }

  setConsiderCommonChest(enabled) {
    this.considerCommonChest = enabled;
  }

  setWatchBossKeys(keys) {
    this.watchBossKeys = keys;
  }

  setWatchCommonKeys(keys) {
    this.watchCommonKeys = keys;
  }

  setFlatCountDropGate(gate) {
    this.flatCountDropGate = gate;
  }

  resetState() {
    this.lastCounts = {};
    this.lastEmittedCount = {};
  }

  seedLine(line) {
    const match = GET_BOX_COUNT_PATTERN.exec(line);
    if (!match) {
      return;
    }
    const count = Number(match[1]);
    const itemKey = match[2];
    const chestType = classifyChestItemKey(itemKey, {
      considerCommonChest: this.considerCommonChest,
    });
    if (!chestType) {
      return;
    }
    this.lastCounts[itemKey] = count;
  }

  /**
   * @param {string} line
   * @returns {ChestEvent | null}
   */
  processLine(line) {
    const match = GET_BOX_COUNT_PATTERN.exec(line);
    if (!match) {
      return null;
    }

    const count = Number(match[1]);
    const itemKey = match[2];
    const chestType = classifyChestItemKey(itemKey, {
      considerCommonChest: this.considerCommonChest,
    });
    if (!chestType) {
      return null;
    }

    let countIncreased = false;

    if (this.useCountTracking) {
      const hadKnownCount = Object.prototype.hasOwnProperty.call(
        this.lastCounts,
        itemKey,
      );
      let previousCount = this.lastCounts[itemKey];
      this.lastCounts[itemKey] = count;

      if (previousCount === undefined) {
        if (count > 0 && this.isWatchedItemKey(itemKey)) {
          previousCount = 0;
        } else {
          return null;
        }
      }

      countIncreased = hadKnownCount && count > previousCount;

      if (count <= previousCount) {
        if (!this.shouldAcceptFlatCountDrop(itemKey)) {
          return null;
        }
        const lastEmitted = this.lastEmittedCount[itemKey];
        if (lastEmitted !== undefined && count <= lastEmitted) {
          return null;
        }
      }
    }

    this.lastEmittedCount[itemKey] = count;

    return {
      itemKey,
      chestType,
      count,
      rawLine: line.trim(),
      countIncreased,
    };
  }

  isWatchedItemKey(itemKey) {
    if (this.watchBossKeys.has(itemKey)) {
      return true;
    }
    return this.considerCommonChest && this.watchCommonKeys.has(itemKey);
  }

  shouldAcceptFlatCountDrop(itemKey) {
    if (!this.flatCountDropGate) {
      return false;
    }
    if (!this.isWatchedItemKey(itemKey)) {
      return false;
    }
    return this.flatCountDropGate(itemKey);
  }
}
