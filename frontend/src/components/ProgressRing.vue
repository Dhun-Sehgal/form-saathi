<template>
  <svg :width="size" :height="size" :viewBox="`0 0 ${size} ${size}`" role="img" :aria-label="`${value}% complete`">
    <defs><linearGradient :id="gid" x1="0" y1="0" x2="1" y2="1"><stop offset="0" style="stop-color: var(--fs-primary)" /><stop offset="1" style="stop-color: var(--fs-accent)" /></linearGradient></defs>
    <circle :cx="c" :cy="c" :r="r" fill="none" stroke="var(--fs-surface-2)" :stroke-width="stroke" />
    <circle :cx="c" :cy="c" :r="r" fill="none" :stroke="color || `url(#${gid})`" :stroke-width="stroke" stroke-linecap="round"
            :stroke-dasharray="len" :stroke-dashoffset="len * (1 - value / 100)" :transform="`rotate(-90 ${c} ${c})`"
            style="transition: stroke-dashoffset .6s var(--fs-ease)" />
    <text :x="c" :y="c + 6" text-anchor="middle" font-weight="800" :font-size="size * 0.24" fill="var(--fs-text)" style="font-family: var(--font-sans)">{{ value }}%</text>
  </svg>
</template>

<script setup>
import { computed } from 'vue'
const props = defineProps({ value: { type: Number, default: 0 }, size: { type: Number, default: 88 }, stroke: { type: Number, default: 9 }, color: { type: String, default: '' } })
const gid = 'pr' + Math.random().toString(36).slice(2, 8)
const c = computed(() => props.size / 2)
const r = computed(() => props.size / 2 - props.stroke / 2 - 1)
const len = computed(() => 2 * Math.PI * r.value)
</script>
