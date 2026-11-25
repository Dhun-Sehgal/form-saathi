<template>
  <StateBlock v-if="loading" kind="loading" :count="1" col-class="col-12" />
  <div v-else style="max-width: 1100px">
    <router-link to="/admin/opportunities" class="small text-muted d-inline-flex align-items-center gap-1 mb-3"><ArrowLeft :size="16" /> All opportunities</router-link>
    <div class="d-flex flex-wrap align-items-start gap-2 mb-4">
      <div class="me-auto"><h1 class="page-title">{{ isNew ? 'Add opportunity' : 'Edit opportunity' }}</h1><p class="page-sub">Copy facts exactly from the official notification. Never guess eligibility, amounts or dates.</p></div>
      <div v-if="!isNew" class="d-flex flex-wrap gap-1"><DataBadge :o="current" /><span class="fs-chip">{{ label('publication', current.publication_status) }}</span></div>
    </div>

    <div class="row g-4">
      <div class="col-lg-8 d-grid gap-4 align-content-start">
        <section class="fs-card fs-card-pad">
          <h2 class="h6 fw-bold mb-3">Basics</h2>
          <div class="row g-3">
            <F class="col-12" k="title" label="Title"><input v-model="o.title" class="form-control" /></F>
            <F class="col-md-6" k="category_id" label="Category"><select v-model.number="o.category_id" class="form-select"><option v-for="c in meta.categories" :key="c.id" :value="c.id">{{ c.name }}</option></select></F>
            <F class="col-md-6" k="organization_id" label="Organisation">
              <select v-model="orgChoice" class="form-select"><option value="__new">+ New organisation</option><option v-for="g in orgs" :key="g.id" :value="g.id">{{ g.name }}</option></select>
            </F>
            <template v-if="orgChoice === '__new'">
              <F class="col-md-8" k="organization_name" label="New organisation name"><input v-model="o.organization_name" class="form-control" /></F>
              <F class="col-md-4" k="organization_type" label="Type"><select v-model="o.organization_type" class="form-select"><option v-for="(n, k) in LABELS.org" :key="k" :value="k">{{ n }}</option></select></F>
            </template>
            <F class="col-12" k="summary" label="Summary (1–2 lines)"><input v-model="o.summary" class="form-control" maxlength="400" /></F>
            <F class="col-12" k="description" label="Full description"><textarea v-model="o.description" rows="5" class="form-control" /></F>
            <F class="col-md-6" k="scope" label="Scope"><select v-model="o.scope" class="form-select"><option value="national">National</option><option value="state">State-specific</option><option value="institution">Institution-specific</option></select></F>
            <F class="col-md-6" k="data_origin" label="Data origin"><select v-model="o.data_origin" class="form-select"><option value="official">Official (from a real source)</option><option value="demo">Demo (sample data)</option></select></F>
          </div>
        </section>

        <section class="fs-card fs-card-pad">
          <div class="d-flex justify-content-between align-items-center mb-1"><h2 class="h6 fw-bold mb-0">Eligibility rules</h2><button class="btn btn-soft btn-sm" @click="addCriterion"><Plus :size="15" /> Add rule</button></div>
          <p class="small text-muted">Structured rules power the eligibility engine. Use “Other rule” for anything that can’t be checked automatically — users will be asked to review it.</p>
          <F k="eligibility_summary" label="Eligibility summary (shown on cards)"><input v-model="o.eligibility_summary" class="form-control" maxlength="500" /></F>
          <div v-for="(c, i) in o.criteria" :key="i" class="border border-soft rounded-3 p-3 mt-3">
            <div class="row g-2 align-items-end">
              <div class="col-md-4"><label class="form-label small">Rule type</label><select v-model="c.criterion_type" class="form-select form-select-sm" @change="c.value = {}"><option v-for="(n, k) in LABELS.criterion" :key="k" :value="k">{{ n }}</option></select></div>
              <div class="col-md-6"><label class="form-label small">Value</label><CriterionValue :c="c" /></div>
              <div class="col-md-2 d-flex gap-1 justify-content-end"><label class="form-check small mb-0 me-auto"><input v-model="c.is_mandatory" type="checkbox" class="form-check-input" /> Required</label><button class="btn btn-ghost btn-sm" aria-label="Remove rule" @click="o.criteria.splice(i, 1)"><Trash2 :size="15" /></button></div>
              <div class="col-12"><input v-model="c.description" class="form-control form-control-sm" placeholder="Plain-language rule, e.g. Family income up to ₹2.5 lakh per year" /></div>
              <div class="col-12"><textarea v-model="c.source_excerpt" rows="2" class="form-control form-control-sm" placeholder="Paste the exact sentence from the official notification (recommended)" /></div>
            </div>
          </div>
        </section>

        <section class="fs-card fs-card-pad">
          <h2 class="h6 fw-bold mb-3">Benefits & application</h2>
          <div class="row g-3">
            <F class="col-12" k="benefits" label="Benefits"><textarea v-model="o.benefits" rows="2" class="form-control" /></F>
            <F class="col-md-4" k="benefit_amount_min" label="Amount min (₹)"><input v-model.number="o.benefit_amount_min" type="number" min="0" class="form-control" /></F>
            <F class="col-md-4" k="benefit_amount_max" label="Amount max (₹)"><input v-model.number="o.benefit_amount_max" type="number" min="0" class="form-control" /></F>
            <F class="col-md-4" k="benefit_frequency" label="Frequency"><select v-model="o.benefit_frequency" class="form-select"><option :value="null">—</option><option v-for="f in ['one_time','annual','monthly','stipend','other']" :key="f" :value="f">{{ f.replace('_',' ') }}</option></select></F>
            <F class="col-md-4" k="application_mode" label="Mode"><select v-model="o.application_mode" class="form-select"><option value="online">Online</option><option value="offline">Offline</option><option value="both">Both</option></select></F>
            <F class="col-12" k="how_to_apply" label="How to apply"><textarea v-model="o.how_to_apply" rows="3" class="form-control" /></F>
          </div>
        </section>

        <section class="fs-card fs-card-pad">
          <div class="d-flex justify-content-between align-items-center mb-2"><h2 class="h6 fw-bold mb-0">Required documents</h2><button class="btn btn-soft btn-sm" @click="o.required_documents.push({ document_type_id: meta.document_types[0]?.id, is_mandatory: true, notes: '' })"><Plus :size="15" /> Add</button></div>
          <div v-for="(d, i) in o.required_documents" :key="i" class="row g-2 align-items-center mt-1">
            <div class="col-md-4"><select v-model.number="d.document_type_id" class="form-select form-select-sm" aria-label="Document type"><option v-for="t in meta.document_types" :key="t.id" :value="t.id">{{ t.name }}</option></select></div>
            <div class="col-md-5"><input v-model="d.notes" class="form-control form-control-sm" placeholder="Notes (e.g. issued this financial year)" /></div>
            <div class="col-md-3 d-flex align-items-center gap-2"><label class="form-check small mb-0"><input v-model="d.is_mandatory" type="checkbox" class="form-check-input" /> Required</label><button class="btn btn-ghost btn-sm ms-auto" aria-label="Remove" @click="o.required_documents.splice(i, 1)"><Trash2 :size="15" /></button></div>
          </div>
          <div v-if="errors.required_documents" class="text-danger small mt-2">{{ errors.required_documents }}</div>
        </section>
      </div>

      <div class="col-lg-4 d-grid gap-4 align-content-start">
        <section class="fs-card fs-card-pad">
          <h2 class="h6 fw-bold mb-3">Source & dates</h2>
          <div class="d-grid gap-3">
            <F k="source_url" label="Official source URL (required)"><input v-model="o.source_url" type="url" class="form-control" placeholder="https://" /></F>
            <F k="official_url" label="Information page"><input v-model="o.official_url" type="url" class="form-control" placeholder="https://" /></F>
            <F k="apply_url" label="Application portal"><input v-model="o.apply_url" type="url" class="form-control" placeholder="https://" /></F>
            <F k="opens_on" label="Opens on"><input v-model="o.opens_on" type="date" class="form-control" /></F>
            <F k="deadline" label="Deadline"><input v-model="o.deadline" type="date" class="form-control" :disabled="o.is_rolling" /></F>
            <label class="form-check small"><input v-model="o.is_rolling" type="checkbox" class="form-check-input" /> Rolling / no fixed deadline</label>
            <F k="deadline_note" label="Deadline note"><input v-model="o.deadline_note" class="form-control" /></F>
          </div>
          <div class="d-flex justify-content-between align-items-center mt-3 mb-2"><span class="small fw-semibold">Other important dates</span><button class="btn btn-soft btn-sm" @click="o.dates.push({ label: '', date: '', note: '' })"><Plus :size="14" /></button></div>
          <div v-for="(d, i) in o.dates" :key="i" class="d-flex gap-1 mb-2"><input v-model="d.label" class="form-control form-control-sm" placeholder="Label" aria-label="Date label" /><input v-model="d.date" type="date" class="form-control form-control-sm" aria-label="Date" /><button class="btn btn-ghost btn-sm" aria-label="Remove date" @click="o.dates.splice(i, 1)"><Trash2 :size="14" /></button></div>
        </section>

        <section class="fs-card fs-card-pad d-grid gap-2">
          <div v-if="formError" class="alert alert-danger small py-2 mb-0">{{ formError }}</div>
          <button class="btn btn-primary" :disabled="busy" @click="save">{{ busy ? 'Saving…' : isNew ? 'Create (as draft)' : 'Save changes' }}</button>
          <template v-if="!isNew">
            <hr class="border-soft my-1" />
            <div class="small-caps">Workflow</div>
            <button v-if="current.data_origin === 'official' && current.verification_status !== 'verified'" class="btn btn-soft" @click="act('verify')"><BadgeCheck :size="16" /> Verify against source</button>
            <button v-if="current.publication_status !== 'published'" class="btn btn-soft" @click="act('publish')"><Globe :size="16" /> Publish</button>
            <button v-else class="btn btn-soft" @click="act('unpublish')"><EyeOff :size="16" /> Unpublish</button>
            <button v-if="current.verification_status === 'verified'" class="btn btn-ghost" @click="act('mark_pending')">Mark pending re-verification</button>
            <button v-if="current.verification_status !== 'expired'" class="btn btn-ghost" @click="act('expire')">Mark expired</button>
            <button v-if="current.verification_status !== 'archived'" class="btn btn-ghost" @click="act('archive')">Archive</button>
            <button class="btn btn-outline-danger btn-sm" @click="remove">Delete</button>
          </template>
        </section>

        <section v-if="!isNew && current.logs?.length" class="fs-card fs-card-pad">
          <h2 class="h6 fw-bold mb-3">Verification log</h2>
          <div class="timeline"><div v-for="(l, i) in current.logs" :key="i" class="timeline-item small"><div class="fw-semibold">{{ l.action.replace('_', ' ') }}</div><div class="text-muted">{{ formatDateTime(l.created_at) }} · {{ l.actor || 'system' }}</div><div v-if="l.notes" class="text-muted">{{ l.notes }}</div></div></div>
        </section>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, h, onMounted, provide, inject, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ArrowLeft, BadgeCheck, EyeOff, Globe, Plus, Trash2 } from 'lucide-vue-next'
