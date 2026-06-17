import { ChestDetector, filterInventorySyncBurst } from "./chest-detector.js";

const LOG_SEED_TAIL_LINES = 400;
const DEFAULT_POLL_INTERVAL_MS = 2000;

export class BrowserLogPoller {
  /**
   * @param {{
   *   onEvents?: (events: import("./chest-detector.js").ChestEvent[]) => void,
   *   onPoll?: (stats: { linesRead: number, fileSize: number, truncated: boolean }) => void,
   *   onLogReset?: () => void,
   *   considerCommonChest?: boolean,
   *   flatCountDropGate?: (itemKey: string) => boolean,
   *   pollIntervalMs?: number,
   * }} options
   */
  constructor({
    onEvents = () => {},
    onPoll = () => {},
    onLogReset = () => {},
    considerCommonChest = true,
    flatCountDropGate = null,
    pollIntervalMs = DEFAULT_POLL_INTERVAL_MS,
  } = {}) {
    this.onEvents = onEvents;
    this.onPoll = onPoll;
    this.onLogReset = onLogReset;
    this.pollIntervalMs = pollIntervalMs;
    /** @type {FileSystemFileHandle | null} */
    this.fileHandle = null;
    this.fileName = "";
    this.byteOffset = 0;
    this.running = false;
    /** @type {ReturnType<typeof setInterval> | null} */
    this.intervalId = null;
    this.detector = new ChestDetector({
      considerCommonChest,
      flatCountDropGate,
    });
    this.detector.enableCountTracking(true);
    this.partialLine = "";
    this.totalLinesRead = 0;
  }

  setConsiderCommonChest(enabled) {
    this.detector.setConsiderCommonChest(enabled);
  }

  setFlatCountDropGate(gate) {
    this.detector.setFlatCountDropGate(gate);
  }

  setWatchBossKeys(keys) {
    this.detector.setWatchBossKeys(keys);
  }

  setWatchCommonKeys(keys) {
    this.detector.setWatchCommonKeys(keys);
  }

  /**
   * @param {FileSystemFileHandle} handle
   */
  async connect(handle) {
    this.fileHandle = handle;
    this.fileName = handle.name;
    this.totalLinesRead = 0;
    const file = await handle.getFile();
    this.detector.resetState();
    await this.seedFromFile(file);
    this.byteOffset = file.size;
    this.partialLine = "";
  }

  /**
   * @param {File} file
   */
  async connectFromFile(file) {
    this.fileHandle = null;
    this.fileName = file.name;
    this.totalLinesRead = 0;
    this.detector.resetState();
    await this.seedFromFile(file);
    this.byteOffset = file.size;
    this.partialLine = "";
  }

  /**
   * @param {File} file
   */
  async seedFromFile(file) {
    const tailBytes = 512 * 1024;
    const start = Math.max(0, file.size - tailBytes);
    const chunk = file.slice(start, file.size);
    const text = await chunk.text();
    const lines = text.split(/\r?\n/).slice(-LOG_SEED_TAIL_LINES);
    for (const line of lines) {
      this.detector.seedLine(line);
    }
  }

  async handleLogTruncation(file) {
    this.byteOffset = 0;
    this.partialLine = "";
    this.detector.resetState();
    await this.seedFromFile(file);
    this.byteOffset = file.size;
    this.onLogReset();
  }

  start() {
    if (this.running) {
      return;
    }
    this.running = true;
    this.poll();
    this.intervalId = setInterval(() => this.poll(), this.pollIntervalMs);
  }

  stop() {
    this.running = false;
    if (this.intervalId !== null) {
      clearInterval(this.intervalId);
      this.intervalId = null;
    }
  }

  async poll() {
    if (!this.running) {
      return;
    }

    let file;
    try {
      if (this.fileHandle) {
        file = await this.fileHandle.getFile();
      } else {
        return;
      }
    } catch {
      this.stop();
      return;
    }

    let truncated = false;
    if (file.size < this.byteOffset) {
      truncated = true;
      await this.handleLogTruncation(file);
    }

    if (file.size === this.byteOffset) {
      this.onPoll({
        linesRead: 0,
        fileSize: file.size,
        truncated,
      });
      return;
    }

    const chunk = file.slice(this.byteOffset, file.size);
    this.byteOffset = file.size;
    const text = this.partialLine + (await chunk.text());
    const parts = text.split(/\r?\n/);
    this.partialLine = parts.pop() ?? "";

    let linesThisPoll = 0;
    /** @type {import("./chest-detector.js").ChestEvent[]} */
    const batchEvents = [];
    for (const line of parts) {
      if (!line) {
        continue;
      }
      linesThisPoll += 1;
      this.totalLinesRead += 1;
      const event = this.detector.processLine(line);
      if (event) {
        batchEvents.push(event);
      }
    }

    const filtered = filterInventorySyncBurst(batchEvents);
    if (filtered.length > 0) {
      this.onEvents(filtered);
    }

    this.onPoll({
      linesRead: linesThisPoll,
      fileSize: file.size,
      truncated,
    });
  }

  isConnected() {
    return Boolean(this.fileHandle || this.fileName);
  }

  getFileName() {
    return this.fileName;
  }

  getTotalLinesRead() {
    return this.totalLinesRead;
  }
}

export function isFileSystemAccessSupported() {
  return typeof window.showOpenFilePicker === "function";
}

export async function pickPlayerLogFile() {
  if (!isFileSystemAccessSupported()) {
    return null;
  }
  const [handle] = await window.showOpenFilePicker({
    types: [
      {
        description: "Player.log",
        accept: { "text/plain": [".log"] },
      },
    ],
    multiple: false,
  });
  return handle;
}
