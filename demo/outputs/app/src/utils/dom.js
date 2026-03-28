/**
 * @param {HTMLElement} el
 */
export function getFocusableElements(el) {
  const selector = [
    "a[href]",
    "button:not([disabled])",
    "textarea:not([disabled])",
    "input:not([disabled])",
    "select:not([disabled])",
    "[tabindex]:not([tabindex='-1'])",
  ].join(",");
  return /** @type {HTMLElement[]} */ (Array.from(el.querySelectorAll(selector))).filter(
    (node) => node.offsetParent !== null
  );
}

