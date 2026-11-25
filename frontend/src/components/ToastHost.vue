<template>
  <div class="toast-host" aria-live="polite" aria-atomic="false">
    <div v-for="t in ui.toasts" :key="t.id" class="fs-toast" role="status">
      <CircleCheck v-if="t.type === 'success'" :size="18" class="flex-shrink-0 mt-1" style="color:#4ADE80" />
      <CircleAlert v-else-if="t.type === 'error'" :size="18" class="flex-shrink-0 mt-1" style="color:#FDA4AF" />
      <Info v-else :size="18" class="flex-shrink-0 mt-1" style="color:#A5B4FC" />
      <span class="flex-grow-1">{{ t.message }}</span>
      <button class="btn-close btn-close-white btn-sm flex-shrink-0" style="min-height:auto" aria-label="Dismiss" @click="ui.dismiss(t.id)" />
    </div>
  </div>
</template>

<script setup>
import { CircleAlert, CircleCheck, Info } from 'lucide-vue-next'
import { useUi } from '@/stores/ui'
const ui = useUi()
</script>
