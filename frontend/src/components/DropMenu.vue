<!-- Minimal accessible dropdown (no Bootstrap JS). -->
<template>
  <div ref="root" class="position-relative">
    <div @click="open = !open" @keydown.esc="open = false"><slot name="trigger" :open="open" /></div>
    <div v-if="open" class="dropdown-menu show" :class="align === 'end' ? 'dropdown-menu-end end-0' : ''" style="position:absolute; top: calc(100% + 6px); min-width: 220px" @click="open = false">
      <slot />
    </div>
  </div>
</template>

<script setup>
import { onBeforeUnmount, onMounted, ref } from 'vue'
defineProps({ align: { type: String, default: 'end' } })
const open = ref(false)
const root = ref(null)
const onDoc = (e) => { if (root.value && !root.value.contains(e.target)) open.value = false }
onMounted(() => document.addEventListener('click', onDoc))
onBeforeUnmount(() => document.removeEventListener('click', onDoc))
</script>
