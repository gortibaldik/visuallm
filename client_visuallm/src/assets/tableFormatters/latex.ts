
/** Transform multiline string value to latex multirow statement
 */
function latexResolveMultilineValue(value: string) {
    let lines = value.split('\n')
    if (lines.length == 1) {
        return value
    }
    let lineWidths = Array(lines.length).fill(0)

    for (let i = 0; i < lines.length; i++) {
        lineWidths[i] = lines[i].length
    }

    let maxLineWidth = Math.max(...lineWidths)

    let result = `\\multirow{${lines.length}}{*}{\\parbox{${maxLineWidth / 2}em}{\\centering ${lines.join("\\\\")}}}`
    return result
}

/** Create latex representation of the code cell.
 *
 * Handle html <code> tags, and line breaks
 */
function latexSanitizeValue(value: string) {
    // replace <code> tags with \texttt
    const codeRegex = /<code>(.*?)<\/code>/g;
    let result = value.replace(codeRegex, '\\texttt{$1}')

    // replace < and >
    result = result.replace(/&lt;/g, '<');
    result = result.replace(/&gt;/g, '>');

    //replace newline tags with multirow
    const newlineTag = '<br \/>'
    const newlineRegex = new RegExp(newlineTag, 'g')
    result = result.replace(newlineRegex, '\n')

    if (result.includes('\n')) {
      result = latexResolveMultilineValue(result)
    }

    return result
}

/** When there is a value with newlines in the row, it is necessary to
 * add the corresponding number of empty rows to the table
 * @returns
 */
function latexResolveNewlines(sanitizedRows: string[][]) {
    let nCols = sanitizedRows[0].length
    let resultLines = [] as string[][]

    for (let i = 0; i < sanitizedRows.length; i++) {
      let isNewline = false
      let newlineIndex = -1
      for (let j = 0; j < nCols; j++) {
        if (sanitizedRows[i][j].includes("multirow")) {
          if (isNewline) {
            throw Error()
          }
          isNewline = true
          newlineIndex = j
        }
      }

      resultLines.push(sanitizedRows[i])
      if (!isNewline) {
        continue
      }

      let match = resultLines[i][newlineIndex].match(/\\multirow{(\d+)}/)
      if (match === null) {
        throw Error()
      }
      let nLines = parseInt(match[1], 10)

      for (let j = 1; j < nLines; j++) {
        resultLines.push(Array(nCols).fill(''))
      }
    }
    return resultLines
}

export function createTableLatexRepre(table: {headers: string[], rows: string[][]}) {
    let n_cols = table.headers.length
    let sanitizedRows = table.rows.map(innerList => innerList.map(latexSanitizeValue))
    sanitizedRows = latexResolveNewlines(sanitizedRows)
    let repre = `\\begin{center}
\\begin{tabular}{${Array(n_cols).fill('c').join(' ')}}
${table.headers.join(' & ')} \\\\
\\hline
${sanitizedRows.map(innerList => innerList.join(' & ')).join(' \\\\\n')}
\\end{tabular}
\\end{center}
`
    return repre
}
