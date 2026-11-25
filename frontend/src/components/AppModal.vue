<template>
  <Teleport to="body">
    <div v-if="open" class="fs-backdrop" @mousedown.self="$emit('close')" @keydown.esc="$emit('close')">
      <div ref="panel" class="fs-modal" :class="{ wide }" role="dialog" aria-modal="true" :aria-labelledby="titleId" tabindex="-1">
        <div class="d-flex align-items-start justify-content-between gap-3 p-4 pb-2">
          <div>
            <h2 :id="titleId" class="h5 fw-bold mb-1">{{ title }}</h2>
            <p v-if="subtitle" class="text-muted small mb-0">{{ subtitle }}</p>
          </div>
          <button class="btn btn-ghost btn-icon" aria-label="Close" @click="$emit('close')"><X :size="20" /></button>
        </div>
        <div class="px-4 pb-4 pt-2"><slot /></div>
        <div v-if="$slots.footer" class="px-4 pb-4 d-flex gap-2 justify-content-end flex-wrap"><slot name="footer" /></div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { nextTick, ref, watch } from 'vue'
import { X } from 'lucide-vue-next'

const props = defineProps({ open: Boolean, title: String, subtitle: String, wide: Boolean })
defineEmits(['close'])
const panel = ref(null)
const titleId = 'm' + Math.random().toString(36).slice(2, 8)
watch(() => props.open, async (v) => {
  document.body.style.overflow = v ? 'hidden' : ''
  if (v) { await nextTick(); panel.value?.focus() }
})
</script>
