<!-- Empty / error / loading states with a small friendly illustration. -->
<template>
  <div v-if="kind === 'loading'" class="row g-3">
    <div v-for="i in count" :key="i" :class="colClass">
      <div class="fs-card fs-card-pad">
        <div class="d-flex gap-3 mb-3"><div class="skeleton" style="width:40px;height:40px;border-radius:12px" /><div class="flex-grow-1"><div class="skeleton mb-2" style="height:12px;width:50%" /><div class="skeleton" style="height:12px;width:30%" /></div></div>
        <div class="skeleton mb-2" style="height:16px;width:85%" /><div class="skeleton mb-2" style="height:12px" /><div class="skeleton" style="height:12px;width:70%" />
      </div>
    </div>
  </div>
  <div v-else class="text-center py-5 px-3">
    <SpotArt v-if="kind !== 'error'" name="discover" class="empty-illus mb-2" />
    <svg v-else class="empty-illus mb-3" viewBox="0 0 120 100" aria-hidden="true">
      <ellipse cx="60" cy="90" rx="40" ry="6" fill="var(--fs-surface-2)" />
      <rect x="30" y="12" width="60" height="72" rx="10" :fill="kind === 'error' ? 'var(--fs-danger-bg)' : 'var(--fs-lavender)'" />
      <rect x="40" y="28" width="40" height="5" rx="2.5" fill="var(--fs-surface)" />
      <rect x="40" y="40" width="30" height="5" rx="2.5" fill="var(--fs-surface)" />
      <rect x="40" y="52" width="35" height="5" rx="2.5" fill="var(--fs-surface)" />
      <circle cx="86" cy="18" r="9" style="fill: var(--color-peach-500)" />
      <text x="86" y="22" text-anchor="middle" font-size="11" font-weight="700" style="fill: var(--ill-paper)">{{ kind === 'error' ? '!' : '?' }}</text>
    </svg>
    <h3 class="h5 fw-bold">{{ title || (kind === 'error' ? 'Something went wrong' : 'Nothing here yet') }}</h3>
    <p class="text-muted mx-auto" style="max-width: 420px">{{ message }}</p>
    <slot>
      <button v-if="kind === 'error'" class="btn btn-soft" @click="$emit('retry')"><RotateCcw :size="16" /> Try again</button>
    </slot>
  </div>
</template>

<script setup>
import { RotateCcw } from 'lucide-vue-next'
import SpotArt from '@/components/art/SpotArt.vue'
defineProps({ kind: { type: String, default: 'empty' }, title: String, message: String, count: { type: Number, default: 3 }, colClass: { type: String, default: 'col-md-6 col-xl-4' } })
defineEmits(['retry'])
</script>
