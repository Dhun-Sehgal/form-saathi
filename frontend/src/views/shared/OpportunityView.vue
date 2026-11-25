<template>
  <div :class="inApp ? '' : 'container py-4 py-lg-5'">
    <StateBlock v-if="loading" kind="loading" :count="1" col-class="col-12" />
    <StateBlock v-else-if="error" kind="error" :title="error.status === 404 ? 'Opportunity not found' : undefined" :message="error.message" @retry="load" />
    <template v-else>
      <router-link :to="inApp ? '/app/discover' : '/explore'" class="small text-muted d-inline-flex align-items-center gap-1 mb-3"><ArrowLeft :size="16" /> Back to opportunities</router-link>

      <div v-if="o.data_origin === 'demo'" class="demo-ribbon d-flex gap-2 mb-3"><FlaskConical :size="18" class="flex-shrink-0 mt-1" /><span><strong>Demo data.</strong> This is a sample listing that shows how FormSaathi works. It is not a real opportunity, and its links point to example.org.</span></div>
      <div v-else-if="o.verification_status !== 'verified'" class="alert alert-warning d-flex gap-2"><Clock :size="18" class="flex-shrink-0 mt-1" /> This listing hasn’t been verified by our team yet. Please confirm every detail on the official source.</div>

      <div class="row g-4">
        <div class="col-lg-8">
          <div class="fs-card fs-card-pad mb-4">
            <div class="d-flex gap-3 align-items-start mb-3">
              <CategoryIcon :name="o.category.icon" :color="o.category.color" />
              <div class="min-w-0">
                <div class="text-muted small">{{ o.organization.name }} · {{ label('org', o.organization.org_type) }}</div>
                <h1 class="h3 fw-bold mb-2">{{ o.title }}</h1>
                <div class="d-flex flex-wrap gap-1"><span class="fs-chip">{{ o.category.name }}</span><DataBadge :o="o" /><span v-if="o.scope === 'state'" class="fs-chip"><MapPin :size="13" /> {{ o.states.map(meta.stateName).join(', ') }}</span></div>
              </div>
            </div>
            <p class="lead fs-6 mb-0">{{ o.summary }}</p>
          </div>

          <section class="fs-card fs-card-pad mb-4" aria-labelledby="about-h">
            <h2 id="about-h" class="h5 fw-bold">About this opportunity</h2>
            <p class="text-muted prewrap mb-0">{{ o.description }}</p>
          </section>

          <section class="fs-card fs-card-pad mb-4" aria-labelledby="elig-h">
            <div class="d-flex align-items-center justify-content-between flex-wrap gap-2 mb-2">
              <h2 id="elig-h" class="h5 fw-bold mb-0">Eligibility requirements</h2>
              <button class="btn btn-primary btn-sm" @click="checkEligibility"><ShieldCheck :size="16" /> {{ t('common.checkEligibility') }}</button>
            </div>
            <p class="text-muted small">{{ o.eligibility_summary }}</p>
            <ul class="list-unstyled mb-0">
              <li v-for="c in o.criteria" :key="c.id" class="crit-row">
                <span class="crit-icon" style="background:var(--fs-surface-2);color:var(--fs-muted)"><ListChecks /></span>
                <div>
                  <div class="fw-semibold">{{ c.description }} <span v-if="!c.is_mandatory" class="fs-chip ms-1">Optional</span></div>
                  <div class="small text-muted">{{ label('criterion', c.criterion_type) }}</div>
                  <div v-if="c.source_excerpt" class="source-quote">“{{ c.source_excerpt }}”</div>
                </div>
              </li>
            </ul>
          </section>

          <section class="fs-card fs-card-pad mb-4" aria-labelledby="ben-h">
            <h2 id="ben-h" class="h5 fw-bold">Benefits</h2>
            <p v-if="benefitAmount(o)" class="fw-bold fs-5 mb-1" style="color: var(--fs-primary)">{{ benefitAmount(o) }}</p>
            <p class="text-muted mb-0 prewrap">{{ o.benefits }}</p>
          </section>

          <section class="fs-card fs-card-pad mb-4" aria-labelledby="docs-h">
            <div class="d-flex justify-content-between align-items-center flex-wrap gap-2 mb-2">
              <h2 id="docs-h" class="h5 fw-bold mb-0">Required documents</h2>
              <button class="btn btn-soft btn-sm" @click="downloadChecklist"><Download :size="15" /> Download checklist</button>
            </div>
            <ul class="list-unstyled mb-0">
              <li v-for="r in o.required_documents" :key="r.document_type.id" class="d-flex gap-2 py-2 border-bottom border-soft">
                <FileText :size="18" class="text-muted flex-shrink-0 mt-1" />
                <div><div class="fw-semibold">{{ r.document_type.name }} <span v-if="!r.is_mandatory" class="fs-chip ms-1">Optional</span></div><div v-if="r.notes" class="small text-muted">{{ r.notes }}</div></div>
              </li>
            </ul>
            <router-link v-if="auth.isLoggedIn" to="/app/documents" class="small d-inline-block mt-2">Check which ones you already have →</router-link>
          </section>

          <section class="fs-card fs-card-pad mb-4" aria-labelledby="how-h">
            <h2 id="how-h" class="h5 fw-bold">How to apply</h2>
            <p class="text-muted prewrap">{{ o.how_to_apply || 'See the official source for the application procedure.' }}</p>
            <p class="small text-muted mb-0">Mode: {{ { online: 'Online', offline: 'Offline', both: 'Online or offline' }[o.application_mode] }}</p>
          </section>

          <div class="d-flex flex-wrap gap-2 align-items-center small text-muted">
            <span>Last updated {{ formatDate(o.updated_at) }}.</span>
            <button v-if="auth.isLoggedIn" class="btn btn-link btn-sm p-0" style="min-height:auto" @click="reportOpen = true"><Flag :size="14" /> Report a correction</button>
          </div>
        </div>

        <aside class="col-lg-4">
          <div class="fs-card fs-card-pad mb-3" style="position: sticky; top: 5.5rem">
            <div class="small-caps mb-2">Deadline</div>
            <div class="d-flex align-items-center gap-2 mb-3"><span class="deadline-pill" :class="dl.tone"><CalendarClock /> {{ dl.text }}</span></div>
            <div class="small mb-3">
              <div v-if="o.opens_on" class="d-flex justify-content-between py-1"><span class="text-muted">Opens</span><span>{{ formatDate(o.opens_on) }}</span></div>
              <div class="d-flex justify-content-between py-1"><span class="text-muted">Closes</span><span>{{ o.deadline ? formatDate(o.deadline) : (o.deadline_note || 'Rolling') }}</span></div>
              <div v-for="d in o.dates" :key="d.label" class="d-flex justify-content-between py-1 gap-2"><span class="text-muted">{{ d.label }}</span><span class="text-nowrap">{{ formatDate(d.date) }}</span></div>
            </div>
            <div class="d-grid gap-2">
              <button class="btn btn-primary" :disabled="busy.track" @click="track"><KanbanSquare :size="17" /> {{ o.application_status ? 'View in tracker' : t('common.track') }}</button>
              <button class="btn btn-soft" :disabled="busy.save" @click="toggleSave"><BookmarkCheck v-if="o.saved" :size="17" /><Bookmark v-else :size="17" /> {{ o.saved ? t('common.saved') : t('common.save') }}</button>
              <button class="btn btn-soft" @click="askSaathi"><Bot :size="17" /> Ask Saathi about this</button>
              <a :href="o.apply_url || o.official_url || o.source_url" target="_blank" rel="noopener noreferrer" class="btn btn-outline-primary"><ExternalLink :size="16" /> {{ t('common.apply') }}</a>
            </div>
            <hr class="border-soft" />
            <div class="small-caps mb-2">Official source</div>
            <a :href="o.source_url" target="_blank" rel="noopener noreferrer" class="small text-break d-block mb-1">{{ o.source_url }}</a>
            <div class="small text-muted">
              <template v-if="o.last_verified_at">Last verified {{ formatDate(o.last_verified_at) }}</template>
              <template v-else-if="o.data_origin === 'demo'">Demo data — not verifiable</template>
              <template v-else>Not yet verified</template>
            </div>
          </div>
        </aside>
      </div>

      <section v-if="o.similar?.length" class="mt-5">
        <h2 class="h5 fw-bold mb-3">Similar opportunities</h2>
        <div class="row g-3"><div v-for="s in o.similar" :key="s.id" class="col-md-6 col-xl-4"><OpportunityCard :o="s" /></div></div>
      </section>
    </template>

    <AppModal :open="reportOpen" title="Report a correction" subtitle="Tell us what’s wrong. Our team checks every report against the official source." @close="reportOpen = false">
      <div class="d-grid gap-3">
        <div><label class="form-label" for="cf">What needs fixing?</label>
          <select id="cf" v-model="report.field" class="form-select"><option v-for="f in ['deadline','eligibility','benefits','documents','link','other']" :key="f" :value="f">{{ f[0].toUpperCase() + f.slice(1) }}</option></select></div>
        <div><label class="form-label" for="cm">Details</label><textarea id="cm" v-model="report.message" rows="4" class="form-control" :class="{ 'is-invalid': reportErr.message }" /><div v-if="reportErr.message" class="invalid-feedback">{{ reportErr.message }}</div></div>
        <div><label class="form-label" for="cu">Official link with the correct info <span class="text-muted fw-normal">(optional)</span></label><input id="cu" v-model="report.suggested_source_url" type="url" class="form-control" :class="{ 'is-invalid': reportErr.suggested_source_url }" placeholder="https://" /><div v-if="reportErr.suggested_source_url" class="invalid-feedback">{{ reportErr.suggested_source_url }}</div></div>
      </div>
      <template #footer><button class="btn btn-ghost" @click="reportOpen = false">Cancel</button><button class="btn btn-primary" :disabled="busy.report" @click="sendReport">Send report</button></template>
    </AppModal>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { ArrowLeft, Bookmark, BookmarkCheck, Bot, CalendarClock, Clock, Download, ExternalLink, FileText, Flag, FlaskConical, KanbanSquare, ListChecks, MapPin, ShieldCheck } from 'lucide-vue-next'
