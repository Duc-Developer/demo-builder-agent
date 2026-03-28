import { FILTERS } from "./constants.js";

/** @typedef {import("./types").TodoItem} TodoItem */
/** @typedef {import("./types").State} State */

export const initialState =
  /** @type {State} */ ({
    todos: [],
    filter: FILTERS.all,
    searchQuery: "",
    editingId: undefined,
    error: null,
  });

/**
 * @typedef {(
 *  | { type: "LOAD_TODOS"; todos: TodoItem[] }
 *  | { type: "ADD_TODO"; todo: TodoItem }
 *  | { type: "TOGGLE_TODO"; id: string }
 *  | { type: "EDIT_TODO"; id: string; title: string; updatedAt: number }
 *  | { type: "DELETE_TODO"; id: string }
 *  | { type: "CLEAR_COMPLETED" }
 *  | { type: "SET_FILTER"; filter: State["filter"] }
 *  | { type: "SET_SEARCH_QUERY"; searchQuery: string }
 *  | { type: "SET_ERROR"; error: string | null }
 * )} Action
 */

/**
 * @param {State} state
 * @param {Action} action
 * @returns {State}
 */
export function todoReducer(state, action) {
  switch (action.type) {
    case "LOAD_TODOS": {
      const sorted = [...action.todos].sort((a, b) => b.createdAt - a.createdAt);
      return { ...state, todos: sorted, error: null };
    }
    case "ADD_TODO": {
      return { ...state, todos: [action.todo, ...state.todos], error: null };
    }
    case "TOGGLE_TODO": {
      const now = Date.now();
      const todos = state.todos.map((t) =>
        t.id === action.id ? { ...t, completed: !t.completed, updatedAt: now } : t
      );
      return { ...state, todos, error: null };
    }
    case "EDIT_TODO": {
      const todos = state.todos.map((t) =>
        t.id === action.id ? { ...t, title: action.title, updatedAt: action.updatedAt } : t
      );
      return { ...state, todos, editingId: undefined, error: null };
    }
    case "DELETE_TODO": {
      const todos = state.todos.filter((t) => t.id !== action.id);
      return { ...state, todos, error: null };
    }
    case "CLEAR_COMPLETED": {
      const todos = state.todos.filter((t) => !t.completed);
      return { ...state, todos, error: null };
    }
    case "SET_FILTER": {
      return { ...state, filter: action.filter };
    }
    case "SET_SEARCH_QUERY": {
      return { ...state, searchQuery: action.searchQuery };
    }
    case "SET_ERROR": {
      return { ...state, error: action.error };
    }
    default:
      return state;
  }
}

