import React from "react";
import TodoItemRow from "./TodoItemRow.jsx";

export default function TodoList({ todos, onToggle, onEdit, onDelete }) {
  return (
    <ul className="list" aria-label="Danh sách công việc">
      {todos.map((t) => (
        <li key={t.id} className="item">
          <TodoItemRow todo={t} onToggle={onToggle} onEdit={onEdit} onDelete={onDelete} />
        </li>
      ))}
    </ul>
  );
}

