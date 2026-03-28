import React, { useEffect, useMemo, useRef, useState } from "react";
import { TITLE_MAX_LENGTH } from "../todo/constants.js";

function formatTime(ts) {
  try {
    return new Intl.DateTimeFormat("vi-VN", {
      hour: "2-digit",
      minute: "2-digit",
      day: "2-digit",
      month: "2-digit",
    }).format(new Date(ts));
  } catch {
    return new Date(ts).toLocaleString();
  }
}

function validateTitle(title) {
  const trimmed = title.trim();
  if (!trimmed) return { ok: false, error: "Tiêu đề không được để trống.", value: "" };
  if (trimmed.length > TITLE_MAX_LENGTH)
    return { ok: false, error: `Tiêu đề tối đa ${TITLE_MAX_LENGTH} ký tự`, value: trimmed };
  return { ok: true, error: "", value: trimmed };
}

export default function TodoItemRow({ todo, onToggle, onEdit, onDelete }) {
  const [isEditing, setIsEditing] = useState(false);
  const [draft, setDraft] = useState(todo.title);
  const [error, setError] = useState("");
  const editRef = useRef(null);

  const createdLabel = useMemo(() => formatTime(todo.createdAt), [todo.createdAt]);

  useEffect(() => {
    if (!isEditing) return;
    setDraft(todo.title);
    setError("");
    const id = requestAnimationFrame(() => editRef.current?.focus());
    return () => cancelAnimationFrame(id);
  }, [isEditing, todo.title]);

  function startEdit() {
    setIsEditing(true);
  }

  function cancelEdit() {
    setIsEditing(false);
    setDraft(todo.title);
    setError("");
  }

  function commitEdit() {
    const res = validateTitle(draft);
    if (!res.ok) {
      setError(res.error);
      return false;
    }
    if (res.value !== todo.title) {
      onEdit(todo.id, res.value);
    }
    setIsEditing(false);
    setError("");
    return true;
  }

  return (
    <>
      <input
        className="checkbox"
        type="checkbox"
        checked={todo.completed}
        aria-label={todo.completed ? "Bỏ hoàn thành" : "Đánh dấu hoàn thành"}
        onChange={() => onToggle(todo.id)}
      />

      <div>
        {!isEditing ? (
          <>
            <div
              className={todo.completed ? "title completed" : "title"}
              onDoubleClick={startEdit}
              role="button"
              tabIndex={0}
              aria-label="Tiêu đề công việc (double click để sửa)"
              onKeyDown={(e) => {
                if (e.key === "Enter") startEdit();
              }}
              title="Double click để sửa"
            >
              {todo.title}
            </div>
            <div className="meta" aria-label="Thời gian tạo">
              Tạo lúc: {createdLabel}
            </div>
          </>
        ) : (
          <div className="inline-edit" aria-label="Chỉnh sửa công việc">
            <input
              ref={editRef}
              className="input"
              value={draft}
              aria-label="Nội dung chỉnh sửa"
              onChange={(e) => {
                setDraft(e.target.value);
                if (error) setError("");
              }}
              onKeyDown={(e) => {
                if (e.key === "Enter") {
                  e.preventDefault();
                  commitEdit();
                } else if (e.key === "Escape") {
                  e.preventDefault();
                  cancelEdit();
                }
              }}
              onBlur={() => {
                commitEdit();
              }}
            />

            {error ? (
              <div className="error" role="alert">
                {error}
              </div>
            ) : null}

            <div className="inline-edit-actions">
              <button type="button" className="btn primary" onMouseDown={(e) => e.preventDefault()} onClick={commitEdit}>
                Lưu
              </button>
              <button type="button" className="btn" onMouseDown={(e) => e.preventDefault()} onClick={cancelEdit}>
                Hủy
              </button>
            </div>
          </div>
        )}
      </div>

      <div className="item-actions" aria-label="Hành động">
        {!isEditing ? (
          <>
            <button type="button" className="btn" onClick={startEdit} aria-label="Sửa công việc">
              Sửa
            </button>
            <button
              type="button"
              className="btn danger"
              onClick={() => onDelete(todo)}
              aria-label="Xóa công việc"
            >
              Xóa
            </button>
          </>
        ) : null}
      </div>
    </>
  );
}

