<template>
  <StateBlock v-if="loading" kind="loading" :count="2" col-class="col-lg-6" />
  <StateBlock v-else-if="error" kind="error" :message="error" @retry="load" />
  <div v-else>
    <!-- Header -->
    <div class="d-flex flex-wrap align-items-center gap-2 mb-3">
      <router-link to="/app/resume" class="btn btn-ghost btn-icon" aria-label="Back to resumes"><ArrowLeft :size="18" /></router-link>
      <input v-model="r.title" class="form-control fw-bold border-0 bg-transparent px-1 flex-grow-1" style="font-size: 1.25rem; min-width: 180px; max-width: 520px" maxlength="120" aria-label="Resume name" />
      <span class="small text-muted d-flex align-items-center gap-1" aria-live="polite">
        <Loader2 v-if="saveState === 'saving'" :size="14" class="spin" /><CircleCheck v-else-if="saveState === 'saved'" :size="14" style="color: var(--fs-success)" /><CircleAlert v-else-if="saveState === 'error'" :size="14" style="color: var(--fs-danger)" />
        {{ { saving: 'Saving…', saved: 'Saved', error: 'Not saved', idle: '' }[saveState] }}
      </span>
      <div class="ms-auto d-flex gap-2 flex-wrap">
        <div class="btn-group" role="group" aria-label="Template">
          <button v-for="tpl in ['classic', 'modern']" :key="tpl" class="btn btn-sm text-capitalize" :class="r.template === tpl ? 'btn-primary' : 'btn-soft'" @click="r.template = tpl">{{ tpl }}</button>
        </div>
        <button class="btn btn-primary btn-sm" @click="exportPdf"><FileDown :size="16" /> PDF</button>
        <button class="btn btn-soft btn-sm" @click="exportTxt"><FileText :size="16" /> .txt</button>
      </div>
    </div>

    <!-- Mobile tabs -->
    <div class="d-flex gap-1 mb-3 d-lg-none overflow-auto">
      <button v-for="tb in mobileTabs" :key="tb.id" class="choice-chip" :class="{ active: tab === tb.id }" @click="tab = tb.id"><component :is="tb.icon" :size="15" /> {{ tb.label }}</button>
    </div>

    <div class="row g-4">
      <!-- EDITOR -->
      <div v-show="isDesktop || tab === 'edit'" class="col-lg-6 d-grid gap-3 align-content-start">
        <div class="fs-card fs-card-pad">
          <div class="row g-2">
            <div class="col-12"><label class="form-label small" for="tr">Target role <span class="text-muted fw-normal">(helps the AI coach)</span></label><input id="tr" v-model="r.target_role" class="form-control form-control-sm" maxlength="120" placeholder="e.g. Software Engineering Intern" /></div>
          </div>
        </div>

        <EditorSection title="Contact" :icon="UserRound" open>
          <div class="row g-2">
            <div class="col-md-6"><label class="form-label small" for="bn">Full name</label><input id="bn" v-model="d.basics.name" class="form-control form-control-sm" /></div>
            <div class="col-md-6"><label class="form-label small" for="bh">Headline <span class="text-muted fw-normal">(optional)</span></label><input id="bh" v-model="d.basics.headline" class="form-control form-control-sm" placeholder="e.g. Data Science student, IIT Madras" /></div>
            <div class="col-md-6"><label class="form-label small" for="be">Email</label><input id="be" v-model="d.basics.email" type="email" class="form-control form-control-sm" /></div>
            <div class="col-md-6"><label class="form-label small" for="bp">Phone</label><input id="bp" v-model="d.basics.phone" class="form-control form-control-sm" /></div>
            <div class="col-12"><label class="form-label small" for="bl">Location</label><input id="bl" v-model="d.basics.location" class="form-control form-control-sm" placeholder="City, State" /></div>
          </div>
          <div class="small fw-bold mt-3 mb-1">Links</div>
          <div v-for="(l, i) in d.basics.links" :key="i" class="d-flex gap-1 mb-1">
            <input v-model="l.label" class="form-control form-control-sm" style="max-width: 130px" placeholder="LinkedIn" aria-label="Link label" />
            <input v-model="l.url" class="form-control form-control-sm" placeholder="https://" aria-label="Link URL" />
            <button class="btn btn-ghost btn-sm" aria-label="Remove link" @click="d.basics.links.splice(i, 1)"><X :size="15" /></button>
          </div>
          <button v-if="d.basics.links.length < 6" class="btn btn-soft btn-sm" @click="d.basics.links.push({ label: '', url: '' })"><Plus :size="14" /> Add link</button>
        </EditorSection>

        <EditorSection title="Professional summary" :icon="AlignLeft" open>
          <textarea v-model="d.summary" rows="4" class="form-control form-control-sm" maxlength="1200" placeholder="2–3 lines: who you are, what you build, and your strongest result." />
          <div class="form-text">{{ wordCount(d.summary) }} words · aim for 20–80</div>
        </EditorSection>

        <EditorSection title="Experience" :icon="Briefcase" :count="d.experience.length" open>
          <ItemCard v-for="(e, i) in d.experience" :key="'e' + i" :index="i" :total="d.experience.length" @up="move(d.experience, i, -1)" @down="move(d.experience, i, 1)" @remove="d.experience.splice(i, 1)">
            <div class="row g-2">
              <div class="col-md-6"><input v-model="e.role" class="form-control form-control-sm" placeholder="Role (e.g. ML Intern)" aria-label="Role" /></div>
              <div class="col-md-6"><input v-model="e.org" class="form-control form-control-sm" placeholder="Organisation" aria-label="Organisation" /></div>
              <div class="col-4"><input v-model="e.start" class="form-control form-control-sm" placeholder="Start (Jul 2026)" aria-label="Start" /></div>
              <div class="col-4"><input v-model="e.end" class="form-control form-control-sm" placeholder="End / Present" aria-label="End" /></div>
              <div class="col-4"><input v-model="e.location" class="form-control form-control-sm" placeholder="Remote / City" aria-label="Location" /></div>
            </div>
            <BulletList v-model="e.bullets" :role="r.target_role || e.role" :ai="aiConfigured" />
          </ItemCard>
          <button v-if="d.experience.length < 10" class="btn btn-soft btn-sm" @click="d.experience.push({ role: '', org: '', location: '', start: '', end: '', bullets: [''] })"><Plus :size="14" /> Add experience</button>
        </EditorSection>

        <EditorSection title="Projects" :icon="FolderGit2" :count="d.projects.length" open>
          <ItemCard v-for="(p, i) in d.projects" :key="'p' + i" :index="i" :total="d.projects.length" @up="move(d.projects, i, -1)" @down="move(d.projects, i, 1)" @remove="d.projects.splice(i, 1)">
            <div class="row g-2">
              <div class="col-md-6"><input v-model="p.name" class="form-control form-control-sm" placeholder="Project name" aria-label="Project name" /></div>
              <div class="col-md-6"><input v-model="p.tech" class="form-control form-control-sm" placeholder="Tech (Flask, Vue.js…)" aria-label="Technologies" /></div>
              <div class="col-12"><input v-model="p.link" class="form-control form-control-sm" placeholder="Link (GitHub / live)" aria-label="Project link" /></div>
            </div>
            <BulletList v-model="p.bullets" :role="r.target_role" :ai="aiConfigured" />
          </ItemCard>
          <button v-if="d.projects.length < 10" class="btn btn-soft btn-sm" @click="d.projects.push({ name: '', tech: '', link: '', bullets: [''] })"><Plus :size="14" /> Add project</button>
        </EditorSection>

        <EditorSection title="Education" :icon="GraduationCap" :count="d.education.length">
          <ItemCard v-for="(e, i) in d.education" :key="'ed' + i" :index="i" :total="d.education.length" @up="move(d.education, i, -1)" @down="move(d.education, i, 1)" @remove="d.education.splice(i, 1)">
            <div class="row g-2">
              <div class="col-12"><input v-model="e.school" class="form-control form-control-sm" placeholder="College / school" aria-label="College" /></div>
              <div class="col-md-8"><input v-model="e.degree" class="form-control form-control-sm" placeholder="Degree and branch" aria-label="Degree" /></div>
              <div class="col-md-4"><input v-model="e.score" class="form-control form-control-sm" placeholder="CGPA / %" aria-label="Score" /></div>
              <div class="col-6"><input v-model="e.start" class="form-control form-control-sm" placeholder="Start" aria-label="Start" /></div>
              <div class="col-6"><input v-model="e.end" class="form-control form-control-sm" placeholder="End / Expected" aria-label="End" /></div>
              <div class="col-12"><input v-model="e.details" class="form-control form-control-sm" placeholder="Coursework or honours (optional)" aria-label="Details" /></div>
            </div>
          </ItemCard>
          <button v-if="d.education.length < 6" class="btn btn-soft btn-sm" @click="d.education.push({ school: '', degree: '', start: '', end: '', score: '', details: '' })"><Plus :size="14" /> Add education</button>
        </EditorSection>

        <EditorSection title="Skills" :icon="Wrench" :count="d.skills.length">
          <div v-for="(s, i) in d.skills" :key="'s' + i" class="d-flex gap-1 mb-2">
            <input v-model="s.group" class="form-control form-control-sm" style="max-width: 150px" placeholder="Group" aria-label="Skill group" />
            <input v-model="s.items" class="form-control form-control-sm" placeholder="Python, SQL, Flask (comma separated)" aria-label="Skills" />
            <button class="btn btn-ghost btn-sm" aria-label="Remove skill group" @click="d.skills.splice(i, 1)"><X :size="15" /></button>
          </div>
          <button v-if="d.skills.length < 10" class="btn btn-soft btn-sm" @click="d.skills.push({ group: '', items: '' })"><Plus :size="14" /> Add skill group</button>
        </EditorSection>

        <EditorSection title="Achievements" :icon="Trophy" :count="d.achievements.length">
          <StringList v-model="d.achievements" placeholder="e.g. Ranked 36 / 1,066 in a Kaggle competition" />
        </EditorSection>
        <EditorSection title="Certifications" :icon="BadgeCheck" :count="d.certifications.length">
          <StringList v-model="d.certifications" placeholder="e.g. NPTEL Elite – Cloud Computing (81%)" />
        </EditorSection>
      </div>

      <!-- PREVIEW / ATS / MATCH -->
      <div v-show="isDesktop || tab !== 'edit'" class="col-lg-6">
        <div class="resume-side">
          <div class="d-none d-lg-flex gap-1 mb-3">
            <button v-for="tb in mobileTabs.slice(1)" :key="tb.id" class="choice-chip" :class="{ active: panel === tb.id }" @click="panel = tb.id"><component :is="tb.icon" :size="15" /> {{ tb.label }}<span v-if="tb.id === 'ats'" class="fs-badge ms-1" :class="atsBadge">{{ report.score }}</span><span v-if="tb.id === 'match' && match" class="fs-badge fs-badge-ai ms-1">{{ match.percent }}%</span></button>
          </div>

          <div v-show="activePanel === 'preview'">
            <div class="resume-paper fs-card" v-html="html" />
            <p class="small text-muted mt-2 mb-0">Exports as an A4 PDF with real, selectable text. In the print dialog choose “Save as PDF”.</p>
          </div>

          <div v-show="activePanel === 'ats'" class="fs-card fs-card-pad">
            <div class="d-flex align-items-center gap-3 mb-3">
              <ProgressRing :value="report.score" :size="76" :stroke="8" />
              <div><h2 class="h6 fw-bold mb-1">ATS score {{ report.score }}/100 · {{ band.label }}</h2><p class="small text-muted mb-0">{{ report.passed }} of {{ report.total }} ATS checks passed. Score = pass 1, warning ½, fail 0, averaged. {{ report.stats.words }} words · {{ report.stats.bullets }} bullets · {{ report.stats.skills }} skills.</p></div>
            </div>
            <ul class="list-unstyled mb-0">
              <li v-for="c in report.checks" :key="c.id" class="crit-row py-2">
                <span class="crit-icon" :class="c.status === 'pass' ? 'crit-met' : c.status === 'fail' ? 'crit-not_met' : 'crit-unknown'"><Check v-if="c.status === 'pass'" /><X v-else-if="c.status === 'fail'" /><AlertTriangle v-else /></span>
                <div><div class="fw-semibold small">{{ c.label }}</div><div class="small text-muted">{{ c.detail }}</div></div>
              </li>
            </ul>
            <template v-if="report.tips.length">
              <h3 class="h6 fw-bold mt-3">Bullet coach</h3>
              <div v-for="(tip, k) in report.tips.slice(0, 8)" :key="k" class="p-2 rounded-3 mb-2" style="background: var(--fs-surface-2)">
                <div class="small fw-semibold mb-1">“{{ tip.text.length > 110 ? tip.text.slice(0, 110) + '…' : tip.text }}”</div>
                <div class="d-flex flex-wrap gap-1"><span v-for="is in tip.issues" :key="is.code" class="fs-badge fs-badge-pending">{{ is.label }}</span></div>
              </div>
            </template>
          </div>

          <div v-show="activePanel === 'match'" class="fs-card fs-card-pad">
            <h2 class="h6 fw-bold mb-1">Match against an opportunity</h2>
            <p class="small text-muted">Pick an internship, job or fellowship on FormSaathi — or paste any job description.</p>
            <select v-model="matchOppId" class="form-select form-select-sm mb-2" aria-label="Choose opportunity">
              <option value="">Choose from FormSaathi…</option>
              <option v-for="o in opportunities" :key="o.id" :value="String(o.id)">{{ o.title }}</option>
            </select>
            <textarea v-model="jobText" rows="5" class="form-control form-control-sm mb-3" placeholder="…or paste a job description here" aria-label="Job description" />
            <template v-if="match && match.keywords.length">
              <div class="d-flex align-items-center gap-3 mb-3">
                <ProgressRing :value="match.percent" :size="76" :stroke="8" />
                <div><div class="fw-bold">{{ match.matched.length }} of {{ match.keywords.length }} key terms found</div><div class="small text-muted">Add missing terms only where they are true for you — never stuff keywords.</div></div>
              </div>
              <div class="small fw-bold mb-1">Found in your resume</div>
              <div class="d-flex flex-wrap gap-1 mb-3"><span v-for="k in match.matched" :key="k" class="fs-badge fs-badge-verified"><Check /> {{ k }}</span><span v-if="!match.matched.length" class="small text-muted">None yet.</span></div>
              <div class="small fw-bold mb-1">Missing</div>
              <div class="d-flex flex-wrap gap-1"><span v-for="k in match.missing" :key="k" class="fs-badge fs-badge-coral">{{ k }}</span><span v-if="!match.missing.length" class="small text-muted">Nothing missing — great match.</span></div>
            </template>
            <p v-else class="small text-muted mb-0">Choose an opportunity or paste a description to see your keyword match.</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, h, onBeforeUnmount, onMounted, reactive, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import {
  AlertTriangle, AlignLeft, ArrowDown, ArrowLeft, ArrowUp, BadgeCheck, Briefcase, Check, ChevronDown, CircleAlert, CircleCheck, Eye,
  FileDown, FileText, FolderGit2, GraduationCap, ListChecks, Loader2, PenLine, Plus, Sparkles, Target, Trash2, Trophy, UserRound, Wrench, X,
} from 'lucide-vue-next'
import api from '@/api'
import { useUi } from '@/stores/ui'
import { analyze, bulletIssues, emptyResume, matchKeywords, opportunityText, resumeText, scoreBand } from '@/utils/ats'
import { downloadText } from '@/utils/format'
import { printResume, renderResumeHTML, RESUME_CSS } from '@/utils/resumeTemplate'
import ProgressRing from '@/components/ProgressRing.vue'
import StateBlock from '@/components/StateBlock.vue'

