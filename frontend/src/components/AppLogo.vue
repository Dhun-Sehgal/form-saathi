<template>
  <span class="d-inline-flex align-items-center gap-2 text-decoration-none" :aria-label="'FormSaathi'">
    <svg :width="size" :height="size" viewBox="0 0 64 64" aria-hidden="true">
      <rect width="64" height="64" rx="16" fill="#3730A3" />
      <path d="M20 14h17l9 9v25a4 4 0 0 1-4 4H20a4 4 0 0 1-4-4V18a4 4 0 0 1 4-4z" fill="#fff" />
      <path d="M37 14v6a3 3 0 0 0 3 3h6z" fill="#C7D2FE" />
      <rect x="22" y="30" width="18" height="3" rx="1.5" fill="#3730A3" />
      <rect x="22" y="37" width="12" height="3" rx="1.5" fill="#A5B4FC" />
      <path d="M47 8l1.9 4.1L53 14l-4.1 1.9L47 20l-1.9-4.1L41 14l4.1-1.9z" fill="#FB7185" />
    </svg>
    <span v-if="!iconOnly" class="font-display fw-bold" :style="{ fontSize: size * 0.58 + 'px', color: 'var(--fs-text)', letterSpacing: '-.02em' }">
      Form<span style="color: var(--fs-primary)">Saathi</span>
    </span>
  </span>
</template>

<script setup>
defineProps({ size: { type: Number, default: 34 }, iconOnly: Boolean })
</script>
