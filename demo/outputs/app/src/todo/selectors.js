import { FILTERS } from "./constants.js";

/** @typedef {import("./types").TodoItem} TodoItem */
/** @typedef {import("./types").State} State */

/**
 * @param {TodoItem[]} todos
 */
export function remainingCount(todos) {
  let count = 0;
  for (const t of todos) if (!t.completed) count++;
  return count;
}

/**
 * @param {TodoItem[]} todos
 */
export function completedCount(todos) {
  let count = 0;
  for (const t of todos) if (t.completed) count++;
  return count;
}

/**
 * @param {State["filter"]} filter
 * @returns {(t: TodoItem) => boolean}
 */
export function predicateByFilter(filter) {
  switch (filter) {
    case FILTERS.active:
      return (t) => !t.completed;
    case FILTERS.completed:
      return (t) => t.completed;
    case FILTERS.all:
    default:
      return () => true;
  }
}

/**
 * @param {string} query
 * @returns {(t: TodoItem) => boolean}
 */
export function predicateBySearch(query) {
  const q = query.trim().toLowerCase();
  if (!q) return () => true;
  return (t) => t.title.toLowerCase().includes(q);
}

/**
 * @param {TodoItem[]} todos
 * @param {State["filter"]} filter
 * @param {string} searchQuery
 */
export function visibleTodos(todos, filter, searchQuery) {
  const byFilter = predicateByFilter(filter);
  const bySearch = predicateBySearch(searchQuery);
  return todos.filter((t) => byFilter(t) && bySearch(t));
}

