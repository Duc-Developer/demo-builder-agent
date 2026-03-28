import { LEGACY_STORAGE_KEY, STORAGE_KEY } from "./constants.js";

/**
 * @param {unknown} input
 * @returns {import("./types").TodoItem[]}
 */
function normalizeTodos(input) {
  if (!Array.isArray(input)) return [];
  return input
    .filter((t) => t && typeof t === "object")
    .map((t) => ({
      id: String(t.id ?? ""),
      title: String(t.title ?? ""),
      completed: Boolean(t.completed),
      createdAt: Number(t.createdAt ?? Date.now()),
      updatedAt: Number(t.updatedAt ?? t.createdAt ?? Date.now()),
    }))
    .filter((t) => t.id && t.title)
    .sort((a, b) => b.createdAt - a.createdAt);
}

/**
 * @returns {import("./types").TodoItem[]}
 */
export function readTodos() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) {
      const parsed = JSON.parse(raw);
      return normalizeTodos(parsed);
    }

    // Migration from legacy key (older builds)
    const legacyRaw = localStorage.getItem(LEGACY_STORAGE_KEY);
    if (!legacyRaw) return [];

    const legacyParsed = JSON.parse(legacyRaw);
    const todos = normalizeTodos(legacyParsed);

    // Best-effort: write to new key and optionally cleanup legacy
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(todos));
      localStorage.removeItem(LEGACY_STORAGE_KEY);
    } catch {
      // ignore
    }

    return todos;
  } catch (e) {
    console.warn("[Todo] Failed to parse localStorage, fallback to empty list.", e);
    return [];
  }
}

/**
 * @param {import("./types").TodoItem[]} todos
 */
export function writeTodos(todos) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(todos));
  } catch (e) {
    console.warn("[Todo] Failed to write localStorage.", e);
  }
}

