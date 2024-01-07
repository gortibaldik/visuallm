
/** Compute y coordinate at which the element should end after adding `requiredAdditionalHeight`.
 */
export function computeEndingYCoordinate(element: HTMLElement, requiredAdditionalHeight: number) {
    let rectangle = element.getBoundingClientRect()
    let magicHeightParam = 10

    return rectangle.y + rectangle.height + requiredAdditionalHeight + magicHeightParam
}
