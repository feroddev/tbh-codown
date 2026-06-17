import { classifyChestItemKey } from "./chest-catalog.js";

/**
 * Matches the working community tracker: only Count : 1 lines are treated as drops.
 * New physical log lines are deduplicated by line number + item key.
 */
export const DROP_LINE_PATTERN =
  /GetBoxCount Success Count\s*:\s*1\s*\/\/\s*ItemKey\s*:\s*(\d+)/i;

/**
 * @typedef {{
 *   itemKey: string,
 *   chestType: "boss" | "actBoss" | "common",
 *   count: number,
 *   rawLine: string,
 *   lineNumber: number,
 *   signature: string,
 *   detectedAt: number,
 * }} LineDropEvent
 */

export function lineSignature(lineNumber, itemKey) {
  return `${lineNumber}:${itemKey}`;
}

/**
 * @param {string} content
 * @returns {Set<string>}
 */
export function collectLineSignatures(content) {
  const lines = content.split(/\r?\n/);
  const signatures = new Set();
  for (let index = 0; index < lines.length; index += 1) {
    const match = DROP_LINE_PATTERN.exec(lines[index]);
    if (!match) {
      continue;
    }
    signatures.add(lineSignature(index + 1, match[1]));
  }
  return signatures;
}

export class LineDropDetector {
  /**
   * @param {{ considerCommonChest?: boolean }} options
   */
  constructor({ considerCommonChest = true } = {}) {
    this.considerCommonChest = considerCommonChest;
    /** @type {Set<string>} */
    this.seenSignatures = new Set();
    this.lastContentLength = 0;
  }

  setConsiderCommonChest(enabled) {
    this.considerCommonChest = enabled;
  }

  resetState() {
    this.seenSignatures = new Set();
    this.lastContentLength = 0;
  }

  /**
   * Mark every existing Count : 1 line as already seen (fresh session baseline).
   * @param {string} content
   */
  seedFromContent(content) {
    this.seenSignatures = collectLineSignatures(content);
    this.lastContentLength = content.length;
  }

  /**
   * @param {string} content
   * @param {{ detectedAt?: number }} options
   * @returns {{ events: LineDropEvent[], truncated: boolean }}
   */
  processContent(content, { detectedAt = Date.now() } = {}) {
    const truncated =
      this.lastContentLength > 0 && content.length < this.lastContentLength;
    if (truncated) {
      this.seenSignatures = collectLineSignatures(content);
    }

    const lines = content.split(/\r?\n/);
    /** @type {LineDropEvent[]} */
    const events = [];

    for (let index = 0; index < lines.length; index += 1) {
      const line = lines[index];
      const match = DROP_LINE_PATTERN.exec(line);
      if (!match) {
        continue;
      }

      const itemKey = match[1];
      const signature = lineSignature(index + 1, itemKey);
      if (this.seenSignatures.has(signature)) {
        continue;
      }

      const chestType = classifyChestItemKey(itemKey, {
        considerCommonChest: this.considerCommonChest,
      });
      if (!chestType) {
        this.seenSignatures.add(signature);
        continue;
      }

      this.seenSignatures.add(signature);
      events.push({
        itemKey,
        chestType,
        count: 1,
        rawLine: line.trim(),
        lineNumber: index + 1,
        signature,
        detectedAt,
      });
    }

    this.lastContentLength = content.length;
    return { events, truncated };
  }
}
