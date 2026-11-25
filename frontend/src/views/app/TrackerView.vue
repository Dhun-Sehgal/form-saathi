<template>
  <div>
    <div class="d-flex flex-wrap align-items-end gap-2 mb-4">
      <div class="me-auto"><h1 class="page-title">Application tracker</h1><p class="page-sub">From interested to approved. You confirm each step — FormSaathi never assumes you’ve applied.</p></div>
      <div class="btn-group" role="group" aria-label="View">
        <button class="btn btn-sm" :class="view === 'board' ? 'btn-primary' : 'btn-soft'" @click="view = 'board'"><KanbanSquare :size="16" /> Board</button>
        <button class="btn btn-sm" :class="view === 'list' ? 'btn-primary' : 'btn-soft'" @click="view = 'list'"><List :size="16" /> List</button>
      </div>
    </div>

    <StateBlock v-if="loading" kind="loading" />
    <StateBlock v-else-if="error" kind="error" :message="error" @retry="load" />
    <StateBlock v-else-if="!items.length" title="No applications tracked yet" message="Open any opportunity and click “Track application” to start."><router-link to="/app/discover" class="btn btn-soft">Discover opportunities</router-link></StateBlock>

    <div v-else-if="view === 'board'" class="board">
      <div v-for="s in STATUSES" :key="s" class="board-col">
        <div class="d-flex align-items-center gap-2 px-1 mb-2"><span class="status-dot" :style="{ background: STATUS_COLORS[s] }" /><span class="small fw-bold">{{ label('status', s) }}</span><span class="small text-muted ms-auto">{{ byStatus[s].length }}</span></div>
        <div class="d-grid gap-2">
          <AppCard v-for="a in byStatus[s]" :key="a.id" :a="a" @move="setStatus" />
          <div v-if="!byStatus[s].length" class="small text-muted text-center py-3">—</div>
        </div>
      </div>
    </div>

    <div v-else class="d-grid gap-4">
      <section v-for="s in STATUSES.filter((x) => byStatus[x].length)" :key="s">
        <h2 class="h6 fw-bold d-flex align-items-center gap-2"><span class="status-dot" :style="{ background: STATUS_COLORS[s] }" />{{ label('status', s) }} <span class="text-muted fw-normal">({{ byStatus[s].length }})</span></h2>
        <div class="row g-2"><div v-for="a in byStatus[s]" :key="a.id" class="col-md-6 col-xl-4"><AppCard :a="a" @move="setStatus" /></div></div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { computed, h, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { CalendarClock, KanbanSquare, List } from 'lucide-vue-next'
import api from '@/api'
import { useUi } from '@/stores/ui'
import { deadlineInfo, label, STATUS_COLORS } from '@/utils/format'
import StateBlock from '@/components/StateBlock.vue'

const STATUSES = ['interested', 'saved', 'preparing_documents', 'ready_to_apply', 'applied', 'under_review', 'approved', 'rejected']
const ui = useUi()
const items = ref([])
const loading = ref(true)
const error = ref('')
const view = ref(window.innerWidth < 768 ? 'list' : 'board')
const byStatus = computed(() => Object.fromEntries(STATUSES.map((s) => [s, items.value.filter((a) => a.status === s)])))

async function load() {
  loading.value = true; error.value = ''
  try { items.value = (await api.get('/applications')).items } catch (e) { error.value = e.message } finally { loading.value = false }
}
onMounted(load)

async function setStatus(a, status) {
  if (['applied', 'approved', 'rejected'].includes(status) && !(await ui.confirm({ title: `Mark as “${label('status', status)}”?`, message: status === 'applied' ? 'Only mark this once you have actually submitted the application on the official site.' : 'Only update this when you have heard back from the organisation.', confirmText: 'Yes, update' }))) return
  try {
    const payload = { status }
    if (status === 'applied' && !a.applied_on) payload.applied_on = new Date().toISOString().slice(0, 10)
    await api.patch(`/applications/${a.id}`, payload)
    a.status = status
    ui.toast(`Moved to ${label('status', status)}.`)
  } catch (e) { ui.error(e) }
}

const AppCard = {
  props: ['a'],
  emits: ['move'],
  setup(props, { emit }) {
    return () => {
      const a = props.a, o = a.opportunity, dl = deadlineInfo(o), c = a.checklist
      return h('div', { class: 'fs-card p-3' }, [
        h(RouterLink, { to: `/app/tracker/${a.id}`, class: 'fw-semibold small d-block mb-1 text-decoration-none', style: 'color: var(--fs-text)' }, () => o.title),
        h('div', { class: 'small text-muted mb-2 text-truncate' }, o.organization.name),
        h('div', { class: 'd-flex flex-wrap gap-1 mb-2' }, [
          h('span', { class: `deadline-pill ${dl.tone}` }, [h(CalendarClock), ' ', dl.text]),
          c?.total ? h('span', { class: 'fs-chip' }, `Docs ${c.ready}/${c.total}`) : null,
        ]),
        h('select', { class: 'form-select form-select-sm', 'aria-label': 'Change status', value: a.status, onChange: (e) => { const v = e.target.value; e.target.value = a.status; emit('move', a, v) } },
          STATUSES.map((s) => h('option', { value: s, selected: a.status === s }, label('status', s)))),
      ])
    }
  },
}
</script>
