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