import api from '@/api'
import { useAuth } from '@/stores/auth'
import { useMeta } from '@/stores/meta'
import { useUi } from '@/stores/ui'
import { benefitAmount, deadlineInfo, downloadText, formatDate, label } from '@/utils/format'
import AppModal from '@/components/AppModal.vue'
import CategoryIcon from '@/components/CategoryIcon.vue'
import DataBadge from '@/components/DataBadge.vue'
import OpportunityCard from '@/components/OpportunityCard.vue'
import StateBlock from '@/components/StateBlock.vue'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()
const auth = useAuth()
const meta = useMeta()
const ui = useUi()
const inApp = computed(() => route.path.startsWith('/app'))
const o = ref(null)
const loading = ref(true)
const error = ref(null)
const busy = reactive({ save: false, track: false, report: false })
const reportOpen = ref(false)
const report = reactive({ field: 'deadline', message: '', suggested_source_url: '' })
const reportErr = ref({})
const dl = computed(() => deadlineInfo(o.value))

async function load() {
  loading.value = true; error.value = null
  try { o.value = (await api.get(`/opportunities/${route.params.slug}`)).opportunity } catch (e) { error.value = e } finally { loading.value = false }
}
onMounted(load)

function needLogin() {
  if (auth.isLoggedIn) return false
  router.push({ name: 'login', query: { next: `/app/opportunities/${route.params.slug}` } })
  return true
}
function checkEligibility() { if (!needLogin()) router.push(`/app/eligibility/${o.value.id}`) }
async function toggleSave() {
  if (needLogin()) return
  busy.save = true
  try {
    if (o.value.saved) await api.delete(`/saved/${o.value.id}`); else await api.post('/saved', { opportunity_id: o.value.id })
    o.value.saved = !o.value.saved
    ui.toast(o.value.saved ? 'Saved. We’ll remind you before the deadline.' : 'Removed from saved.')
  } catch (e) { ui.error(e) } finally { busy.save = false }
}
async function track() {
  if (needLogin()) return
  busy.track = true
  try {
    const r = await api.post('/applications', { opportunity_id: o.value.id })
    if (r.created) ui.toast('Added to your tracker.')
    router.push(`/app/tracker/${r.application.id}`)
  } catch (e) { ui.error(e) } finally { busy.track = false }
}
async function askSaathi() {
  if (needLogin()) return
  try {
    const r = await api.post('/ai/sessions', { opportunity_id: o.value.id, language: auth.profile.preferred_language || 'en' })
    router.push({ path: '/app/saathi', query: { session: r.session.id } })
  } catch (e) { ui.error(e) }
}
async function sendReport() {
  reportErr.value = {}
  if (report.message.trim().length < 10) { reportErr.value = { message: 'Please describe the issue (at least 10 characters).' }; return }
  busy.report = true
  try {
    const payload = { field: report.field, message: report.message }
    if (report.suggested_source_url) payload.suggested_source_url = report.suggested_source_url
    ui.toast((await api.post(`/opportunities/${o.value.id}/corrections`, payload)).message)
    reportOpen.value = false; report.message = ''; report.suggested_source_url = ''
  } catch (e) { reportErr.value = e.fields || {}; if (!e.fields) ui.error(e) } finally { busy.report = false }
}
function downloadChecklist() {
  const lines = [`FormSaathi document checklist`, `${o.value.title} — ${o.value.organization.name}`, `Deadline: ${o.value.deadline ? formatDate(o.value.deadline) : 'Rolling'}`, '', ...o.value.required_documents.map((r) => `[ ] ${r.document_type.name}${r.is_mandatory ? '' : ' (optional)'}${r.notes ? ' — ' + r.notes : ''}`), '', `Official source: ${o.value.source_url}`, o.value.data_origin === 'demo' ? 'NOTE: This is demo data, not a real opportunity.' : 'Always confirm requirements on the official source.']
  downloadText(`checklist-${o.value.slug}.txt`, lines.join('\n'))
}
</script>
