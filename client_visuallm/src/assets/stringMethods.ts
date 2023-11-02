function escapeRegExp(value: string): string {
  return value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'); // $& means the whole matched string
}

export function replaceAll(wholeString: string, oldValue: string, newValue: string): string {
  return wholeString.replace(new RegExp(escapeRegExp(oldValue), 'g'), newValue);
}
