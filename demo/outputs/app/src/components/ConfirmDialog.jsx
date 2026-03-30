import React, { useEffect, useId, useRef } from "react";

/**
 * @param {{
 *  open: boolean,
 *  title: string,
 *  message: string,
 *  confirmText?: string,
 *  cancelText?: string,
 *  onConfirm: () => void,
 *  onCancel: () => void
 * }} props
 */
export default function ConfirmDialog({
  open,
  title,
  message,
  confirmText = "Xóa",
  cancelText = "Hủy",
  onConfirm,
  onCancel
}) {
  const titleId = useId();
  const messageId = useId();
  const cancelBtnRef = useRef(null);

  useEffect(() => {
    if (!open) return;
    const onKeyDown = (e) => {
      if (e.key === "Escape") onCancel();
    };
    window.addEventListener("keydown", onKeyDown);
    cancelBtnRef.current?.focus();
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [open, onCancel]);

  if (!open) return null;

  return (
    <div
      className="modalOverlay"
      role="presentation"
      onMouseDown={(e) => {
        if (e.target === e.currentTarget) onCancel();
      }}
    >
      <div
        className="modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby={titleId}
        aria-describedby={messageId}
      >
        <div className="modalHeader">
          <h3 id={titleId} className="modalTitle">
            {title || "Xác nhận"}
          </h3>
        </div>

        <div id={messageId} className="modalBody">
          {message}
        </div>

        <div className="modalFooter">
          <button ref={cancelBtnRef} type="button" className="btn" onClick={onCancel}>
            {cancelText}
          </button>
          <button type="button" className="btn btnDanger" onClick={onConfirm}>
            {confirmText}
          </button>
        </div>
      </div>
    </div>
  );
}

