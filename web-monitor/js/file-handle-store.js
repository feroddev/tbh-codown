const DB_NAME = "tbh-tracker-files";
const DB_VERSION = 1;
const STORE_NAME = "handles";
const HANDLE_KEY = "player-log";

/**
 * @returns {Promise<IDBDatabase>}
 */
function openDb() {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open(DB_NAME, DB_VERSION);
    request.onerror = () => reject(request.error);
    request.onsuccess = () => resolve(request.result);
    request.onupgradeneeded = (event) => {
      const db = event.target.result;
      if (!db.objectStoreNames.contains(STORE_NAME)) {
        db.createObjectStore(STORE_NAME);
      }
    };
  });
}

/**
 * @param {FileSystemFileHandle} handle
 */
export async function savePlayerLogHandle(handle) {
  const db = await openDb();
  return new Promise((resolve, reject) => {
    const tx = db.transaction(STORE_NAME, "readwrite");
    tx.oncomplete = () => {
      db.close();
      resolve();
    };
    tx.onerror = () => reject(tx.error);
    tx.objectStore(STORE_NAME).put(handle, HANDLE_KEY);
  });
}

/**
 * @returns {Promise<FileSystemFileHandle | null>}
 */
export async function loadPlayerLogHandle() {
  const db = await openDb();
  return new Promise((resolve, reject) => {
    const tx = db.transaction(STORE_NAME, "readonly");
    tx.onerror = () => reject(tx.error);
    const request = tx.objectStore(STORE_NAME).get(HANDLE_KEY);
    request.onsuccess = () => {
      db.close();
      resolve(request.result ?? null);
    };
    request.onerror = () => reject(request.error);
  });
}

export async function clearPlayerLogHandle() {
  const db = await openDb();
  return new Promise((resolve, reject) => {
    const tx = db.transaction(STORE_NAME, "readwrite");
    tx.oncomplete = () => {
      db.close();
      resolve();
    };
    tx.onerror = () => reject(tx.error);
    tx.objectStore(STORE_NAME).delete(HANDLE_KEY);
  });
}

const READ_OPTIONS = { mode: "read" };

/**
 * @param {FileSystemFileHandle} handle
 * @returns {Promise<"granted" | "prompt" | "denied">}
 */
export async function queryReadPermission(handle) {
  return handle.queryPermission(READ_OPTIONS);
}

/**
 * @param {FileSystemFileHandle} handle
 * @returns {Promise<"granted" | "denied">}
 */
export async function requestReadPermission(handle) {
  return handle.requestPermission(READ_OPTIONS);
}

/**
 * @param {FileSystemFileHandle} handle
 * @returns {Promise<{ status: "ok", handle: FileSystemFileHandle } | { status: "needs_permission", handle: FileSystemFileHandle } | { status: "missing" } | { status: "denied" }>}
 */
export async function inspectPlayerLogHandle(handle) {
  if (!handle) {
    return { status: "missing" };
  }

  let permission;
  try {
    permission = await queryReadPermission(handle);
  } catch {
    return { status: "missing" };
  }

  if (permission === "denied") {
    return { status: "denied" };
  }

  if (permission === "prompt") {
    return { status: "needs_permission", handle };
  }

  try {
    await handle.getFile();
    return { status: "ok", handle };
  } catch {
    return { status: "missing" };
  }
}

/**
 * @param {FileSystemFileHandle} handle
 * @returns {Promise<FileSystemFileHandle | null>}
 */
export async function grantReadAccess(handle) {
  const permission = await requestReadPermission(handle);
  if (permission !== "granted") {
    return null;
  }

  try {
    await handle.getFile();
    return handle;
  } catch {
    return null;
  }
}