const route = useRoute()
const ui = useUi()
const loading = ref(true)
const error = ref('')
const r = reactive({ id: null, title: '', target_role: '', template: 'classic' })
const d = reactive(emptyResume())
const aiConfigured = ref(false)
const saveState = ref('idle')
const tab = ref('edit')
const panel = ref('preview')
const isDesktop = ref(window.matchMedia('(min-width: 992px)').matches)
const opportunities = ref([])
const matchOppId = ref(route.query.match ? String(route.query.match) : '')
const jobText = ref('')
const detailText = ref('')
const mobileTabs = [{ id: 'edit', label: 'Edit', icon: PenLine }, { id: 'preview', label: 'Preview', icon: Eye }, { id: 'ats', label: 'ATS check', icon: ListChecks }, { id: 'match', label: 'Job match', icon: Target }]
const activePanel = computed(() => (isDesktop.value ? panel.value : tab.value))
const html = computed(() => renderResumeHTML(d, r.template))
const report = computed(() => analyze(d))
const band = computed(() => scoreBand(report.value.score))
const atsBadge = computed(() => `fs-badge-${band.value.tone}`)
const match = computed(() => {
  const text = [jobText.value, detailText.value].filter(Boolean).join('\n')
  return text.trim() ? matchKeywords(d, text) : null
})
const wordCount = (s) => (s || '').trim().split(/\s+/).filter(Boolean).length

