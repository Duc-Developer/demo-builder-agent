import React, { useMemo, useRef, useState } from "react";
import { TITLE_MAX_LENGTH } from "../todo/constants.js";

function validateTitle(title) {
  const trimmed = title.trim();
  if (!trimmed) return { ok: false, error: "Vui lòng nhập công việc", value: "" };
  if (trimmed.length > TITLE_MAX_LENGTH)
    return { ok: false, error: `Tiêu đề tối đa ${TITLE_MAX_LENGTH} ký tự`, value: trimmed };
  return { ok: true, error: "", value: trimmed };
}

export default function TodoInput({ onAdd }) {
  const [value, setValue] = useState("");
  const [error, setError] = useState("");
  const inputRef = useRef(null);

  const remainingChars = useMemo(() => TITLE_MAX_LENGTH - value.trim().length, [value]);

  function submit() {
    const res = validateTitle(value);
    if (!res.ok) {
      setError(res.error);
      return;
    }
    onAdd(res.value);
    setValue("");
    setError("");
    // keep focus for rapid entry
    inputRef.current?.focus();
  }

  return (
    <div>
      <div className="row">
        <input
          ref={inputRef}
          className="input"
          type="text"
          value={value}
          placeholder="Thêm việc cần làm…"
          aria-label="Thêm việc cần làm"
          maxLength={TITLE_MAX_LENGTH + 30}
          onChange={(e) => {
            setValue(e.target.value);
            if (error) setError("");
          }}
          onKeyDown={(e) => {
            if (e.key === "Enter") {
              e.preventDefault();
              submit();
            }
          }}
        />
        <button className="btn primary" type="button" onClick={submit} disabled={value.trim().length === 0}>
          Thêm
        </button>
      </div>

      <div className="row" style={{ justifyContent: "space-between", marginTop: 8 }}>
        <div className="small" aria-live="polite">
          {value.trim().length > 0 ? `Còn ${Math.max(0, remainingChars)} ký tự` : " "}
        </div>
        <div className="small">{value.trim().length > TITLE_MAX_LENGTH ? "Vượt giới hạn" : " "}</div>
      </div>

      {error ? (
        <div className="error" role="alert">
          {error}
        </div>
      ) : null}
    </div>
  );
}

