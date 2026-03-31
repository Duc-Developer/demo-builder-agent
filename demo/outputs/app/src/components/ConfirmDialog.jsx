import React, { useEffect, useRef } from "react";
import ModalSheet from "./ModalSheet.jsx";

export default function ConfirmDialog({ open, title, description, confirmLabel, danger, onConfirm, onClose }) {
  const confirmRef = useRef(null);

  useEffect(() => {
    // handled by ModalSheet focus trap
  }, []);

  const footer = (
    <div className="modalFooter">
      <button type="button" className="button button--ghost" onClick={onClose}>
        Huỷ
      </button>
      <button
        ref={confirmRef}
        type="button"
        className={`button ${danger ? "button--danger" : "button--primary"}`}
        onClick={onConfirm}
      >
        {confirmLabel}
      </button>
    </div>
  );

  return (
    <ModalSheet open={open} title={title} onClose={onClose} initialFocusRef={confirmRef} footer={footer}>
      <div className="confirm">
        <p className="confirm__desc">{description}</p>
      </div>
    </ModalSheet>
  );
}