// ---- small local components -------------------------------------------------
const EditorSection = {
  props: { title: String, icon: [Object, Function], count: Number, open: Boolean },
  setup(props, { slots }) {
    const isOpen = ref(props.open)
    return () => h('section', { class: 'fs-card' }, [
      h('button', { class: 'w-100 d-flex align-items-center gap-2 p-3 bg-transparent border-0 text-start', 'aria-expanded': isOpen.value, onClick: () => { isOpen.value = !isOpen.value } }, [
        h('span', { class: 'icon-tile icon-tile-sm tint-lavender' }, [h(props.icon)]),
        h('span', { class: 'fw-bold flex-grow-1', style: 'color: var(--fs-text)' }, props.title),
        props.count ? h('span', { class: 'fs-chip' }, String(props.count)) : null,
        h(ChevronDown, { size: 18, style: `transition: transform .2s; transform: rotate(${isOpen.value ? 180 : 0}deg); color: var(--fs-muted)` }),
      ]),
      isOpen.value ? h('div', { class: 'px-3 pb-3' }, slots.default()) : null,
    ])
  },
}
const ItemCard = {
  props: { index: Number, total: Number },
  emits: ['up', 'down', 'remove'],
  setup(props, { slots, emit }) {
    return () => h('div', { class: 'border border-soft rounded-4 p-2 mb-2' }, [
      h('div', { class: 'd-flex justify-content-end gap-1 mb-1' }, [
        h('button', { class: 'btn btn-ghost btn-sm', 'aria-label': 'Move up', disabled: props.index === 0, onClick: () => emit('up') }, [h(ArrowUp, { size: 14 })]),
        h('button', { class: 'btn btn-ghost btn-sm', 'aria-label': 'Move down', disabled: props.index === props.total - 1, onClick: () => emit('down') }, [h(ArrowDown, { size: 14 })]),
        h('button', { class: 'btn btn-ghost btn-sm', 'aria-label': 'Remove', onClick: () => emit('remove') }, [h(Trash2, { size: 14 })]),
      ]),
      slots.default(),
    ])
  },
}
const StringList = {
  props: { modelValue: Array, placeholder: String },
  setup(props) {
    return () => h('div', [
      ...props.modelValue.map((_, i) => h('div', { class: 'd-flex gap-1 mb-1' }, [
        h('input', { class: 'form-control form-control-sm', value: props.modelValue[i], placeholder: props.placeholder, 'aria-label': `Item ${i + 1}`, onInput: (e) => { props.modelValue[i] = e.target.value } }),
        h('button', { class: 'btn btn-ghost btn-sm', 'aria-label': 'Remove', onClick: () => props.modelValue.splice(i, 1) }, [h(X, { size: 15 })]),
      ])),
      props.modelValue.length < 10 ? h('button', { class: 'btn btn-soft btn-sm', onClick: () => props.modelValue.push('') }, [h(Plus, { size: 14 }), ' Add']) : null,
    ])
  },
}
const BulletList = {
  props: { modelValue: Array, role: String, ai: Boolean },
  setup(props) {
    const busy = ref(-1)
    const suggestions = reactive({})
    async function improve(i) {
      const text = (props.modelValue[i] || '').trim()
      if (text.length < 3) return ui.toast('Write the bullet first, then ask Saathi to improve it.', 'info')
      busy.value = i
      try { suggestions[i] = (await api.post('/resumes/improve-bullet', { bullet: text, role: props.role || '' })).suggestions } catch (e) { ui.error(e) } finally { busy.value = -1 }
    }
    return () => h('div', { class: 'mt-2' }, [
      h('div', { class: 'small fw-bold mb-1' }, 'Bullets'),
      ...props.modelValue.map((_, i) => {
        const issues = (props.modelValue[i] || '').trim() ? bulletIssues(props.modelValue[i]) : []
        return h('div', { class: 'mb-2' }, [
          h('div', { class: 'd-flex gap-1' }, [
            h('textarea', { class: 'form-control form-control-sm', rows: 2, maxlength: 400, value: props.modelValue[i], placeholder: 'Start with an action verb and add a real number, e.g. “Built … used by 40 students”', 'aria-label': `Bullet ${i + 1}`, onInput: (e) => { props.modelValue[i] = e.target.value } }),
            h('div', { class: 'd-flex flex-column gap-1' }, [
              props.ai ? h('button', { class: 'btn btn-soft btn-sm', title: 'Improve with Saathi AI', 'aria-label': 'Improve with Saathi AI', disabled: busy.value === i, onClick: () => improve(i) }, [busy.value === i ? h(Loader2, { size: 14, class: 'spin' }) : h(Sparkles, { size: 14 })]) : null,
              h('button', { class: 'btn btn-ghost btn-sm', 'aria-label': 'Remove bullet', onClick: () => props.modelValue.splice(i, 1) }, [h(X, { size: 14 })]),
            ]),
          ]),
          issues.length ? h('div', { class: 'd-flex flex-wrap gap-1 mt-1' }, issues.map((is) => h('span', { class: 'fs-badge fs-badge-pending', style: 'white-space: normal' }, is.label))) : null,
          suggestions[i] ? h('div', { class: 'mt-1 p-2 rounded-3', style: 'background: var(--fs-primary-50)' }, [
            h('div', { class: 'small fw-bold mb-1' }, ['AI suggestions ', h('span', { class: 'fs-badge fs-badge-ai' }, 'AI guidance — check every word is true')]),
            ...suggestions[i].map((sug) => h('button', { class: 'd-block w-100 text-start btn btn-ghost btn-sm mb-1', style: 'white-space: normal', onClick: () => { props.modelValue[i] = sug; delete suggestions[i] } }, sug)),
          ]) : null,
        ])
      }),
      props.modelValue.length < 8 ? h('button', { class: 'btn btn-soft btn-sm', onClick: () => props.modelValue.push('') }, [h(Plus, { size: 14 }), ' Add bullet']) : null,
    ])
  },
}

