import React, { useEffect, useMemo, useRef } from "react";
import { createPortal } from "react-dom";
import { getFocusableElements } from "../utils/dom.js";

export default function ConfirmDialog({
  open,
  title,
  description,
  confirmText = "Xác nhận",
  cancelText = "Hủy",
  tone = "danger",
  onConfirm,
  onCancel,
}) {
  const dialogRef = useRef(null);
  const lastActiveRef = useRef(null);

  const confirmBtnClass = useMemo(() => {
    if (tone === "danger") return "btn danger";
    if (tone === "primary") return "btn primary";
    return "btn";
  }, [tone]);

  useEffect(() => {
    if (!open) return;

    lastActiveRef.current = document.activeElement;

    const dialogEl = dialogRef.current;
    if (!dialogEl) return;

    const focusables = getFocusableElements(dialogEl);
    const initial = focusables[0] || dialogEl;
    const id = requestAnimationFrame(() => initial.focus());

    function onKeyDown(e) {
      if (e.key === "Escape") {
        e.preventDefault();
        onCancel?.();
        return;
      }
      if (e.key !== "Tab") return;

      const els = getFocusableElements(dialogEl);
      if (els.length === 0) return;

      const first = els[0];
      const last = els[els.length - 1];

      if (e.shiftKey) {
        if (document.activeElement === first || document.activeElement === dialogEl) {
          e.preventDefault();
          last.focus();
        }
      } else {
        if (document.activeElement === last) {
          e.preventDefault();
          first.focus();
        }
      }
    }

    document.addEventListener("keydown", onKeyDown);
    return () => {
      cancelAnimationFrame(id);
      document.removeEventListener("keydown", onKeyDown);
    };
  }, [open, onCancel]);

  useEffect(() => {
    if (open) return;
    const prev = lastActiveRef.current;
    if (prev && typeof prev.focus === "function") {
      requestAnimationFrame(() => prev.focus());
    }
  }, [open]);

  if (!open) return null;

  return createPortal(
    <div
      className="backdrop"
      role="presentation"
      onMouseDown={(e) => {
        if (e.target === e.currentTarget) onCancel?.();
      }}
    >
      <div
        className="dialog"
        role="dialog"
        aria-modal="true"
        aria-label={title}
        ref={dialogRef}
        tabIndex={-1}
      >
        <div className="dialog-head">
          <h2 className="dialog-title">{title}</h2>
        </div>
        <div className="dialog-body">{description}</div>
        <div className="dialog-actions">
          <button type="button" className="btn" onClick={onCancel} aria-label={cancelText}>
            {cancelText}
          </button>
          <button type="button" className={confirmBtnClass} onClick={onConfirm} aria-label={confirmText}>
            {confirmText}
          </button>
        </div>
      </div>
    </div>,
    document.body
  );
}

