<template>
  <div class="wrapElement spacedTables">
    <div v-for="table, tableIndex in tables" class="table-wrapper">
      <div class="table-header">
        <h3 v-if="table.title != undefined" style="margin: 0">{{ table.title }}</h3>
        <DownloadButton v-if="table.is_latex_downloadable" buttonText="LaTEX" @download-clicked="downloadClicked(tableIndex)" ref="downloadButton"/>
      </div>
      <table class="table-style-0">
        <thead>
          <tr>
            <th v-for="val in table.headers">{{ val }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(row, r) in table.rows" :id="`${table.id}_${r}`" :class="{
            active: displayedLinksRowID == `${table.id}_${r}`
          }">
            <td v-for="col in row" v-html="col"></td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script lang="ts" scoped>
import { defineComponent } from 'vue'
import LeaderLine from 'leader-line-new'
import DownloadButton from './utils/DownloadButton.vue'
import { dataSharedInComponent, getSharedDataUniqueName } from '@/assets/reactiveData'
import type ElementRegistry from '@/assets/elementRegistry'
import { registerElementBase } from '@/assets/elementRegistry'
import { isSane } from '@/assets/stringMethods'
import {createTableLatexRepre } from '@/assets/tableFormatters/latex'

export type LoadedTable = {
  title: string
  id: string
  headers: string[]
  rows: string[][]
  is_latex_downloadable: boolean
}

/**
 * Structure holding all the information needed to display a link between two
 * HTML elements.
 */
export type LinkBetweenRows = {
  StartTable: string
  StartRow: number
  EndTable: string
  EndRow: number
  Importance: number
  Label: string
  Color: string
}

let component = defineComponent({
  props: {
    name: {
      type: String,
      required: true
    }
  },
  data() {
    return {
      initializeLinksTimeout: 400,
      areRowLinksDisplayed: {} as { [id: string]: boolean },
      displayedLinksRowID: undefined as string | undefined,
      linksFromRow: {} as { [id: string]: LeaderLine[] }
    }
  },
  components: {DownloadButton},
  computed: {
    links(): LinkBetweenRows[] {
      return dataSharedInComponent[getSharedDataUniqueName(this.name, 'links')]
    },
    tables(): LoadedTable[] {
      let tables = dataSharedInComponent[getSharedDataUniqueName(this.name, 'loadedTables')] as LoadedTable[]
      for (const table of tables) {
        for (const row of table.rows) {
          for (let i = 0; i < row.length; i++) {
            if (!isSane(row[i])) {
              throw Error("Invalid value arrived from backend")
            }
          }
        }
      }
      return tables
    }
  },
  watch: {
    tables(newValue: LoadedTable[]) {
      this.updateEverything(newValue)
    },
    links(newValue: LinkBetweenRows[]) {
      this.updateEverything(this.tables)
    }
  },
  mounted() {
    this.updateEverything(this.tables)
  },
  unmounted() {
    this.unregisterLinks()
  },
  methods: {
    // TODO: move it to some "Latex utils"
    // create a test for the download
    downloadClicked(tableIndex: number) {
      let downloadButtons = this.$refs.downloadButton as (typeof DownloadButton)[]
      let downloadButton = downloadButtons[tableIndex]
      let fileContents = createTableLatexRepre(this.tables[tableIndex])
      downloadButton.startDownloadOfFile(fileContents)
    },
    table_title_to_id(title: string) {
      return title.replace(/\s/g, '')
    },
    /** Update titles of tables and register all the links between tables.
     */
    updateEverything(tables: LoadedTable[]) {
      if (tables !== undefined) {
        for (let t of tables) {
          t.id = this.table_title_to_id(t.title)
        }
        setTimeout(this.registerLinks.bind(this), this.initializeLinksTimeout)
      }
    },
    /** Remove all the registered links from all the element component
     * structures.
     */
    unregisterLinks() {
      for (let key in this.linksFromRow) {
        let lines = this.linksFromRow[key]
        for (let i = 0; i < lines.length; i++) {
          let line = lines[i]
          line.remove()
        }
      }
      this.linksFromRow = {}
      if (this.displayedLinksRowID !== undefined) {
        this.areRowLinksDisplayed[this.displayedLinksRowID] = false
        this.displayedLinksRowID = undefined
      }
    },
    /** Create a displayable link between elStart and elEnd. The link
     * display properties are defined in the link object.
     */
    createLink(link: LinkBetweenRows, elStart: HTMLElement, elEnd: HTMLElement) {
      return new LeaderLine(elStart, elEnd, {
        startSocket: 'right',
        endSocket: 'right',
        path: 'grid',
        size: link.Importance,
        startSocketGravity: [150, 0],
        startPlug: 'square',
        // endPlugSize is by default multiplied by
        // link.Importance, to set it to constant size
        // one must divide endPlugSize by link.Importance
        endPlugSize: 4 / link.Importance,
        endLabel: LeaderLine.captionLabel(link.Label, {
          offset: [25, -25]
        }),
        hide: true,
        color: link.Color
      })
    },
    /** Each displayable link should be in the following structures belonging
     * to the element component:
     * - `linksFromRow`: `map<rowID, LeaderLine>` of all displayable links from
     *  the row it is used to hide/show links that shouldn't/should be
     * displayed at the moment and to remove links at the unmount time
     * - `areRowLinksDisplayed`: `map<rowID, boolean>` whether the links from
     *  row are currently displayed
     * - event listener for `mouseover` event, which should display all links
     *  starting at the row when mouse hovers above it
     */
    appendLinkToStructures(startID: string, elStart: HTMLElement, displayableLink: LeaderLine) {
      if (!(startID in this.linksFromRow)) {
        this.linksFromRow[startID] = []
        this.areRowLinksDisplayed[startID] = false
        elStart.addEventListener('mouseover', this.displayLinksStartingAtRowID.bind(this, startID))
      }
      this.linksFromRow[startID].push(displayableLink)
    },
    /** Register all the links, and create event listeners for display on
     * hover
     */
    registerLinks() {
      let links = this.links
      if (links == undefined) {
        return
      }
      // remove all links that have been registered, so that only new
      // links are to be displayed
      this.unregisterLinks()
      for (let i = 0; i < links.length; i++) {
        let link = links[i]

        let startID = `${this.table_title_to_id(link.StartTable)}_${link.StartRow}`
        let endID = `${this.table_title_to_id(link.EndTable)}_${link.EndRow}`

        let elStart = document.getElementById(startID)
        let elEnd = document.getElementById(endID)

        if (elStart != null && elEnd != null) {
          const displayableLink = this.createLink(link, elStart, elEnd)
          this.appendLinkToStructures(startID, elStart, displayableLink)
        }
      }
    },
    /** Method used to display all links starting at `rowID`. Triggered on
     * hover.
     *
     * @param rowID id of the row which will be highlighted and links
     *  from it will be displayed
     */
    displayLinksStartingAtRowID(rowID: string) {
      // if the links are already displayed, ignore
      if (this.areRowLinksDisplayed[rowID]) {
        return
      }

      // if there isn't anything to display, ignore
      let linksToBeDisplayed = this.linksFromRow[rowID]
      if (linksToBeDisplayed == undefined) {
        return
      }

      // if something else was displayed, turn it off
      if (this.displayedLinksRowID != undefined) {
        let currentlyVisibleLinks = this.linksFromRow[this.displayedLinksRowID]
        if (currentlyVisibleLinks !== undefined) {
          for (let i = 0; i < currentlyVisibleLinks.length; i++) {
            currentlyVisibleLinks[i].hide('none')
          }
        }
        this.areRowLinksDisplayed[this.displayedLinksRowID] = false
      }

      // display
      this.displayedLinksRowID = rowID
      this.areRowLinksDisplayed[rowID] = true
      for (let i = 0; i < linksToBeDisplayed.length; i++) {
        linksToBeDisplayed[i].show('draw', { duration: 500 })
      }
    }
  }
})

export default component

let FEBEMapping: { [key: string]: string } = {
  "tables": "loadedTables",
  "links": "links"
}

export function registerElement(elementRegistry: ElementRegistry) {
  registerElementBase(elementRegistry, "connected_tables", "Tables", FEBEMapping)
}
</script>

<style scoped>

.table-header {
  display: flex;
  align-items: center;
}

.table-style-0 td+td {
  border-left: 0.5px solid rgb(106, 106, 106);
}

.table-wrapper h3 {
  text-align: center;
  margin-top: 0px;
}

.table-wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
  flex-direction: column;
  width: fit-content;
  max-width: 100%;
  background-color: rgba(0, 0, 0, 0.127);
  border-style: dashed;
  border-width: 1px;
  padding: 5px;
  border-radius: 5px;
  box-shadow: 0px 35px 50px rgba(0, 0, 0, 0.2);
}

.table-style-0 {
  border-radius: 5px;
  font-size: 12px;
  font-weight: normal;
  border-collapse: collapse;
  width: 100%;
  background-color: white;
  table-layout: auto;
}

.table-style-0 td,
.table-style-0 th {
  text-align: left;
  padding: 8px;
}

.table-style-0 td {
  font-size: 12px;
}

.table-style-0 thead th {
  color: #ffffff;
  background: #7c7c7c;
  padding-right: 10px;
  padding-left: 10px;
}

.table-style-0 thead th:nth-child(odd) {
  color: #ffffff;
  background: #6d6d6d;
  padding-right: 10px;
  padding-left: 10px;
}

.table-style-0 tr:nth-child(even) {
  background: #efeeee;
  padding-right: 10px;
  padding-left: 10px;
}

/* .table-style-0 td {
  display: inline-block
} */

.table-style-0 .active {
  background: #fbd0d0 !important;
}

.spacedTables {
  display: flex;
  flex-direction: row;
  row-gap: 5px;
  align-items: center;
  justify-content: center;
  flex-wrap: wrap;
  column-gap: 5em;
}
</style>