function move(list, i, dir) {
  const j = i + dir
  if (j < 0 || j >= list.length) return
  const [x] = list.splice(i, 1)
  list.splice(j, 0, x)
}

// ---- load / save ----------------------------------------------------------------
let ready = false
async function load() {
  loading.value = true; error.value = ''; ready = false
  try {
    const res = await api.get(`/resumes/${route.params.id}`)
    const x = res.resume
    Object.assign(r, { id: x.id, title: x.title, target_role: x.target_role || '', template: x.template })
    Object.assign(d, emptyResume(), x.data || {})
    d.basics = { ...emptyResume().basics, ...(x.data?.basics || {}), links: [...(x.data?.basics?.links || [])] }
    aiConfigured.value = !!res.ai_configured
    if (route.query.match) { panel.value = 'match'; tab.value = 'match' }
  } catch (e) { error.value = e.message } finally { loading.value = false; setTimeout(() => { ready = true }, 0) }
}
let timer = null
const payload = () => ({ title: r.title.trim() || 'Untitled resume', target_role: r.target_role.trim() || null, template: r.template, data: JSON.parse(JSON.stringify(d)) })
async function save() {
  saveState.value = 'saving'
  try {
    await api.put(`/resumes/${r.id}`, payload())
    saveState.value = 'saved'
  } catch (e) {
    saveState.value = 'error'
    if (e.status === 422) ui.toast(Object.values(e.fields || {})[0] ? 'Some text is too long — please shorten it.' : e.message, 'error')
    else ui.error(e)
  }
}
watch([() => JSON.stringify(d), () => r.title, () => r.target_role, () => r.template], () => {
  if (!ready) return
  saveState.value = 'saving'
  clearTimeout(timer)
  timer = setTimeout(save, 800)
})
watch(matchOppId, async (id) => {
  detailText.value = ''
  if (!id) return
  const o = opportunities.value.find((x) => String(x.id) === id)
  if (!o) return
  try { detailText.value = opportunityText((await api.get(`/opportunities/${o.slug}`)).opportunity) } catch { detailText.value = opportunityText(o) }
})

