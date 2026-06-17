import { classifyChestItemKey } from "./chest-catalog.js";

/**
 * Each new physical GetBoxCount line is a drop candidate. Deduplication uses
 * line number + item key only (same approach as the community tracker).
 */
export const DROP_LINE_PATTERN =
  /GetBoxCount Success Count\s*:\s*(\d+)\s*\/\/\s*ItemKey\s*:\s*(\d+)/i;

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
 * @param {string} line
 * @returns {{ count: number, itemKey: string } | null}
 */
export function parseDropLine(line) {
  const match = DROP_LINE_PATTERN.exec(line);
  if (!match) {
    return null;
  }
  return {
    count: Number(match[1]),
    itemKey: match[2],
  };
}

/**
 * @param {string} content
 * @returns {Set<string>}
 */
export function collectLineSignatures(content) {
  const lines = content.split(/\r?\n/);
  const signatures = new Set();
  for (let index = 0; index < lines.length; index += 1) {
    const parsed = parseDropLine(lines[index]);
    if (!parsed) {
      continue;
    }
    signatures.add(lineSignature(index + 1, parsed.itemKey));
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
   * Mark every existing GetBoxCount line as already seen (fresh session baseline).
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
      const parsed = parseDropLine(line);
      if (!parsed) {
        continue;
      }

      const { count, itemKey } = parsed;
      const signature = lineSignature(index + 1, itemKey);
      if (this.seenSignatures.has(signature)) {
        continue;
      }

      this.seenSignatures.add(signature);

      const chestType = classifyChestItemKey(itemKey, {
        considerCommonChest: this.considerCommonChest,
      });
      if (!chestType) {
        continue;
      }

      events.push({
        itemKey,
        chestType,
        count,
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
