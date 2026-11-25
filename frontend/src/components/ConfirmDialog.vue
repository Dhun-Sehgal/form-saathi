<template>
  <AppModal :open="!!ui.confirmState" :title="ui.confirmState?.title || 'Are you sure?'" @close="ui.closeConfirm(false)">
    <p class="mb-0 text-muted">{{ ui.confirmState?.message }}</p>
    <template #footer>
      <button class="btn btn-ghost" @click="ui.closeConfirm(false)">Cancel</button>
      <button class="btn" :class="ui.confirmState?.danger ? 'btn-danger' : 'btn-primary'" @click="ui.closeConfirm(true)">
        {{ ui.confirmState?.confirmText }}
      </button>
    </template>
  </AppModal>
</template>

<script setup>
import AppModal from './AppModal.vue'
import { useUi } from '@/stores/ui'
const ui = useUi()
</script>