const onResize = () => { isDesktop.value = window.matchMedia('(min-width: 992px)').matches }
// Autosave waits 0.8 s after typing stops. If the page is reloaded or closed in that window,
// save straight away so nothing typed is lost.
function flushOnExit() {
  if (!r.id || saveState.value !== 'saving') return
  clearTimeout(timer)
  api.putNow(`/resumes/${r.id}`, payload())
}
function onVisibility() {
  if (document.visibilityState === 'hidden' && saveState.value === 'saving') { clearTimeout(timer); save() }
}
onMounted(async () => {
  window.addEventListener('pagehide', flushOnExit)
  window.addEventListener('beforeunload', flushOnExit)
  document.addEventListener('visibilitychange', onVisibility)
  if (!document.getElementById('resume-css')) {
    const st = document.createElement('style'); st.id = 'resume-css'; st.textContent = RESUME_CSS; document.head.appendChild(st)
  }
  window.addEventListener('resize', onResize)
  await load()
  try {
    opportunities.value = (await api.get('/opportunities', { status: 'all', per_page: 48 })).items
    if (matchOppId.value) { const id = matchOppId.value; matchOppId.value = ''; matchOppId.value = id }
  } catch { /* matching from pasted text still works */ }
})
onBeforeUnmount(() => {
  window.removeEventListener('resize', onResize)
  window.removeEventListener('pagehide', flushOnExit)
  window.removeEventListener('beforeunload', flushOnExit)
  document.removeEventListener('visibilitychange', onVisibility)
  if (saveState.value === 'saving') { clearTimeout(timer); save() }
})

function fileName() { return (d.basics.name || r.title || 'Resume').trim().replace(/[^\w\- ]+/g, '').replace(/\s+/g, '_') + '_Resume' }
function exportPdf() { printResume(JSON.parse(JSON.stringify(d)), r.template, fileName()) }
function exportTxt() { downloadText(`${fileName()}.txt`, resumeText(d)) }
</script>
