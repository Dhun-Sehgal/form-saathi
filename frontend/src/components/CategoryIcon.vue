<template>
  <span class="icon-tile" :class="[`tint-${color || 'lavender'}`, { 'icon-tile-sm': small }]">
    <component :is="icon" aria-hidden="true" />
  </span>
</template>

<script setup>
import { computed } from 'vue'
import { Award, Briefcase, Building2, FilePenLine, GraduationCap, HandCoins, Landmark, Sparkles, Wrench } from 'lucide-vue-next'

const ICONS = { 'graduation-cap': GraduationCap, briefcase: Briefcase, award: Award, landmark: Landmark, 'file-pen-line': FilePenLine, 'building-2': Building2, wrench: Wrench, 'hand-coins': HandCoins, sparkles: Sparkles }
const props = defineProps({ name: String, color: String, small: Boolean })
const icon = computed(() => ICONS[props.name] || Sparkles)
</script>
