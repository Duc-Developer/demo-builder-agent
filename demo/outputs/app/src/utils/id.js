export function createId() {
  if (typeof crypto !== "undefined" && typeof crypto.randomUUID === "function") {
    return crypto.randomUUID();
  }
  // Fallback (not perfect, but ok for local-only MVP)
  return "id_" + Math.random().toString(16).slice(2) + "_" + Date.now().toString(16);
}

