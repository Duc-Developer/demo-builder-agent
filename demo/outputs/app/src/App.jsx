import React, { useEffect, useMemo, useReducer, useRef, useState } from "react";
import Header from "./components/Header.jsx";
import AddTodoForm from "./components/AddTodoForm.jsx";
import TodoControls from "./components/TodoControls.jsx";
import TodoList from "./components/TodoList.jsx";
import FooterStats from "./components/FooterStats.jsx";
import ConfirmDialog from "./components/ConfirmDialog.jsx";
import { loadTasks, saveTasks } from "./utils/storage.js";
import { createId } from "./utils/uuid.js";

const STORAGE_KEY = "newtodoapp.tasks";
const TITLE_MAX_LEN = 200;

function tasksReducer(state, action) {
  switch (action.type) {
    case "init": {
      return Array.isArray(action.payload) ? action.payload : [];
    }
    case "add": {
      const now = Date.now();
      const newTask = {
        id: createId(),
        title: action.payload.title,
        completed: false,
        createdAt: now
      };
      // Newest on top
      return [newTask, ...state];
    }
    case "toggle": {
      const { id } = action.payload;
      return state.map((t) => (t.id === id ? { ...t, completed: !t.completed } : t));
    }
    case "updateTitle": {
      const { id, title } = action.payload;
      return state.map((t) => (t.id === id ? { ...t, title } : t));
    }
    case "remove": {
      const { id } = action.payload;
      return state.filter((t) => t.id !== id);
    }
    case "clearCompleted": {
      return state.filter((t) => !t.completed);
    }
    default:
      return state;
  }
}

export default function App() {
  const [tasks, dispatch] = useReducer(tasksReducer, []);
  const [filter, setFilter] = useState("all"); // all | active | completed
  const [searchQuery, setSearchQuery] = useState("");

  const [editingTaskId, setEditingTaskId] = useState(null);
  const [editingTitleDraft, setEditingTitleDraft] = useState("");
  const [editError, setEditError] = useState("");

  const [confirmState, setConfirmState] = useState({
    open: false,
    title: "",
    message: "",
    confirmText: "Xóa",
    intent: /** @type {null | {type: "deleteOne", id: string} | {type: "clearCompleted"}} */ (null)
  });

  const addInputRef = useRef(null);

  useEffect(() => {
    const initial = loadTasks(STORAGE_KEY);
    dispatch({ type: "init", payload: initial });
  }, []);

  useEffect(() => {
    saveTasks(STORAGE_KEY, tasks);
  }, [tasks]);

  const completedCount = useMemo(() => tasks.reduce((acc, t) => acc + (t.completed ? 1 : 0), 0), [tasks]);
  const activeCount = useMemo(() => tasks.reduce((acc, t) => acc + (!t.completed ? 1 : 0), 0), [tasks]);

  const normalizedQuery = searchQuery.trim().toLowerCase();

  const visibleTasks = useMemo(() => {
    let list = tasks;

    if (filter === "active") list = list.filter((t) => !t.completed);
    if (filter === "completed") list = list.filter((t) => t.completed);

    if (normalizedQuery) {
      list = list.filter((t) => t.title.toLowerCase().includes(normalizedQuery));
    }

    return list;
  }, [tasks, filter, normalizedQuery]);

  const showEmptyAll = tasks.length === 0;
  const showEmptySearch = tasks.length > 0 && visibleTasks.length === 0;

  function focusAddInput() {
    if (addInputRef.current) addInputRef.current.focus();
  }

  function onAddTask(rawTitle) {
    const title = rawTitle.trim();
    if (!title) return { ok: false, error: "Vui lòng nhập nội dung" };
    const safe = title.slice(0, TITLE_MAX_LEN);
    dispatch({ type: "add", payload: { title: safe } });
    focusAddInput();
    return { ok: true };
  }

  function startEdit(task) {
    setEditingTaskId(task.id);
    setEditingTitleDraft(task.title);
    setEditError("");
  }

  function cancelEdit() {
    setEditingTaskId(null);
    setEditingTitleDraft("");
    setEditError("");
  }

  function commitEdit(taskId) {
    const title = editingTitleDraft.trim();
    if (!title) {
      setEditError("Vui lòng nhập nội dung");
      return false;
    }
    dispatch({ type: "updateTitle", payload: { id: taskId, title: title.slice(0, TITLE_MAX_LEN) } });
    setEditingTaskId(null);
    setEditingTitleDraft("");
    setEditError("");
    return true;
  }

  function requestDeleteTask(taskId) {
    setConfirmState({
      open: true,
      title: "Xác nhận",
      message: "Bạn có chắc muốn xóa việc này?",
      confirmText: "Xóa",
      intent: { type: "deleteOne", id: taskId }
    });
  }

  function requestClearCompleted() {
    setConfirmState({
      open: true,
      title: "Xác nhận",
      message: "Xóa tất cả việc đã hoàn thành?",
      confirmText: "Xóa",
      intent: { type: "clearCompleted" }
    });
  }

  function closeConfirm() {
    setConfirmState((s) => ({ ...s, open: false, intent: null }));
  }

  function confirmAction() {
    const intent = confirmState.intent;
    if (!intent) return;

    if (intent.type === "deleteOne") {
      // If deleting the task being edited, exit edit mode.
      if (editingTaskId === intent.id) cancelEdit();
      dispatch({ type: "remove", payload: { id: intent.id } });
    } else if (intent.type === "clearCompleted") {
      // If currently editing a completed task, exit edit mode after clearing.
      if (editingTaskId) {
        const editingTask = tasks.find((t) => t.id === editingTaskId);
        if (editingTask?.completed) cancelEdit();
      }
      dispatch({ type: "clearCompleted" });
    }
    closeConfirm();
  }

  return (
    <div className="appRoot">
      <div className="container">
        <Header />

        <main className="card" aria-label="Todo app">
          <AddTodoForm
            ref={addInputRef}
            maxLen={TITLE_MAX_LEN}
            onAdd={onAddTask}
          />

          <TodoControls
            filter={filter}
            onChangeFilter={(next) => setFilter(next)}
            searchQuery={searchQuery}
            onChangeSearch={setSearchQuery}
            completedCount={completedCount}
            onClearCompleted={requestClearCompleted}
          />

          <TodoList
            tasks={visibleTasks}
            isEmptyAll={showEmptyAll}
            isEmptySearch={showEmptySearch}
            onToggle={(id) => dispatch({ type: "toggle", payload: { id } })}
            onRequestDelete={requestDeleteTask}
            onStartEdit={startEdit}
            editingTaskId={editingTaskId}
            editingTitleDraft={editingTitleDraft}
            onChangeEditingTitle={(v) => {
              setEditingTitleDraft(v.slice(0, TITLE_MAX_LEN));
              if (editError) setEditError("");
            }}
            editError={editError}
            onCommitEdit={commitEdit}
            onCancelEdit={cancelEdit}
            maxLen={TITLE_MAX_LEN}
          />

          <FooterStats activeCount={activeCount} totalCount={tasks.length} />
        </main>
      </div>

      <ConfirmDialog
        open={confirmState.open}
        title={confirmState.title}
        message={confirmState.message}
        confirmText={confirmState.confirmText}
        cancelText="Hủy"
        onCancel={closeConfirm}
        onConfirm={confirmAction}
      />
    </div>
  );
}