import api from '@/api'
import { useMeta } from '@/stores/meta'
import { useUi } from '@/stores/ui'
import { formatDateTime, label, LABELS } from '@/utils/format'
import DataBadge from '@/components/DataBadge.vue'
import StateBlock from '@/components/StateBlock.vue'

const route = useRoute()
const router = useRouter()
const meta = useMeta()
const ui = useUi()
const isNew = computed(() => !route.params.id)
const loading = ref(true)
const busy = ref(false)
const orgs = ref([])
const orgChoice = ref('__new')
const current = ref(null)
const errors = ref({})
const formError = ref('')
const blank = () => ({ title: '', category_id: null, organization_name: '', organization_type: 'other', summary: '', description: '', scope: 'national', data_origin: 'official', eligibility_summary: '', benefits: '', benefit_amount_min: null, benefit_amount_max: null, benefit_frequency: null, application_mode: 'online', how_to_apply: '', source_url: '', official_url: '', apply_url: '', opens_on: '', deadline: '', is_rolling: false, deadline_note: '', criteria: [], required_documents: [], dates: [], is_featured: false })
const o = reactive(blank())
provide('errors', errors)

// Small form-field wrapper that shows the server's validation error for its key.
const F = {
  props: ['k', 'label'],
  setup(props, { slots }) {
    const errs = inject('errors')
    // Wrapping the control in <label> associates it with its text for screen readers.
    return () => h('div', [h('label', { class: 'd-block mb-0' }, [h('span', { class: 'form-label small d-block' }, props.label), slots.default()]), errs.value[props.k] ? h('div', { class: 'text-danger small mt-1', role: 'alert' }, errs.value[props.k]) : null])
  },
}
// Value editor that adapts to the rule type.
const CriterionValue = {
  props: ['c'],
  setup(props) {
    const multi = (opts) => h('select', { class: 'form-select form-select-sm', multiple: true, size: 3, onChange: (e) => { props.c.value = { any_of: [...e.target.selectedOptions].map((x) => x.value) } } },
      opts.map(([v, l]) => h('option', { value: v, selected: (props.c.value.any_of || []).includes(v) }, l)))
    const num = (key, ph) => h('input', { type: 'number', class: 'form-control form-control-sm', placeholder: ph, value: props.c.value[key] ?? '', onInput: (e) => { props.c.value = { ...props.c.value, [key]: e.target.value === '' ? undefined : Number(e.target.value) } } })
    return () => {
      const t = props.c.criterion_type
      if (t === 'age_min' || t === 'age_max') return num('years', 'Years')
      if (t === 'income_max') return num('amount', 'Annual income limit in ₹')
      if (t === 'marks_min_percentage' || t === 'marks_min_cgpa') return num('value', t.endsWith('cgpa') ? 'Min CGPA' : 'Min %')
      if (t === 'year_of_study') return h('div', { class: 'd-flex gap-1' }, [num('min', 'From year'), num('max', 'To year')])
      if (t === 'education_level') return multi(Object.entries(LABELS.education))
      if (t === 'social_category') return multi(Object.entries(LABELS.social).filter(([k]) => k !== 'prefer_not_say'))
      if (t === 'gender') return multi(Object.entries(LABELS.gender).filter(([k]) => k !== 'prefer_not_say'))
      if (t === 'state_domicile') return multi(meta.states.map((s) => [s.code, s.name]))
      if (t === 'course') return h('input', { class: 'form-control form-control-sm', placeholder: 'Keywords, comma separated (e.g. engineering, b.tech)', value: (props.c.value.any_of || []).join(', '), onChange: (e) => { props.c.value = { any_of: e.target.value.split(',').map((s) => s.trim().toLowerCase()).filter(Boolean) } } })
      if (t === 'disability') { if (!props.c.value.required) props.c.value = { required: true }; return h('div', { class: 'small text-muted pt-1' }, 'Applicant must have a disability certificate') }
      return h('div', { class: 'small text-muted pt-1' }, 'Users review this rule themselves')
    }
  },
}

