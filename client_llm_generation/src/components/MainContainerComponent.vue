<script lang="ts" scoped>
import { defineComponent } from 'vue';
import type { PollUntilSuccessGET } from '@/assets/pollUntilSuccessLib';
import type { ProcessedContext } from '@/assets/formatter'
import DisplayPlainTextComponent from '@/components/DisplayPlainTextComponent.vue'
import DisplaySoftmaxComponent from '@/components/DisplaySoftmaxComponent.vue'
import DisplaySampleSelectorComponent from '@/components/DisplaySampleSelector.vue'
import DisplayLinksComponent from './DisplayLinksComponent.vue';
import { fetchDefault } from '@/assets/fetchPathsResolver';
import { reactiveStore } from '@/assets/reactiveData';

export default defineComponent({
  data() {
    return {
      contexts: {} as {[name: string]: ProcessedContext},
      reactiveStore,
      defaultPoll: undefined as PollUntilSuccessGET | undefined,
    };
  },
  inject: ['backendAddress'],
  async created() {
    await this.fetchInitDataFromServer()
  },
  unmounted() {
    this.defaultPoll?.clear()
  },
  components: {
    DisplayPlainTextComponent,
    DisplaySoftmaxComponent,
    DisplaySampleSelectorComponent,
    DisplayLinksComponent,
  },
  methods: {
    setUpContext(response: any) {
      this.$formatter.processResponse(
        response,
        this.reactiveStore,
        this.contexts
      )
    },
    async fetchInitDataFromServer() {
      
      await fetchDefault(
        this,
        this.backendAddress as string,
        "defaultPoll",
        this.setUpContext.bind(this)
      )
    }
  },
});
</script>

<template>
  <div class="horizontal rounded">
    <component v-for="(processedContext, name) in contexts"
      :is="processedContext.component" :name="processedContext.name"
    ></component>
  </div>
</template>
