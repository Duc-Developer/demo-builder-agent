import React, { useEffect, useMemo, useReducer, useRef } from "react";
import { Navigate, Route, Routes, useLocation, useNavigate } from "react-router-dom";
import HomePage from "./pages/HomePage.jsx";
import SettingsPage from "./pages/SettingsPage.jsx";
import { loadTasks, saveTasks } from "./storage/taskStorage.js";
import { loadTheme, saveTheme, resolveTheme, THEME_KEY } from "./storage/themeStorage.js";
import Toast from "./components/Toast.jsx";
import { createId } from "./utils/id.js";

const TASKS_KEY = "new-todoapp.tasks.v1";

const initialState = {
  hydrated: false,
  tasks: [],
  filter: "all",
  searchQuery: "",
  theme: "system", // system | light | dark
  toast: null
};

function sortTasks(tasks) {
  const active = tasks
    .filter((t) => t.status === "active")
    .sort((a, b) => b.createdAt - a.createdAt);
  const completed = tasks
    .filter((t) => t.status === "completed")
    .sort((a, b) => b.createdAt - a.createdAt);
  return [...active, ...completed];
}

function reducer(state, action) {
  switch (action.type) {
    case "HYDRATE": {
      const tasks = Array.isArray(action.tasks) ? sortTasks(action.tasks) : [];
      return {
        ...state,
        hydrated: true,
        tasks,
        theme: action.theme ?? state.theme
      };
    }
    case "SET_FILTER":
      return { ...state, filter: action.filter };
    case "SET_SEARCH":
      return { ...state, searchQuery: action.query };
    case "ADD_TASK": {
      const now = Date.now();
      const newTask = {
        id: createId(),
        title: action.title,
        note: action.note || "",
        status: "active",
        createdAt: now,
        updatedAt: now
      };
      return { ...state, tasks: sortTasks([newTask, ...state.tasks]) };
    }
    case "UPDATE_TASK": {
      const now = Date.now();
      const tasks = state.tasks.map((t) => {
        if (t.id !== action.id) return t;
        return {
          ...t,
          title: action.title,
          note: action.note ?? "",
          status: action.status ?? t.status,
          updatedAt: now
        };
      });
      return { ...state, tasks: sortTasks(tasks) };
    }
    case "TOGGLE_TASK": {
      const now = Date.now();
      const tasks = state.tasks.map((t) => {
        if (t.id !== action.id) return t;
        const nextStatus = t.status === "active" ? "completed" : "active";
        return { ...t, status: nextStatus, updatedAt: now };
      });
      return { ...state, tasks: sortTasks(tasks) };
    }
    case "DELETE_TASK": {
      const tasks = state.tasks.filter((t) => t.id !== action.id);
      return { ...state, tasks };
    }
    case "RESTORE_TASK": {
      const tasks = sortTasks([action.task, ...state.tasks]);
      return { ...state, tasks };
    }
    case "SET_THEME":
      return { ...state, theme: action.theme };
    case "SHOW_TOAST":
      return { ...state, toast: action.toast };
    case "HIDE_TOAST":
      if (!state.toast) return state;
      if (action.id && state.toast.id !== action.id) return state;
      return { ...state, toast: null };
    case "CLEAR_ALL":
      return { ...state, tasks: [] };
    default:
      return state;
  }
}

function useApplyTheme(theme) {
  useEffect(() => {
    const resolved = resolveTheme(theme);
    const root = document.documentElement;
    root.dataset.theme = resolved;
    root.style.colorScheme = resolved;

    if (theme !== "system") return;

    const mq = window.matchMedia?.("(prefers-color-scheme: dark)");
    if (!mq) return;

    const handler = () => {
      const r = resolveTheme("system");
      root.dataset.theme = r;
      root.style.colorScheme = r;
    };

    mq.addEventListener?.("change", handler);
    return () => mq.removeEventListener?.("change", handler);
  }, [theme]);
}

