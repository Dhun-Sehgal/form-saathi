<!-- Split auth card: illustrated brand panel (desktop) + form. -->
<template>
  <div class="auth-split">
    <aside class="auth-art" aria-hidden="true">
      <h2 class="mb-2">{{ heading }}</h2>
      <p class="mb-4 auth-sub">{{ sub }}</p>
      <div class="position-relative mx-auto mb-4" style="max-width: 320px; width: 100%">
        <div class="art-card float"><SpotArt :name="art" /></div>
        <div class="phone-chip float-2 d-flex align-items-center gap-2" style="top: -14px; right: -18px; color: var(--fs-text)"><span class="icon-tile icon-tile-sm tint-mint"><CircleCheck /></span><span class="fw-bold small">You’re eligible!</span></div>
        <div class="phone-chip float-3 d-flex align-items-center gap-2" style="bottom: -16px; left: -18px; color: var(--fs-text)"><span class="icon-tile icon-tile-sm tint-peach"><CalendarClock /></span><span class="fw-bold small">3 days left</span></div>
      </div>
      <ul class="list-unstyled d-grid gap-2 mt-auto mb-0">
        <li v-for="p in points" :key="p" class="d-flex gap-2 align-items-start"><span class="auth-tick d-inline-grid flex-shrink-0 rounded-circle"><Check :size="14" /></span><span>{{ p }}</span></li>
      </ul>
    </aside>
    <div class="auth-form"><slot /></div>
  </div>
</template>

<script setup>
import { CalendarClock, Check, CircleCheck } from 'lucide-vue-next'
import SpotArt from '@/components/art/SpotArt.vue'

defineProps({
  heading: { type: String, default: 'Never miss an opportunity you deserve.' },
  sub: { type: String, default: 'Scholarships, internships, schemes and jobs — matched to you, explained simply.' },
  art: { type: String, default: 'celebrate' },
  points: { type: Array, default: () => ['Rule-by-rule eligibility checks', 'Document checklists for every application', 'Deadline reminders, in your language'] },
})
</script>
