<template>
  <StateBlock v-if="loading" kind="loading" :count="1" col-class="col-12" />
  <StateBlock v-else-if="error" kind="error" :message="error" @retry="load" />
  <div v-else>
    <router-link to="/app/tracker" class="small text-muted d-inline-flex align-items-center gap-1 mb-3"><ArrowLeft :size="16" /> Tracker</router-link>
    <div class="d-flex flex-wrap gap-3 align-items-start mb-4">
      <div class="me-auto min-w-0">
        <h1 class="page-title">{{ a.opportunity.title }}</h1>
        <p class="page-sub">{{ a.opportunity.organization.name }} · <span class="deadline-pill" :class="dl.tone"><CalendarClock /> {{ dl.text }}</span></p>
      </div>
      <router-link :to="`/app/opportunities/${a.opportunity.slug}`" class="btn btn-soft"><Eye :size="16" /> Details</router-link>
      <a :href="a.opportunity.apply_url || a.opportunity.official_url || a.opportunity.source_url" target="_blank" rel="noopener" class="btn btn-primary"><ExternalLink :size="16" /> Official site</a>
    </div>

    <!-- Stepper -->
    <div class="fs-card fs-card-pad mb-4">
      <div class="d-flex gap-1 overflow-auto pb-1" role="list" aria-label="Application progress">
        <div v-for="(s, i) in FLOW" :key="s" role="listitem" class="flex-fill text-center" style="min-width: 88px">
          <div class="rounded-pill mx-1 mb-2" style="height: 6px" :style="{ background: i <= stepIndex ? 'var(--fs-primary)' : 'var(--fs-surface-2)' }" />
          <div class="small" :class="i === stepIndex ? 'fw-bold' : 'text-muted'">{{ label('status', s) }}</div>
        </div>
      </div>
      <div v-if="a.status === 'rejected'" class="alert alert-light border mt-3 mb-0 small">This application was marked as not successful. Don’t lose heart — check your recommendations for similar opportunities.</div>
    </div>

    <div class="row g-4">
      <div class="col-lg-7 d-grid gap-4 align-content-start">
        <section class="fs-card fs-card-pad">
          <h2 class="h6 fw-bold mb-3">Status & details</h2>
          <div class="row g-3">
            <div class="col-md-6"><label class="form-label" for="st">Status</label><select id="st" v-model="form.status" class="form-select"><option v-for="s in STATUSES" :key="s" :value="s">{{ label('status', s) }}</option></select></div>
            <div class="col-md-6"><label class="form-label" for="ad">Application date</label><input id="ad" v-model="form.applied_on" type="date" class="form-control" :max="today" :class="{ 'is-invalid': errors.applied_on }" /><div v-if="errors.applied_on" class="invalid-feedback">{{ errors.applied_on }}</div></div>
            <div class="col-md-6"><label class="form-label" for="ref">Reference / acknowledgement no.</label><input id="ref" v-model="form.reference_number" class="form-control" maxlength="80" /></div>
            <div class="col-md-6"><label class="form-label" for="sn">Note for this change <span class="text-muted fw-normal">(optional)</span></label><input id="sn" v-model="form.note" class="form-control" maxlength="300" /></div>
          </div>
          <p v-if="['applied','approved','rejected'].includes(form.status) && form.status !== a.status" class="small text-muted mt-2 mb-0">Only choose this after it has actually happened — FormSaathi records it as confirmed by you.</p>
          <button class="btn btn-primary mt-3" :disabled="busy" @click="save">Save changes</button>
        </section>

        <section class="fs-card fs-card-pad">
          <div class="d-flex justify-content-between align-items-center mb-2"><h2 class="h6 fw-bold mb-0">Documents checklist</h2><span class="small text-muted">{{ a.checklist.ready }} of {{ a.checklist.total }} ready</span></div>
          <div class="progress mb-3"><div class="progress-bar" :style="{ width: a.checklist.total ? (a.checklist.ready / a.checklist.total) * 100 + '%' : '0%', background: 'var(--fs-success)' }" /></div>
          <ul class="list-unstyled mb-0">
            <li v-for="i in a.checklist.items" :key="i.document_type.id" class="d-flex gap-2 py-2 border-bottom border-soft align-items-start">
              <component :is="DOC_ICON[i.status]" :size="18" class="flex-shrink-0 mt-1" :style="{ color: DOC_COLOR[i.status] }" />
              <div class="flex-grow-1"><div class="small fw-semibold">{{ i.document_type.name }} <span v-if="!i.is_mandatory" class="fs-chip">Optional</span></div><div class="small text-muted">{{ DOC_TEXT[i.status] }}<span v-if="i.notes"> · {{ i.notes }}</span></div></div>
              <router-link v-if="i.status !== 'ready'" to="/app/documents" class="btn btn-soft btn-sm">Upload</router-link>
            </li>
          </ul>
        </section>

        <section class="fs-card fs-card-pad">
          <h2 class="h6 fw-bold mb-3">Notes</h2>
          <form class="d-flex gap-2 mb-3" @submit.prevent="addNote"><input v-model="note" class="form-control" placeholder="e.g. Called the scholarship cell, they said…" maxlength="4000" aria-label="New note" /><button class="btn btn-primary" :disabled="!note.trim()">Add</button></form>
          <p v-if="!a.notes.length" class="small text-muted mb-0">No notes yet.</p>
          <div v-for="n in a.notes" :key="n.id" class="d-flex gap-2 py-2 border-bottom border-soft">
            <div class="flex-grow-1"><div class="small prewrap">{{ n.body }}</div><div class="small text-muted">{{ formatDateTime(n.created_at) }}</div></div>
            <button class="btn btn-ghost btn-sm" aria-label="Delete note" @click="deleteNote(n)"><Trash2 :size="15" /></button>
          </div>
        </section>
      </div>

      <div class="col-lg-5 d-grid gap-4 align-content-start">
        <section class="fs-card fs-card-pad">
          <h2 class="h6 fw-bold mb-3">Reminders</h2>
          <form class="d-grid gap-2 mb-3" @submit.prevent="addReminder">
            <input v-model="rem.title" class="form-control" placeholder="Reminder, e.g. Get income certificate attested" aria-label="Reminder title" maxlength="160" />
            <div class="d-flex gap-2"><input v-model="rem.at" type="datetime-local" class="form-control" aria-label="Remind at" /><select v-model="rem.channel" class="form-select" style="max-width: 140px" aria-label="Channel"><option value="in_app">In-app</option><option value="both">In-app + email</option></select></div>
            <button class="btn btn-soft" :disabled="!rem.title.trim() || !rem.at"><BellPlus :size="16" /> Add reminder</button>
          </form>
          <p v-if="!a.reminders.length" class="small text-muted mb-0">No reminders set.</p>
          <div v-for="r in a.reminders" :key="r.id" class="d-flex gap-2 align-items-center py-2 border-bottom border-soft">
            <input type="checkbox" class="form-check-input mt-0" :checked="r.is_done" :aria-label="'Done: ' + r.title" @change="toggleReminder(r)" />
            <div class="flex-grow-1 small" :class="{ 'text-decoration-line-through text-muted': r.is_done }"><div class="fw-semibold">{{ r.title }}</div><div class="text-muted">{{ formatDateTime(r.remind_at) }}</div></div>
            <button class="btn btn-ghost btn-sm" aria-label="Delete reminder" @click="deleteReminder(r)"><Trash2 :size="15" /></button>
          </div>
        </section>

        <section class="fs-card fs-card-pad">
          <h2 class="h6 fw-bold mb-3">History</h2>
          <div class="timeline">
            <div v-for="(h, i) in [...a.history].reverse()" :key="i" class="timeline-item">
              <div class="small fw-semibold">{{ h.from_status ? `${label('status', h.from_status)} → ${label('status', h.to_status)}` : label('status', h.to_status) }}</div>
              <div class="small text-muted">{{ formatDateTime(h.created_at) }} · confirmed by you<span v-if="h.note"> · {{ h.note }}</span></div>
            </div>
          </div>
        </section>
        <button class="btn btn-outline-danger" @click="remove"><Trash2 :size="16" /> Remove from tracker</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ArrowLeft, BellPlus, CalendarClock, CircleAlert, CircleCheck, CircleDashed, ExternalLink, Eye, Trash2 } from 'lucide-vue-next'
