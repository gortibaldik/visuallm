<template>
<button @click="buttonClicked" class="download-button">{{ buttonText }}</button>
<a ref="refForDownload" style="display: none"></a>
</template>
<script lang="ts" scoped>
import { defineComponent } from 'vue'
let component = defineComponent({
  props: {
    buttonText: {
      type: String,
      required: true
    }
  },
  emits: ['downloadClicked'],
  computed: {
  },
  watch: {
  },
  data() {
    return {
      selected: '',
    }
  },
  methods: {
    buttonClicked() {
        this.$emit("downloadClicked")
    },
    startDownloadOfFile(contents: string) {
        this.download("file.txt", contents)
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
</style>
