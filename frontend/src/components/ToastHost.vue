<template>
  <div class="toast-host" aria-live="polite" aria-atomic="false">
    <div v-for="t in ui.toasts" :key="t.id" class="fs-toast" role="status">
      <CircleCheck v-if="t.type === 'success'" :size="18" class="flex-shrink-0 mt-1" style="color: var(--fs-success)" />
      <CircleAlert v-else-if="t.type === 'error'" :size="18" class="flex-shrink-0 mt-1" style="color: var(--fs-danger)" />
      <Info v-else :size="18" class="flex-shrink-0 mt-1" style="color: var(--fs-primary-600)" />
      <span class="flex-grow-1">{{ t.message }}</span>
      <button class="btn-close btn-sm flex-shrink-0" style="min-height:auto" aria-label="Dismiss" @click="ui.dismiss(t.id)" />
    </div>
  </div>
</template>

<script setup>
import { CircleAlert, CircleCheck, Info } from 'lucide-vue-next'
import { useUi } from '@/stores/ui'
const ui = useUi()
</script>
