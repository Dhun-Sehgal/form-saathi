<template>
  <div>
    <div class="d-flex flex-wrap align-items-center gap-2 mb-4">
      <div class="me-auto"><h1 class="page-title">Calendar</h1><p class="page-sub">Deadlines and dates for saved and tracked opportunities, plus your reminders.</p></div>
      <button class="btn btn-soft btn-icon" aria-label="Previous month" @click="shift(-1)"><ChevronLeft :size="18" /></button>
      <div class="fw-bold text-center" style="min-width: 150px">{{ monthLabel }}</div>
      <button class="btn btn-soft btn-icon" aria-label="Next month" @click="shift(1)"><ChevronRight :size="18" /></button>
      <button class="btn btn-ghost btn-sm" @click="goToday">Today</button>
    </div>

    <div class="d-flex flex-wrap gap-3 small mb-3" aria-label="Legend">
      <span v-for="(c, k) in TYPE" :key="k" class="d-flex align-items-center gap-1"><span class="cal-dot" :style="{ background: c.color }" /> {{ c.label }}</span>
    </div>

    <StateBlock v-if="error" kind="error" :message="error" @retry="load" />
    <div v-else class="cal-grid" :style="{ opacity: loading ? .6 : 1 }">
      <div v-for="d in ['Mon','Tue','Wed','Thu','Fri','Sat','Sun']" :key="d" class="cal-head">{{ d }}</div>
      <div v-for="cell in cells" :key="cell.iso" class="cal-cell" :class="{ other: !cell.inMonth, today: cell.iso === todayIso }" @click="selected = cell.iso">
        <span class="cal-day">{{ cell.day }}</span>
        <div class="d-none d-md-block">
          <router-link v-for="(e, i) in (eventsByDay[cell.iso] || []).slice(0, 3)" :key="i" :to="e.link || '/app/calendar'" class="cal-event text-decoration-none" :style="{ background: TYPE[e.type].bg, color: TYPE[e.type].ink }" :title="e.title">{{ e.title }}</router-link>
          <div v-if="(eventsByDay[cell.iso] || []).length > 3" class="small text-muted">+{{ eventsByDay[cell.iso].length - 3 }} more</div>
        </div>
        <div class="d-md-none mt-1"><span v-for="(e, i) in (eventsByDay[cell.iso] || []).slice(0, 4)" :key="i" class="cal-dot" :style="{ background: TYPE[e.type].color }" /></div>
      </div>
    </div>

    <section class="fs-card fs-card-pad mt-4">
      <h2 class="h6 fw-bold mb-3">{{ selected ? formatDate(selected, { weekday: 'long', day: 'numeric', month: 'long' }) : 'This month' }}</h2>
      <ul v-if="listed.length" class="list-unstyled mb-0 d-grid gap-2">
        <li v-for="(e, i) in listed" :key="i" class="d-flex gap-2 align-items-center">
          <span class="cal-dot flex-shrink-0" :style="{ background: TYPE[e.type].color }" />
          <span class="small text-muted text-nowrap" style="width: 72px">{{ formatDate(e.date, { day: 'numeric', month: 'short' }) }}</span>
          <router-link :to="e.link || '/app/calendar'" class="small text-truncate">{{ e.title }}</router-link>
          <span class="fs-chip ms-auto d-none d-sm-inline-flex">{{ TYPE[e.type].label }}</span>
        </li>
      </ul>
      <p v-else class="small text-muted mb-0">Nothing scheduled. Save opportunities or add reminders to see them here.</p>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { ChevronLeft, ChevronRight } from 'lucide-vue-next'
import api from '@/api'
import { formatDate } from '@/utils/format'
import StateBlock from '@/components/StateBlock.vue'

const TYPE = {
  deadline: { label: 'Deadline', color: 'var(--accent-peach)', bg: 'var(--tint-peach)', ink: 'var(--ink-peach)' },
  date: { label: 'Important date', color: 'var(--accent-lavender)', bg: 'var(--tint-lavender)', ink: 'var(--ink-lavender)' },
  reminder: { label: 'My reminder', color: 'var(--accent-butter)', bg: 'var(--tint-butter)', ink: 'var(--ink-butter)' },
  applied: { label: 'Applied', color: 'var(--accent-mint)', bg: 'var(--tint-mint)', ink: 'var(--ink-mint)' },
}
const pad = (n) => String(n).padStart(2, '0')
const iso = (d) => `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`
const todayIso = iso(new Date())
const cursor = ref(new Date(new Date().getFullYear(), new Date().getMonth(), 1))
const events = ref([])
const loading = ref(true)
const error = ref('')
const selected = ref(null)

const monthLabel = computed(() => cursor.value.toLocaleDateString('en-IN', { month: 'long', year: 'numeric' }))
const cells = computed(() => {
  const first = new Date(cursor.value), offset = (first.getDay() + 6) % 7
  const start = new Date(first); start.setDate(1 - offset)
  return [...Array(42)].map((_, i) => { const d = new Date(start); d.setDate(start.getDate() + i); return { iso: iso(d), day: d.getDate(), inMonth: d.getMonth() === first.getMonth() } })
})
const eventsByDay = computed(() => events.value.reduce((m, e) => ((m[e.date] ||= []).push(e), m), {}))
const listed = computed(() => selected.value ? (eventsByDay.value[selected.value] || []) : events.value.filter((e) => e.date.slice(0, 7) === iso(cursor.value).slice(0, 7)))

async function load() {
  loading.value = true; error.value = ''
  try { events.value = (await api.get('/calendar', { start: cells.value[0].iso, end: cells.value[41].iso })).events } catch (e) { error.value = e.message } finally { loading.value = false }
}
function shift(n) { cursor.value = new Date(cursor.value.getFullYear(), cursor.value.getMonth() + n, 1); selected.value = null; load() }
function goToday() { cursor.value = new Date(new Date().getFullYear(), new Date().getMonth(), 1); selected.value = todayIso; load() }
onMounted(load)
</script>
