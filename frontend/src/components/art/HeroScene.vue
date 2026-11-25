<!-- Hero illustration: a student using FormSaathi, surrounded by the things it helps with.
     Pure SVG, coloured through CSS variables so it adapts to dark mode. -->
<template>
  <svg viewBox="0 0 600 520" role="img" aria-labelledby="hs-title" class="w-100 h-auto d-block" style="font-family: var(--font-sans)">
    <title id="hs-title">Illustration: a student using FormSaathi on a laptop, with a scholarship match, an eligibility check, a deadline reminder and a document checklist floating around her.</title>
    <defs>
      <linearGradient id="hs-blob" x1="0" y1="0" x2="1" y2="1">
        <stop offset="0" style="stop-color: var(--ill-violet-3)" />
        <stop offset="1" style="stop-color: var(--ill-pink-2)" />
      </linearGradient>
      <linearGradient id="hs-logo" x1="0" y1="0" x2="1" y2="1">
        <stop offset="0" stop-color="#7c68ee" /><stop offset="1" stop-color="#ec7f58" />
      </linearGradient>
      <filter id="hs-shadow" x="-30%" y="-30%" width="160%" height="170%">
        <feDropShadow dx="0" dy="12" stdDeviation="12" flood-color="#211f2e" flood-opacity=".14" />
      </filter>
    </defs>

    <!-- backdrop -->
    <circle cx="318" cy="268" r="212" fill="url(#hs-blob)" />
    <circle cx="318" cy="268" r="236" fill="none" style="stroke: var(--ill-violet-2)" stroke-width="2" stroke-dasharray="2 12" stroke-linecap="round" />
    <circle cx="534" cy="126" r="12" style="fill: var(--ill-yellow-2)" />
    <circle cx="92" cy="438" r="9" style="fill: var(--ill-mint-2)" />
    <circle cx="566" cy="352" r="6" style="fill: var(--ill-pink)" />
    <circle cx="74" cy="160" r="5" style="fill: var(--ill-violet-2)" />

    <!-- desk -->
    <ellipse cx="318" cy="472" rx="236" ry="14" style="fill: var(--ill-violet)" opacity=".12" />
    <rect x="86" y="436" width="464" height="22" rx="11" style="fill: var(--ill-violet-2)" />

    <!-- student -->
    <circle cx="318" cy="130" r="24" style="fill: var(--ill-ink)" />
    <rect x="303" y="146" width="30" height="8" rx="4" style="fill: var(--ill-pink)" />
    <circle cx="318" cy="200" r="58" style="fill: var(--ill-ink)" />
    <rect x="303" y="244" width="30" height="40" rx="11" style="fill: var(--ill-skin-2)" />
    <path d="M212 440 C212 340 250 292 318 292 C386 292 424 340 424 440 Z" style="fill: var(--ill-violet)" />
    <path d="M292 293 Q318 334 344 293 Z" style="fill: var(--ill-paper)" />
    <circle cx="272" cy="212" r="10" style="fill: var(--ill-skin)" />
    <circle cx="364" cy="212" r="10" style="fill: var(--ill-skin)" />
    <circle cx="271" cy="226" r="3.5" style="fill: var(--ill-yellow)" />
    <circle cx="365" cy="226" r="3.5" style="fill: var(--ill-yellow)" />
    <circle cx="318" cy="206" r="46" style="fill: var(--ill-skin)" />
    <path d="M272 204 C268 166 294 150 320 150 C348 150 370 168 365 202 C352 182 334 174 316 173 C302 180 286 190 272 204 Z" style="fill: var(--ill-ink)" />
    <circle cx="318" cy="193" r="2.3" style="fill: var(--ill-pink)" />
    <ellipse cx="302" cy="214" rx="4" ry="5.2" style="fill: var(--ill-ink)" />
    <ellipse cx="334" cy="214" rx="4" ry="5.2" style="fill: var(--ill-ink)" />
    <circle cx="303.4" cy="212.2" r="1.4" fill="#fff" />
    <circle cx="335.4" cy="212.2" r="1.4" fill="#fff" />
    <ellipse cx="290" cy="229" rx="8" ry="4.5" style="fill: var(--ill-pink)" opacity=".55" />
    <ellipse cx="346" cy="229" rx="8" ry="4.5" style="fill: var(--ill-pink)" opacity=".55" />
    <path d="M307 232 Q318 243 329 232" fill="none" style="stroke: var(--ill-ink)" stroke-width="3.2" stroke-linecap="round" />

    <!-- laptop (back view, FormSaathi logo) -->
    <rect x="208" y="318" width="220" height="118" rx="16" style="fill: var(--ill-paper); stroke: var(--ill-line)" stroke-width="3" />
    <rect x="298" y="357" width="40" height="40" rx="11" fill="url(#hs-logo)" />
    <path d="M311 365 h9 l7 7 v15 a2.5 2.5 0 0 1 -2.5 2.5 h-13.5 a2.5 2.5 0 0 1 -2.5 -2.5 v-19.5 a2.5 2.5 0 0 1 2.5 -2.5 z" fill="#fff" />
    <rect x="312.5" y="378" width="10" height="2.4" rx="1.2" fill="#7c68ee" />
    <rect x="312.5" y="383" width="7" height="2.4" rx="1.2" fill="#ec7f58" />
    <path d="M190 432 H446 L436 446 H200 Z" style="fill: var(--ill-violet)" />

    <!-- plant -->
    <ellipse cx="146" cy="374" rx="11" ry="26" transform="rotate(-28 146 374)" style="fill: var(--ill-mint)" />
    <ellipse cx="172" cy="372" rx="11" ry="27" transform="rotate(24 172 372)" style="fill: var(--ill-mint)" opacity=".8" />
    <ellipse cx="159" cy="360" rx="10" ry="30" style="fill: var(--ill-mint)" />
    <path d="M134 398 H184 L177 436 H141 Z" style="fill: var(--ill-yellow)" />
    <rect x="130" y="392" width="58" height="12" rx="6" style="fill: var(--ill-yellow)" />
    <path d="M159 426 c-6 -4 -9 -7 -9 -10.5 a4.3 4.3 0 0 1 9 -1.6 a4.3 4.3 0 0 1 9 1.6 c0 3.5 -3 6.5 -9 10.5 z" style="fill: var(--ill-pink)" />

    <!-- books + graduation cap -->
    <rect x="444" y="418" width="96" height="18" rx="5" style="fill: var(--ill-sky)" />
    <rect x="452" y="401" width="82" height="18" rx="5" style="fill: var(--ill-pink)" />
    <rect x="440" y="384" width="90" height="18" rx="5" style="fill: var(--ill-yellow)" />
    <rect x="452" y="424" width="70" height="3" rx="1.5" fill="#fff" opacity=".7" />
    <rect x="460" y="407" width="58" height="3" rx="1.5" fill="#fff" opacity=".7" />
    <rect x="448" y="390" width="66" height="3" rx="1.5" fill="#fff" opacity=".7" />
    <path d="M459 366 V382 Q485 394 511 382 V366 L485 375 Z" style="fill: var(--ill-ink-2)" />
    <path d="M485 344 L532 360 L485 376 L438 360 Z" style="fill: var(--ill-ink)" />
    <path d="M485 360 L520 368 L520 390" fill="none" style="stroke: var(--ill-yellow)" stroke-width="3" stroke-linecap="round" />
    <circle cx="520" cy="393" r="4.5" style="fill: var(--ill-yellow)" />
    <circle cx="485" cy="360" r="3" style="fill: var(--ill-yellow)" />

    <!-- paper plane trail -->
    <path d="M228 118 C258 72 302 62 346 82" fill="none" style="stroke: var(--ill-violet-2)" stroke-width="2.5" stroke-dasharray="5 7" stroke-linecap="round" />
    <g transform="translate(350 76) rotate(12)">
      <path d="M0 0 L28 -10 L14 10 Z" style="fill: var(--ill-violet)" />
      <path d="M14 10 L11 2 L28 -10 Z" style="fill: var(--ill-violet-2)" />
    </g>

    <!-- floating card: scholarship match -->
    <g class="float">
      <g transform="translate(26 64)">
        <rect width="202" height="74" rx="18" style="fill: var(--ill-paper)" filter="url(#hs-shadow)" />
        <circle cx="37" cy="37" r="21" style="fill: var(--ill-violet-3)" />
        <path d="M37 27 L52 33.5 L37 40 L22 33.5 Z" style="fill: var(--ill-violet)" />
        <path d="M28 37 v6 q9 5.5 18 0 v-6 l-9 3.8 z" style="fill: var(--ill-violet)" />
        <text x="68" y="31" font-size="12" font-weight="700" style="fill: var(--ill-muted)">Scholarship match</text>
        <text x="68" y="54" font-size="17" font-weight="800" style="fill: var(--ill-text)">₹12,000 / year</text>
      </g>
    </g>

    <!-- floating pill: eligible -->
    <g class="float-2">
      <g transform="translate(396 50)">
        <rect width="184" height="56" rx="28" style="fill: var(--ill-paper)" filter="url(#hs-shadow)" />
        <circle cx="28" cy="28" r="18" style="fill: var(--ill-mint)" />
        <path d="M20 28.5 l5.5 5.5 l10.5 -11" fill="none" style="stroke: var(--ill-paper)" stroke-width="3.6" stroke-linecap="round" stroke-linejoin="round" />
        <text x="54" y="34" font-size="15" font-weight="800" style="fill: var(--ink-mint)">You’re eligible!</text>
      </g>
    </g>

    <!-- floating card: deadline -->
    <g class="float-3">
      <g transform="translate(462 176)">
        <rect width="116" height="118" rx="20" style="fill: var(--ill-paper)" filter="url(#hs-shadow)" />
        <path d="M0 20 a20 20 0 0 1 20 -20 h76 a20 20 0 0 1 20 20 v14 h-116 z" style="fill: var(--ill-pink-2)" />
        <rect x="32" y="-7" width="7" height="16" rx="3.5" style="fill: var(--ill-ink-2)" />
        <rect x="77" y="-7" width="7" height="16" rx="3.5" style="fill: var(--ill-ink-2)" />
        <text x="58" y="25" text-anchor="middle" font-size="11" font-weight="800" letter-spacing="1.5" style="fill: var(--ink-peach)">DEADLINE</text>
        <text x="58" y="78" text-anchor="middle" font-size="38" font-weight="800" style="fill: var(--ill-text)">12</text>
        <text x="58" y="101" text-anchor="middle" font-size="12" font-weight="800" style="fill: var(--ink-peach)">3 days left</text>
      </g>
    </g>

    <!-- floating card: documents checklist -->
    <g class="float-2">
      <g transform="translate(18 196)">
        <rect width="202" height="128" rx="20" style="fill: var(--ill-paper)" filter="url(#hs-shadow)" />
        <text x="18" y="31" font-size="13.5" font-weight="800" style="fill: var(--ill-text)">Documents</text>
        <text x="184" y="31" text-anchor="end" font-size="12" font-weight="800" style="fill: var(--ill-violet)">2 / 3 ready</text>
        <g v-for="(row, i) in rows" :key="row.label" :transform="`translate(18 ${46 + i * 26})`">
          <rect width="18" height="18" rx="6" :style="row.done ? 'fill: var(--ill-mint)' : 'fill: none; stroke: var(--ill-violet-2)'" :stroke-width="row.done ? 0 : 2" />
          <path v-if="row.done" d="M4.5 9.5 l3.2 3.2 l6 -6.5" fill="none" style="stroke: var(--ill-paper)" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round" />
          <text x="28" y="14" font-size="12.5" font-weight="600" style="fill: var(--ill-muted)">{{ row.label }}</text>
        </g>
      </g>
    </g>

    <!-- sparkles -->
    <g v-for="(s, i) in sparkles" :key="i" :transform="`translate(${s.x} ${s.y}) scale(${s.s})`">
      <path class="twinkle" :style="{ animationDelay: `${i * -0.8}s`, fill: s.c }" d="M0 -12 C1.6 -3.2 3.2 -1.6 12 0 C3.2 1.6 1.6 3.2 0 12 C-1.6 3.2 -3.2 1.6 -12 0 C-3.2 -1.6 -1.6 -3.2 0 -12 Z" />
    </g>
  </svg>
</template>

<script setup>
const rows = [
  { label: 'Aadhaar card', done: true },
  { label: 'Marksheet', done: true },
  { label: 'Income certificate', done: false },
]
const sparkles = [
  { x: 246, y: 176, s: 0.9, c: 'var(--ill-yellow)' },
  { x: 432, y: 150, s: 0.6, c: 'var(--ill-pink)' },
  { x: 566, y: 300, s: 0.7, c: 'var(--ill-violet)' },
  { x: 60, y: 368, s: 0.55, c: 'var(--ill-yellow)' },
  { x: 410, y: 30, s: 0.5, c: 'var(--ill-mint)' },
]
</script>
