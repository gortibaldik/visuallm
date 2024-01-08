function escapeRegExp(value: string): string {
  return value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'); // $& means the whole matched string
}

export function replaceAll(wholeString: string, oldValue: string, newValue: string): string {
  return wholeString.replace(new RegExp(escapeRegExp(oldValue), 'g'), newValue);
}

/** A string is sane if it doesn't contain any html except allowed tags.
 */
export function isSane(value: string) {
  let toBeReplaced = [
    "<br />",
    "<code>",
    "</code>",
    "<b>",
    "</b>",
    "<em>",
    "</em>"
  ]
  toBeReplaced = toBeReplaced.map(escapeRegExp)
  let checkedValue = value.replace(new RegExp(toBeReplaced.join("|"), 'g'), "")
  return !checkedValue.includes("<") && !checkedValue.includes(">")
}

export function escapeHtml(unsafe: string) {
  return unsafe
  .replace(/&/g, "&amp;")
  .replace(/</g, "&lt;")
  .replace(/>/g, "&gt;")
  .replace(/"/g, "&quot;")
  .replace(/'/g, "&#039;");
}

export function turnNewlinesToBr(text: string) {
  text = text.replace(/(?:\r\n|\r|\n)/g, '<br>')
  return text
}
