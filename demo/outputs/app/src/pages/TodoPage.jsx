import React, { useEffect, useMemo, useReducer, useRef, useState } from "react";
import { initialState, todoReducer } from "../todo/reducer.js";
import { readTodos, writeTodos } from "../todo/storage.js";
import { completedCount, remainingCount, visibleTodos } from "../todo/selectors.js";
import { createId } from "../utils/id.js";

import TodoInput from "../components/TodoInput.jsx";
import TodoControls from "../components/TodoControls.jsx";
import TodoList from "../components/TodoList.jsx";
import EmptyState from "../components/EmptyState.jsx";
import ConfirmDialog from "../components/ConfirmDialog.jsx";

function formatDateVi(d = new Date()) {
  try {
    return new Intl.DateTimeFormat("vi-VN", { weekday: "short", day: "2-digit", month: "2-digit", year: "numeric" }).format(d);
  } catch {
    return d.toLocaleDateString();
  }
}

export default function TodoPage() {
  const [state, dispatch] = useReducer(todoReducer, initialState);
  const didInitRef = useRef(false);

  const [confirmState, setConfirmState] = useState(
    /** @type {null | { kind: "deleteOne"; id: string; title: string } | { kind: "clearCompleted"; count: number }} */ (null)
  );

  useEffect(() => {
    if (didInitRef.current) return;
    didInitRef.current = true;

    const todos = readTodos();
    dispatch({ type: "LOAD_TODOS", todos });
  }, []);

  useEffect(() => {
    if (!didInitRef.current) return;
    writeTodos(state.todos);
  }, [state.todos]);

  const remaining = useMemo(() => remainingCount(state.todos), [state.todos]);
  const completed = useMemo(() => completedCount(state.todos), [state.todos]);

  const visible = useMemo(
    () => visibleTodos(state.todos, state.filter, state.searchQuery),
    [state.todos, state.filter, state.searchQuery]
  );

  const showEmptyNoTodos = state.todos.length === 0;
  const showEmptyNoMatch = state.todos.length > 0 && visible.length === 0;

  function addTodo(rawTitle) {
    const now = Date.now();
    const todo = {
      id: createId(),
      title: rawTitle,
      completed: false,
      createdAt: now,
      updatedAt: now,
    };
    dispatch({ type: "ADD_TODO", todo });
  }

  function onRequestDelete(todo) {
    setConfirmState({ kind: "deleteOne", id: todo.id, title: todo.title });
  }

  function onConfirmDelete() {
    if (!confirmState || confirmState.kind !== "deleteOne") return;
    dispatch({ type: "DELETE_TODO", id: confirmState.id });
    setConfirmState(null);
  }

  function onRequestClearCompleted() {
    setConfirmState({ kind: "clearCompleted", count: completed });
  }

  function onConfirmClearCompleted() {
    dispatch({ type: "CLEAR_COMPLETED" });
    setConfirmState(null);
  }

  return (
    <div className="card">
      <div className="header">
        <h1>Todo</h1>
        <div className="date" aria-label="Ngày hiện tại">
          {formatDateVi(new Date())}
        </div>
      </div>

      {state.error ? (
        <div className="banner" role="alert">
          {state.error}
        </div>
      ) : null}

      <div className="section">
        <TodoInput onAdd={addTodo} />
        <div className="kbd-hint">Mẹo: Enter để thêm • Double click tiêu đề để sửa • Esc để hủy khi đang sửa</div>
      </div>

      <div className="hr" />

      <div className="section">
        <TodoControls
          filter={state.filter}
          onChangeFilter={(filter) => dispatch({ type: "SET_FILTER", filter })}
          searchQuery={state.searchQuery}
          onChangeSearch={(searchQuery) => dispatch({ type: "SET_SEARCH_QUERY", searchQuery })}
          remaining={remaining}
          completed={completed}
          onClearCompleted={onRequestClearCompleted}
        />
      </div>

      <div className="hr" />

      {showEmptyNoTodos ? (
        <EmptyState text="Chưa có việc nào. Thêm việc đầu tiên!" />
      ) : showEmptyNoMatch ? (
        <EmptyState text="Không có việc phù hợp." />
      ) : (
        <TodoList
          todos={visible}
          onToggle={(id) => dispatch({ type: "TOGGLE_TODO", id })}
          onEdit={(id, title) => dispatch({ type: "EDIT_TODO", id, title, updatedAt: Date.now() })}
          onDelete={onRequestDelete}
        />
      )}

      <ConfirmDialog
        open={confirmState !== null}
        title={
          confirmState?.kind === "deleteOne"
            ? "Xóa công việc?"
            : confirmState?.kind === "clearCompleted"
              ? "Xóa các việc đã hoàn thành?"
              : ""
        }
        description={
          confirmState?.kind === "deleteOne"
            ? `Bạn có chắc muốn xóa “${confirmState.title}”? Thao tác này không thể hoàn tác.`
            : confirmState?.kind === "clearCompleted"
              ? `Bạn có chắc muốn xóa ${confirmState.count} công việc đã hoàn thành?`
              : ""
        }
        confirmText="Xóa"
        cancelText="Hủy"
        tone="danger"
        onCancel={() => setConfirmState(null)}
        onConfirm={() => {
          if (confirmState?.kind === "deleteOne") onConfirmDelete();
          else if (confirmState?.kind === "clearCompleted") onConfirmClearCompleted();
        }}
      />
    </div>
  );
}