import api from '@/api'
import { useUi } from '@/stores/ui'
import { deadlineInfo, formatDateTime, label } from '@/utils/format'
import StateBlock from '@/components/StateBlock.vue'

const STATUSES = ['interested', 'saved', 'preparing_documents', 'ready_to_apply', 'applied', 'under_review', 'approved', 'rejected']
const FLOW = ['interested', 'preparing_documents', 'ready_to_apply', 'applied', 'under_review', 'approved']
const DOC_ICON = { ready: CircleCheck, missing: CircleDashed, expired: CircleAlert, expiring: CircleAlert }
const DOC_COLOR = { ready: 'var(--fs-success)', missing: 'var(--fs-muted)', expired: 'var(--fs-danger)', expiring: 'var(--fs-warning)' }
const DOC_TEXT = { ready: 'In your vault', missing: 'Not uploaded yet', expired: 'Your copy has expired', expiring: 'Expires before the deadline' }
const route = useRoute()
const router = useRouter()
const ui = useUi()
const a = ref(null)
const loading = ref(true)
const error = ref('')
const busy = ref(false)
const errors = ref({})
const form = reactive({ status: '', applied_on: '', reference_number: '', note: '' })
const note = ref('')
const rem = reactive({ title: '', at: '', channel: 'in_app' })
const today = new Date().toISOString().slice(0, 10)
const dl = computed(() => deadlineInfo(a.value.opportunity))
const stepIndex = computed(() => { const s = a.value.status === 'saved' ? 'interested' : a.value.status === 'rejected' ? 'under_review' : a.value.status; return FLOW.indexOf(s) })