function addCriterion() { o.criteria.push({ criterion_type: 'education_level', value: {}, description: '', source_excerpt: '', is_mandatory: true }) }

async function load() {
  loading.value = true
  try {
    await meta.load()
    orgs.value = (await api.get('/admin/organizations')).items
    if (!isNew.value) {
      const d = (await api.get(`/admin/opportunities/${route.params.id}`)).opportunity
      current.value = d
      Object.assign(o, blank(), {
        ...Object.fromEntries(Object.keys(blank()).filter((k) => k in d).map((k) => [k, d[k] ?? blank()[k]])),
        criteria: d.criteria.map(({ criterion_type, value, description, source_excerpt, is_mandatory }) => ({ criterion_type, value: { ...value }, description, source_excerpt: source_excerpt || '', is_mandatory })),
        required_documents: d.required_documents.map((r) => ({ document_type_id: r.document_type.id, is_mandatory: r.is_mandatory, notes: r.notes || '' })),
        dates: d.dates.map((x) => ({ label: x.label, date: x.date, note: x.note || '' })),
      })
      orgChoice.value = d.organization_id
    } else {
      o.category_id = meta.categories[0]?.id
    }
  } catch (e) { ui.error(e) } finally { loading.value = false }
}
onMounted(load)

function payload() {
  const p = JSON.parse(JSON.stringify(o))
  for (const k of ['official_url', 'apply_url', 'opens_on', 'deadline', 'deadline_note', 'how_to_apply']) if (!p[k]) p[k] = null
  if (p.is_rolling) p.deadline = p.deadline || null
  for (const k of ['benefit_amount_min', 'benefit_amount_max']) if (p[k] === '' || p[k] === undefined) p[k] = null
  if (orgChoice.value !== '__new') { p.organization_id = Number(orgChoice.value); p.organization_name = null } else p.organization_id = null
  p.criteria.forEach((c) => { if (!c.source_excerpt) c.source_excerpt = null })
  p.required_documents.forEach((d) => { if (!d.notes) d.notes = null })
  p.dates = p.dates.filter((d) => d.label && d.date).map((d) => ({ ...d, note: d.note || null }))
  return p
}
async function save() {
  errors.value = {}; formError.value = ''; busy.value = true
  try {
    const p = payload()
    const r = isNew.value ? await api.post('/admin/opportunities', p) : await api.put(`/admin/opportunities/${route.params.id}`, p)
    ui.toast(isNew.value ? 'Created as a draft. Verify it, then publish.' : 'Saved.')
    if (isNew.value) router.replace(`/admin/opportunities/${r.opportunity.id}`)
    await load()
  } catch (e) {
    errors.value = Object.fromEntries(Object.entries(e.fields || {}).map(([k, v]) => [k, typeof v === 'string' ? v : 'Check this field']))
    formError.value = e.message
  } finally { busy.value = false }
}
async function act(action) {
  if (action === 'verify' && !(await ui.confirm({ title: 'Mark as verified?', message: `Confirm you have checked every detail against the official source: ${current.value.source_url}`, confirmText: 'I checked it — verify' }))) return
  try { await api.post(`/admin/opportunities/${route.params.id}/status`, { action }); ui.toast('Status updated.'); load() } catch (e) { ui.error(e) }
}
async function remove() {
  if (!(await ui.confirm({ title: 'Delete this opportunity?', message: 'Only possible if no user has saved or tracked it. Otherwise, archive it.', confirmText: 'Delete', danger: true }))) return
  try { await api.delete(`/admin/opportunities/${route.params.id}`); ui.toast('Deleted.'); router.push('/admin/opportunities') } catch (e) { ui.error(e) }
}
</script>
