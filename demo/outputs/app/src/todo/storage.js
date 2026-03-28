import { STORAGE_KEY } from "./constants.js";

/**
 * @returns {import("./types").TodoItem[]}
 */
export function readTodos() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw);
    if (!Array.isArray(parsed)) return [];
    // Minimal shape validation
    return parsed
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
  } catch (e) {
    // Fail-safe: do not crash app if JSON is invalid
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

