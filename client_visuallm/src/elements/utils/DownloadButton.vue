<template>
<button @click="buttonClicked" class="download-button">{{ buttonText }}</button>
<div v-if="displayModal" ref="modal" class="modal">
  <div class="modal-content">
    <div v-html="modalText" class="wrapElement"></div>
    <div class="modal-button-wrapper">
      <div class="copy-message" v-if="displayCopyMessage">{{ copyMessage }}</div>
      <button class="download-button" @click.prevent="displayModal = false">Close</button>
      <button class="download-button" @click.prevent="copyToClickboard">Copy</button>
    </div>
  </div>
  <input style="display: none" type="textarea" ref="refForCopy" :value="copyText" readonly/>
</div>
<a ref="refForDownload" style="display: none"></a>
</template>
<script lang="ts" scoped>
import { defineComponent } from 'vue'
import { escapeHtml, turnNewlinesToBr } from '@/assets/stringMethods'
let component = defineComponent({
  props: {
    buttonText: {
      type: String,
      required: true
    },
    onlyModal: {
      type: Boolean,
      default: true, // set to false for legacy file download
    },
  },
  emits: ['downloadClicked'],
  data() {
    return {
      modalText: "",
      copyText: "",
      copyMessage: "",
      copyMessageTimeout: 5_000,
      displayCopyMessage: false,
      displayModal: false,
    }
  },
  methods: {
    buttonClicked() {
        this.$emit("downloadClicked")
    },
    displayCopySuccessMessage() {
      this.displayCopyMessage = true
      this.copyMessage = "Copied!"
      setTimeout(() => this.displayCopyMessage = false, this.copyMessageTimeout)
    },
    displayCopyFailureMessage(error: string) {
      this.displayCopyMessage = true
      this.copyMessage = `Copy failed! ${error}`
      setTimeout(() => this.displayCopyMessage = false, this.copyMessageTimeout)
    },
    copyToClickboard() {
      let textarea = this.$refs.refForCopy as HTMLElement
      textarea.focus()
      navigator.clipboard.writeText(this.copyText)
        .then(this.displayCopySuccessMessage.bind(this))
        .catch((error) => this.displayCopyFailureMessage.bind(this, error))
    },
    startDownloadOfFile(contents: string) {
      if (this.onlyModal) {
        this.modalText = turnNewlinesToBr(escapeHtml(contents))
        this.copyText = contents
        this.displayModal = true
      } else {
        this.download("file.txt", contents)
      }
    },
    download(filename: string, text: string) {
        let element = this.$refs.refForDownload as HTMLElement
        element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(text))
        element.setAttribute('download', filename)
        element.click()
    }
  }
})

export default component


</script>
<style scoped>

/* CSS */
.download-button {
    align-items: center;
    background-color: #FFFFFF;
    border: 1px solid rgba(0, 0, 0, 0.1);
    border-radius: .25rem;
    box-shadow: rgba(0, 0, 0, 0.364) 0 4px 12px;
    box-sizing: border-box;
    color: rgba(0, 0, 0, 0.85);
    cursor: pointer;
    display: inline-flex;
    font-family: sans-serif;
    font-weight: lighter;
    justify-content: center;
    margin: 5px;
    min-height: 2rem;
    padding-right: calc(1.0rem - 1px);
    padding-left: calc(1.0rem - 1px);
    position: relative;
    text-decoration: none;
    transition: all 250ms;
    user-select: none;
    -webkit-user-select: none;
    touch-action: manipulation;
    vertical-align: baseline;
    width: fit-content;
}

.download-button:hover,
.download-button:focus {
  border-color: rgba(0, 0, 0, 0.15);
  box-shadow: rgba(0, 0, 0, 0.371) 0 4px 12px;
  color: rgba(0, 0, 0, 0.65);
}

.download-button:hover {
  transform: translateY(-2px) scaleY(.95) scaleX(.95);
}

.download-button:active {
  background-color: #F0F0F1;
  border-color: rgba(0, 0, 0, 0.15);
  box-shadow: rgba(0, 0, 0, 0.06) 0 2px 4px;
  color: rgba(0, 0, 0, 0.65);
  transform: translateY(0);
}

.modal {
  display: block;
  position: fixed; /* Stay in place */
  z-index: 1; /* Sit on top */
  left: 0;
  top: 0;
  width: 100%; /* Full width */
  height: 100%; /* Full height */
  overflow: auto; /* Enable scroll if needed */
  background-color: rgb(0,0,0); /* Fallback color */
  background-color: rgba(0,0,0,0.4); /* Black w/ opacity */
}

/* Modal Content/Box */
.modal-content {
  background-color: #fefefe;
  margin: 15% auto; /* 15% from the top and centered */
  padding: 5px;
  padding-bottom: 20px;
  border: 1px solid #888;
  width: 80%; /* Could be more or less, depending on screen size */
}

.modal-button-wrapper {
  text-align: center;
}

.copy-message {
  color: rgb(209, 174, 174);
  font-weight:300;
  font-size:small;
}
</style>
