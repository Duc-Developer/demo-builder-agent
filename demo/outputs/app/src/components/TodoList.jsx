import React, { useId } from "react";
import TodoItem from "./TodoItem.jsx";

/**
 * @typedef {{id: string, title: string, completed: boolean, createdAt?: number}} Task
 */

/**
 * @param {{
 *  tasks: Task[],
 *  isEmptyAll: boolean,
 *  isEmptySearch: boolean,
 *  onToggle: (id: string) => void,
 *  onRequestDelete: (id: string) => void,
 *  onStartEdit: (task: Task) => void,
 *  editingTaskId: string | null,
 *  editingTitleDraft: string,
 *  onChangeEditingTitle: (v: string) => void,
 *  editError: string,
 *  onCommitEdit: (taskId: string) => boolean,
 *  onCancelEdit: () => void,
 *  maxLen: number
 * }} props
 */
export default function TodoList({
  tasks,
  isEmptyAll,
  isEmptySearch,
  onToggle,
  onRequestDelete,
  onStartEdit,
  editingTaskId,
  editingTitleDraft,
  onChangeEditingTitle,
  editError,
  onCommitEdit,
  onCancelEdit,
  maxLen
}) {
  const labelId = useId();

  return (
    <section className="section" aria-labelledby={labelId}>
      <div className="sectionHeader">
        <h2 id={labelId} className="sectionTitle">Danh sách</h2>
      </div>

      {isEmptyAll ? (
        <div className="emptyState" role="status">
          Chưa có việc nào. Hãy thêm việc mới!
        </div>
      ) : isEmptySearch ? (
        <div className="emptyState" role="status">
          Không tìm thấy việc phù hợp.
        </div>
      ) : (
        <ul className="todoList" aria-label="Danh sách việc cần làm">
          {tasks.map((task) => (
            <TodoItem
              key={task.id}
              task={task}
              onToggle={() => onToggle(task.id)}
              onRequestDelete={() => onRequestDelete(task.id)}
              onStartEdit={() => onStartEdit(task)}
              isEditing={editingTaskId === task.id}
              editingTitleDraft={editingTitleDraft}
              onChangeEditingTitle={onChangeEditingTitle}
              editError={editingTaskId === task.id ? editError : ""}
              onCommitEdit={() => onCommitEdit(task.id)}
              onCancelEdit={onCancelEdit}
              maxLen={maxLen}
            />
          ))}
        </ul>
      )}
    </section>
  );
}