async function load() {
  loading.value = true; error.value = ''
  try {
    a.value = (await api.get(`/applications/${route.params.id}`)).application
    Object.assign(form, { status: a.value.status, applied_on: a.value.applied_on || '', reference_number: a.value.reference_number || '', note: '' })
  } catch (e) { error.value = e.message } finally { loading.value = false }
}
onMounted(load)

async function save() {
  errors.value = {}; busy.value = true
  try {
    const payload = { applied_on: form.applied_on || null, reference_number: form.reference_number || null }
    if (form.status !== a.value.status) { payload.status = form.status; if (form.note) payload.note = form.note }
    if (form.status === 'applied' && !payload.applied_on) payload.applied_on = today
    await api.patch(`/applications/${a.value.id}`, payload)
    ui.toast('Application updated.')
    await load()
  } catch (e) { errors.value = e.fields || {}; ui.error(e) } finally { busy.value = false }
}
async function addNote() { try { await api.post(`/applications/${a.value.id}/notes`, { body: note.value }); note.value = ''; load() } catch (e) { ui.error(e) } }
async function deleteNote(n) { try { await api.delete(`/applications/${a.value.id}/notes/${n.id}`); load() } catch (e) { ui.error(e) } }
async function addReminder() {
  try {
    const r = await api.post('/reminders', { title: rem.title.trim(), remind_at: new Date(rem.at).toISOString(), channel: rem.channel, application_id: a.value.id })
    if (rem.channel !== 'in_app' && !r.email_configured) ui.toast('Reminder saved. Email isn’t configured on this server, so you’ll get it in-app.', 'info', 5000)
    else ui.toast('Reminder saved.')
    rem.title = ''; rem.at = ''; load()
  } catch (e) { ui.error(e) }
}
async function toggleReminder(r) { try { await api.patch(`/reminders/${r.id}`, { is_done: !r.is_done }); load() } catch (e) { ui.error(e) } }
async function deleteReminder(r) { try { await api.delete(`/reminders/${r.id}`); load() } catch (e) { ui.error(e) } }
async function remove() {
  if (!(await ui.confirm({ title: 'Remove from tracker?', message: 'Notes, history and reminders for this application will be deleted.', confirmText: 'Remove', danger: true }))) return
  try { await api.delete(`/applications/${a.value.id}`); ui.toast('Removed from tracker.'); router.push('/app/tracker') } catch (e) { ui.error(e) }
}
</script>
