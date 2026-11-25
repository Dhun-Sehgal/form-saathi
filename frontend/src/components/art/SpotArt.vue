<!-- Small spot illustrations used across the site. Decorative (aria-hidden) unless a label is given. -->
<template>
  <svg viewBox="0 0 200 150" class="spot" :role="label ? 'img' : undefined" :aria-label="label || undefined" :aria-hidden="label ? undefined : 'true'">
    <ellipse cx="100" cy="80" rx="80" ry="62" :style="{ fill: bg }" />
    <circle cx="28" cy="36" r="5" style="fill: var(--ill-yellow)" opacity=".8" />
    <circle cx="176" cy="118" r="4" style="fill: var(--ill-pink)" opacity=".8" />

    <!-- 1. Create your profile -->
    <g v-if="name === 'profile'">
      <rect x="46" y="34" width="108" height="80" rx="14" style="fill: var(--ill-paper); stroke: var(--ill-line)" stroke-width="2" />
      <circle cx="76" cy="64" r="17" style="fill: var(--ill-pink-2)" />
      <circle cx="76" cy="59" r="6.5" style="fill: var(--ill-skin)" />
      <path d="M63 77 C63 67 89 67 89 77 Z" style="fill: var(--ill-violet)" />
      <rect x="102" y="54" width="38" height="7" rx="3.5" style="fill: var(--ill-violet-2)" />
      <rect x="102" y="67" width="26" height="7" rx="3.5" style="fill: var(--ill-mint-2)" />
      <rect x="62" y="94" width="78" height="7" rx="3.5" style="fill: var(--ill-line)" />
      <g transform="rotate(35 152 42)">
        <rect x="146" y="16" width="12" height="40" rx="3" style="fill: var(--ill-yellow)" />
        <rect x="146" y="12" width="12" height="9" rx="3" style="fill: var(--ill-pink)" />
        <path d="M146 56 H158 L152 66 Z" style="fill: var(--ill-ink-2)" />
      </g>
    </g>

    <!-- 2. Discover matches -->
    <g v-else-if="name === 'discover'">
      <rect x="40" y="50" width="86" height="62" rx="12" style="fill: var(--ill-paper)" opacity=".7" transform="rotate(-8 83 81)" />
      <rect x="54" y="38" width="88" height="64" rx="12" style="fill: var(--ill-paper); stroke: var(--ill-line)" stroke-width="2" />
      <circle cx="72" cy="58" r="8" style="fill: var(--ill-violet-2)" />
      <rect x="86" y="53" width="42" height="6" rx="3" style="fill: var(--ill-line)" />
      <rect x="86" y="64" width="28" height="6" rx="3" style="fill: var(--ill-mint-2)" />
      <rect x="66" y="82" width="62" height="6" rx="3" style="fill: var(--ill-line)" />
      <circle cx="136" cy="88" r="21" style="fill: var(--ill-paper); fill-opacity: .55; stroke: var(--ill-violet)" stroke-width="7" />
      <line x1="151" y1="103" x2="168" y2="120" style="stroke: var(--ill-ink-2)" stroke-width="10" stroke-linecap="round" />
      <path d="M128 88 l6 6 l10 -12" fill="none" style="stroke: var(--ill-mint)" stroke-width="4" stroke-linecap="round" stroke-linejoin="round" />
    </g>

    <!-- 3. Eligibility & documents checklist -->
    <g v-else-if="name === 'checklist'">
      <rect x="58" y="28" width="84" height="106" rx="14" style="fill: var(--ill-paper); stroke: var(--ill-line)" stroke-width="2" />
      <rect x="82" y="19" width="36" height="17" rx="7" style="fill: var(--ill-violet)" />
      <g v-for="(y, i) in [56, 80, 104]" :key="y">
        <circle cx="78" :cy="y" r="8.5" :style="i < 2 ? 'fill: var(--ill-mint)' : 'fill: none; stroke: var(--ill-violet-2)'" :stroke-width="i < 2 ? 0 : 2.5" />
        <path v-if="i < 2" :d="`M73.5 ${y} l3 3 l5.5 -6`" fill="none" style="stroke: var(--ill-paper)" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round" />
        <rect x="94" :y="y - 3.5" :width="i === 1 ? 26 : 36" height="7" rx="3.5" style="fill: var(--ill-line)" />
      </g>
      <g transform="translate(150 40) scale(.7)"><path d="M0 -12 C1.6 -3.2 3.2 -1.6 12 0 C3.2 1.6 1.6 3.2 0 12 C-1.6 3.2 -3.2 1.6 -12 0 C-3.2 -1.6 -1.6 -3.2 0 -12 Z" style="fill: var(--ill-yellow)" /></g>
    </g>

    <!-- 4. Apply & track -->
    <g v-else-if="name === 'track'">
      <path d="M36 120 C70 122 66 76 104 76 S148 44 160 34" fill="none" style="stroke: var(--ill-violet)" stroke-width="3" stroke-dasharray="6 7" stroke-linecap="round" />
      <line x1="36" y1="120" x2="36" y2="92" style="stroke: var(--ill-ink-2)" stroke-width="3" stroke-linecap="round" />
      <path d="M36 92 L56 98.5 L36 105 Z" style="fill: var(--ill-pink)" />
      <circle cx="70" cy="100" r="7" style="fill: var(--ill-mint)" />
      <circle cx="104" cy="76" r="7" style="fill: var(--ill-mint)" />
      <circle cx="136" cy="54" r="7" style="fill: var(--ill-paper); stroke: var(--ill-violet-2)" stroke-width="3" />
      <g transform="translate(150 36) rotate(-28)">
        <path d="M0 0 L32 -11 L16 11 Z" style="fill: var(--ill-violet)" />
        <path d="M16 11 L13 2 L32 -11 Z" style="fill: var(--ill-violet-2)" />
      </g>
    </g>

    <!-- Students -->
    <g v-else-if="name === 'student'">
      <path d="M100 112 C86 104 66 102 46 106 V66 C66 62 86 64 100 74 Z" style="fill: var(--ill-paper); stroke: var(--ill-line)" stroke-width="2" />
      <path d="M100 112 C114 104 134 102 154 106 V66 C134 62 114 64 100 74 Z" style="fill: var(--ill-paper); stroke: var(--ill-line)" stroke-width="2" />
      <rect x="56" y="78" width="32" height="5" rx="2.5" style="fill: var(--ill-violet-2)" />
      <rect x="56" y="88" width="24" height="5" rx="2.5" style="fill: var(--ill-line)" />
      <rect x="112" y="78" width="32" height="5" rx="2.5" style="fill: var(--ill-mint-2)" />
      <rect x="112" y="88" width="26" height="5" rx="2.5" style="fill: var(--ill-line)" />
      <path d="M78 46 V58 Q100 68 122 58 V46 L100 54 Z" style="fill: var(--ill-ink-2)" />
      <path d="M100 24 L142 39 L100 54 L58 39 Z" style="fill: var(--ill-ink)" />
      <path d="M100 39 L134 46 L134 64" fill="none" style="stroke: var(--ill-yellow)" stroke-width="3" stroke-linecap="round" />
      <circle cx="134" cy="66" r="4" style="fill: var(--ill-yellow)" />
    </g>

    <!-- Job seekers -->
    <g v-else-if="name === 'jobseeker'">
      <rect x="94" y="24" width="64" height="86" rx="10" style="fill: var(--ill-paper); stroke: var(--ill-line)" stroke-width="2" />
      <circle cx="112" cy="44" r="8" style="fill: var(--ill-pink-2)" />
      <rect x="126" y="40" width="22" height="5" rx="2.5" style="fill: var(--ill-violet-2)" />
      <rect x="106" y="60" width="42" height="5" rx="2.5" style="fill: var(--ill-line)" />
      <rect x="106" y="70" width="34" height="5" rx="2.5" style="fill: var(--ill-line)" />
      <path d="M72 66 V58 a6 6 0 0 1 6 -6 h16 a6 6 0 0 1 6 6 V66" fill="none" style="stroke: var(--ill-ink-2)" stroke-width="5" />
      <rect x="42" y="64" width="88" height="60" rx="12" style="fill: var(--ill-violet)" />
      <rect x="42" y="86" width="88" height="6" style="fill: var(--ill-ink-2)" opacity=".25" />
      <rect x="79" y="82" width="14" height="14" rx="4" style="fill: var(--ill-yellow)" />
    </g>

    <!-- Families & citizens (government schemes) -->
    <g v-else-if="name === 'family'">
      <path d="M40 76 L82 40 L124 76 Z" style="fill: var(--ill-pink)" />
      <rect x="50" y="74" width="64" height="50" rx="6" style="fill: var(--ill-paper); stroke: var(--ill-line)" stroke-width="2" />
      <rect x="74" y="96" width="16" height="28" rx="4" style="fill: var(--ill-violet-2)" />
      <rect x="57" y="84" width="12" height="12" rx="3" style="fill: var(--ill-sky-2)" />
      <rect x="95" y="84" width="12" height="12" rx="3" style="fill: var(--ill-sky-2)" />
      <g transform="rotate(8 146 90)">
        <rect x="122" y="58" width="50" height="64" rx="8" style="fill: var(--ill-paper); stroke: var(--ill-line)" stroke-width="2" />
        <rect x="130" y="70" width="32" height="5" rx="2.5" style="fill: var(--ill-violet-2)" />
        <rect x="130" y="80" width="24" height="5" rx="2.5" style="fill: var(--ill-line)" />
        <circle cx="156" cy="106" r="10" style="fill: var(--ill-yellow)" />
        <path d="M151.5 106 l3 3 l5 -6" fill="none" style="stroke: var(--ill-paper)" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" />
      </g>
      <path d="M82 26 c-5 -3.5 -8 -6 -8 -9 a3.8 3.8 0 0 1 8 -1.4 a3.8 3.8 0 0 1 8 1.4 c0 3 -3 5.5 -8 9 z" style="fill: var(--ill-pink)" />
    </g>

    <!-- Approved / celebration (auth panel, success states) -->
    <g v-else-if="name === 'celebrate'">
      <rect x="62" y="28" width="76" height="98" rx="12" style="fill: var(--ill-paper); stroke: var(--ill-line)" stroke-width="2" />
      <rect x="74" y="44" width="40" height="6" rx="3" style="fill: var(--ill-violet-2)" />
      <rect x="74" y="58" width="52" height="6" rx="3" style="fill: var(--ill-line)" />
      <rect x="74" y="70" width="44" height="6" rx="3" style="fill: var(--ill-line)" />
      <rect x="74" y="82" width="30" height="6" rx="3" style="fill: var(--ill-line)" />
      <circle cx="132" cy="108" r="22" style="fill: var(--ill-mint)" />
      <path d="M121 108.5 l7.5 7.5 l14 -15" fill="none" style="stroke: var(--ill-paper)" stroke-width="4.5" stroke-linecap="round" stroke-linejoin="round" />
      <g transform="rotate(-16 62 30)">
        <path d="M48 32 V40 Q62 46 76 40 V32 L62 37 Z" style="fill: var(--ill-ink-2)" />
        <path d="M62 18 L88 27 L62 36 L36 27 Z" style="fill: var(--ill-ink)" />
        <path d="M62 27 L84 31 L84 44" fill="none" style="stroke: var(--ill-yellow)" stroke-width="2.5" stroke-linecap="round" />
      </g>
      <rect x="152" y="40" width="8" height="8" rx="2" transform="rotate(20 156 44)" style="fill: var(--ill-yellow)" />
      <rect x="40" y="96" width="7" height="7" rx="2" transform="rotate(-25 43 99)" style="fill: var(--ill-pink)" />
      <rect x="160" y="74" width="6" height="12" rx="2" transform="rotate(35 163 80)" style="fill: var(--ill-violet)" />
      <circle cx="46" cy="70" r="4" style="fill: var(--ill-sky)" />
    </g>
  </svg>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({ name: { type: String, required: true }, label: String, tint: String })
const BG = { profile: 'var(--ill-violet-3)', discover: 'var(--ill-pink-2)', checklist: 'var(--ill-mint-2)', track: 'var(--ill-yellow-2)', student: 'var(--ill-violet-3)', jobseeker: 'var(--ill-sky-2)', family: 'var(--ill-mint-2)', celebrate: 'var(--ill-violet-3)' }
const bg = computed(() => props.tint || BG[props.name] || 'var(--ill-violet-3)')
</script>
