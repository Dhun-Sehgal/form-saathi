<template>
  <span class="d-inline-flex align-items-center gap-2 text-decoration-none" :aria-label="'FormSaathi'">
    <svg :width="size" :height="size" viewBox="0 0 64 64" aria-hidden="true">
      <defs>
        <linearGradient :id="gid" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0" stop-color="#7458F8" /><stop offset=".55" stop-color="#A86BFF" /><stop offset="1" stop-color="#FF8FB1" />
        </linearGradient>
      </defs>
      <rect width="64" height="64" rx="18" :fill="`url(#${gid})`" />
      <path d="M21 14h15.5l8.5 8.5V46a4.5 4.5 0 0 1-4.5 4.5H21a4.5 4.5 0 0 1-4.5-4.5V18.5A4.5 4.5 0 0 1 21 14z" fill="#fff" />
      <path d="M36.5 14v6.5a2 2 0 0 0 2 2H45z" fill="#E4DBFF" />
      <path d="M23.5 35.5l4.8 4.8 9.2-10" fill="none" stroke="#7458F8" stroke-width="3.6" stroke-linecap="round" stroke-linejoin="round" />
      <path d="M50 6l1.8 3.9L55.7 11.7 51.8 13.5 50 17.4 48.2 13.5 44.3 11.7 48.2 9.9z" fill="#FFC94D" />
    </svg>
    <span v-if="!iconOnly" class="font-display fw-bold" :style="{ fontSize: size * 0.6 + 'px', color: 'var(--fs-text)', letterSpacing: '-.03em' }">
      Form<span class="text-grad">Saathi</span>
    </span>
  </span>
</template>

<script setup>
defineProps({ size: { type: Number, default: 34 }, iconOnly: Boolean })
const gid = 'lg' + Math.random().toString(36).slice(2, 8)
</script>