export default function App() {
  const [state, dispatch] = useReducer(reducer, initialState);
  const toastTimerRef = useRef(null);

  useApplyTheme(state.theme);

  // Hydrate
  useEffect(() => {
    const tasks = loadTasks(TASKS_KEY);
    const theme = loadTheme(THEME_KEY) ?? "system";
    dispatch({ type: "HYDRATE", tasks, theme });
  }, []);

  // Persist tasks
  useEffect(() => {
    if (!state.hydrated) return;
    saveTasks(TASKS_KEY, state.tasks);
  }, [state.hydrated, state.tasks]);

  // Persist theme
  useEffect(() => {
    if (!state.hydrated) return;
    saveTheme(THEME_KEY, state.theme);
  }, [state.hydrated, state.theme]);

  // Toast auto-hide
  useEffect(() => {
    if (!state.toast) return;
    if (toastTimerRef.current) window.clearTimeout(toastTimerRef.current);
    toastTimerRef.current = window.setTimeout(() => {
      dispatch({ type: "HIDE_TOAST", id: state.toast?.id });
    }, state.toast.durationMs ?? 4000);

    return () => {
      if (toastTimerRef.current) window.clearTimeout(toastTimerRef.current);
    };
  }, [state.toast]);

  const api = useMemo(() => {
    const showToast = (toast) => {
      dispatch({
        type: "SHOW_TOAST",
        toast: {
          id: createId(),
          durationMs: 4200,
          ...toast
        }
      });
    };

    const completeWithUndo = (taskId) => {
      const prev = state.tasks.find((t) => t.id === taskId);
      if (!prev) return;
      dispatch({ type: "TOGGLE_TASK", id: taskId });

      const willBeCompleted = prev.status === "active";
      showToast({
        message: willBeCompleted ? "Đã hoàn thành" : "Đã hoàn tác hoàn thành",
        actionLabel: "Hoàn tác",
        onAction: () => dispatch({ type: "TOGGLE_TASK", id: taskId })
      });
    };

    const deleteWithUndo = (taskId) => {
      const prev = state.tasks.find((t) => t.id === taskId);
      if (!prev) return;
      dispatch({ type: "DELETE_TASK", id: taskId });
      showToast({
        message: "Đã xoá",
        actionLabel: "Hoàn tác",
        onAction: () => dispatch({ type: "RESTORE_TASK", task: prev })
      });
    };

    return {
      dispatch,
      showToast,
      completeWithUndo,
      deleteWithUndo
    };
  }, [state.tasks]);

  return (
    <div className="app">
      <Routes>
        <Route
          path="/"
          element={
            <HomePage
              hydrated={state.hydrated}
              tasks={state.tasks}
              filter={state.filter}
              searchQuery={state.searchQuery}
              onChangeFilter={(filter) => dispatch({ type: "SET_FILTER", filter })}
              onChangeSearch={(query) => dispatch({ type: "SET_SEARCH", query })}
              onAddTask={({ title, note }) => dispatch({ type: "ADD_TASK", title, note })}
              onUpdateTask={({ id, title, note, status }) =>
                dispatch({ type: "UPDATE_TASK", id, title, note, status })
              }
              onToggleTask={(id) => api.completeWithUndo(id)}
              onDeleteTask={(id) => api.deleteWithUndo(id)}
              onShowToast={api.showToast}
            />
          }
        />
        <Route
          path="/settings"
          element={
            <SettingsPage
              theme={state.theme}
              onChangeTheme={(theme) => dispatch({ type: "SET_THEME", theme })}
              onClearAll={() => dispatch({ type: "CLEAR_ALL" })}
              onShowToast={api.showToast}
            />
          }
        />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>

      <Toast
        toast={state.toast}
        onClose={() => dispatch({ type: "HIDE_TOAST", id: state.toast?.id })}
      />
    </div>
  );
}

