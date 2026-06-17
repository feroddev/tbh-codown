import { LineDropDetector } from "./line-drop-detector.js";

const DEFAULT_POLL_INTERVAL_MS = 5000;

export class BrowserLogPoller {
  /**
   * @param {{
   *   onEvents?: (events: import("./line-drop-detector.js").LineDropEvent[]) => void,
   *   onPoll?: (stats: { linesRead: number, fileSize: number, truncated: boolean }) => void,
   *   onLogReset?: () => void,
   *   considerCommonChest?: boolean,
   *   pollIntervalMs?: number,
   * }} options
   */
  constructor({
    onEvents = () => {},
    onPoll = () => {},
    onLogReset = () => {},
    considerCommonChest = true,
    pollIntervalMs = DEFAULT_POLL_INTERVAL_MS,
  } = {}) {
    this.onEvents = onEvents;
    this.onPoll = onPoll;
    this.onLogReset = onLogReset;
    this.pollIntervalMs = pollIntervalMs;
    /** @type {FileSystemFileHandle | null} */
    this.fileHandle = null;
    this.fileName = "";
    this.running = false;
    /** @type {ReturnType<typeof setInterval> | null} */
    this.intervalId = null;
    this.detector = new LineDropDetector({ considerCommonChest });
    this.totalEventsDetected = 0;
  }

  setConsiderCommonChest(enabled) {
    this.detector.setConsiderCommonChest(enabled);
  }

  /**
   * @param {FileSystemFileHandle} handle
   */
  async connect(handle) {
    this.fileHandle = handle;
    this.fileName = handle.name;
    this.totalEventsDetected = 0;
    const file = await handle.getFile();
    const content = await file.text();
    this.detector.resetState();
    this.detector.seedFromContent(content);
  }

  /**
   * @param {File} file
   */
  async connectFromFile(file) {
    this.fileHandle = null;
    this.fileName = file.name;
    this.totalEventsDetected = 0;
    const content = await file.text();
    this.detector.resetState();
    this.detector.seedFromContent(content);
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

    let content;
    try {
      content = await file.text();
    } catch {
      return;
    }

    const { events, truncated } = this.detector.processContent(content);
    if (truncated) {
      this.onLogReset();
    }
    if (events.length > 0) {
      this.totalEventsDetected += events.length;
      this.onEvents(events);
    }

    this.onPoll({
      linesRead: events.length,
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
    return this.totalEventsDetected;
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
