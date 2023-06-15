/** Return the expected width of the number in pixels
 */
export function numberWidth(n: number): number {
  // TODO: find some better method of measuring number width
  let w = n.toString().length * 7 + 35
  return w
}

/** Export the expected width of the string in pixels
 */
export function stringWidth(s: string): number {
  let width = s.length
  width *= 8
  width += 30

  return width
}
