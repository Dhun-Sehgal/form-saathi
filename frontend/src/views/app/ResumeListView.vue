<template>
  <div>
    <section class="welcome-banner mb-4">
      <div class="d-flex align-items-center gap-4">
        <div class="flex-grow-1 min-w-0">
          <h1 class="page-title mb-1">ATS Resume Builder</h1>
          <p class="page-sub mb-3">Build a clean, one-column resume that applicant tracking systems can read — then check it against any internship or job on FormSaathi.</p>
          <button class="btn btn-white btn-pill" :disabled="busy" @click="openNew"><Plus :size="17" /> New resume</button>
        </div>
        <div class="d-none d-md-block flex-shrink-0 bg-surface rounded-xl p-2 float" style="transform: rotate(3deg); box-shadow: 0 24px 50px -28px rgba(27,23,64,.7)"><SpotArt name="checklist" style="width: 170px" /></div>
      </div>
    </section>

    <div v-if="matchTitle" class="alert d-flex gap-2 align-items-center" style="background: var(--fs-primary-50); color: var(--fs-text)">
      <Target :size="18" style="color: var(--fs-primary)" /> <span>Tailoring for <strong>{{ matchTitle }}</strong> — open a resume (or create one) to see how well it matches.</span>
    </div>

    <div class="row g-3 mb-4">
      <div v-for="f in features" :key="f.title" class="col-sm-6 col-lg-3">
        <div class="feature-tile h-100"><span class="icon-tile icon-tile-sm" :class="f.tint"><component :is="f.icon" /></span><div><div class="fw-bold small">{{ f.title }}</div><div class="small text-muted">{{ f.text }}</div></div></div>
      </div>
    </div>

    <h2 class="h5 fw-bold mb-3">Your resumes</h2>
    <StateBlock v-if="loading" kind="loading" :count="2" />
    <StateBlock v-else-if="error" kind="error" :message="error" @retry="load" />
    <StateBlock v-else-if="!items.length" title="No resumes yet" message="Start from your FormSaathi profile — your name, college, marks and skills are filled in for you.">
      <button class="btn btn-primary btn-pill" @click="openNew"><Plus :size="16" /> Create my first resume</button>
    </StateBlock>
    <div v-else class="row g-3">
      <div v-for="r in items" :key="r.id" class="col-md-6 col-xl-4">
        <div class="fs-card fs-card-hover fs-card-pad h-100 d-flex flex-column">
          <div class="d-flex align-items-start gap-3 mb-2">
            <span class="icon-tile icon-tile-sm tint-lavender"><ScrollText /></span>
            <div class="min-w-0 flex-grow-1">
              <router-link :to="editorLink(r)" class="fw-bold text-decoration-none d-block text-truncate" style="color: var(--fs-text)">{{ r.title }}</router-link>
              <div class="small text-muted text-truncate">{{ r.target_role || 'General resume' }}</div>
            </div>
            <span class="fs-chip text-capitalize">{{ r.template }}</span>
          </div>
          <div class="small text-muted mb-3">Edited {{ timeAgo(r.updated_at) }}</div>
          <div class="mt-auto d-flex gap-2">
            <router-link :to="editorLink(r)" class="btn btn-primary btn-sm flex-grow-1"><PenLine :size="15" /> Open</router-link>
            <button class="btn btn-soft btn-sm" :aria-label="'Duplicate ' + r.title" @click="duplicate(r)"><Copy :size="15" /></button>
            <button class="btn btn-ghost btn-sm" :aria-label="'Delete ' + r.title" @click="remove(r)"><Trash2 :size="15" /></button>
          </div>
        </div>
      </div>
    </div>

    <AppModal :open="newOpen" title="New resume" subtitle="You can change everything later." @close="newOpen = false">
      <div class="d-grid gap-3">
        <div><label class="form-label" for="rt">Resume name</label><input id="rt" v-model="form.title" class="form-control" maxlength="120" placeholder="e.g. Data Science internships" /></div>
        <div><label class="form-label" for="rr">Target role <span class="text-muted fw-normal">(optional)</span></label><input id="rr" v-model="form.target_role" class="form-control" maxlength="120" placeholder="e.g. Data Analyst Intern" /></div>
        <div><span class="form-label d-block">Style</span>
          <div class="d-flex gap-2"><label v-for="tpl in ['classic', 'modern']" :key="tpl" class="choice-chip text-capitalize" :class="{ active: form.template === tpl }"><input v-model="form.template" type="radio" :value="tpl" />{{ tpl }}</label></div>
        </div>
        <label class="form-check"><input v-model="form.from_profile" type="checkbox" class="form-check-input" /> Fill in from my FormSaathi profile <span class="text-muted small">(name, email, college, marks, skills)</span></label>
      </div>
      <template #footer><button class="btn btn-ghost" @click="newOpen = false">Cancel</button><button class="btn btn-primary" :disabled="busy || !form.title.trim()" @click="create">Create resume</button></template>
    </AppModal>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Copy, FileDown, ListChecks, PenLine, Plus, ScanSearch, ScrollText, Target, Trash2 } from 'lucide-vue-next'
import api from '@/api'
import { useUi } from '@/stores/ui'
import { timeAgo } from '@/utils/format'
import AppModal from '@/components/AppModal.vue'
import StateBlock from '@/components/StateBlock.vue'
import SpotArt from '@/components/art/SpotArt.vue'

const route = useRoute()
const router = useRouter()
const ui = useUi()
const items = ref([])
const loading = ref(true)
const error = ref('')
const busy = ref(false)
const newOpen = ref(false)
const matchTitle = ref('')
const form = reactive({ title: '', target_role: '', template: 'classic', from_profile: true })
const features = [
  { icon: ListChecks, title: 'ATS readiness checks', text: '15 clear checks: contact, verbs, numbers, length and more.', tint: 'tint-mint' },
  { icon: Target, title: 'Match any opportunity', text: 'See which keywords from an internship or job you’re missing.', tint: 'tint-peach' },
  { icon: ScanSearch, title: 'Bullet coach', text: 'Tips on every bullet — and AI rewrites when Saathi AI is on.', tint: 'tint-lavender' },
  { icon: FileDown, title: 'PDF & text export', text: 'One-column, real-text PDF that ATS parsers can read.', tint: 'tint-sky' },
]
const editorLink = (r) => ({ path: `/app/resume/${r.id}`, query: route.query.match ? { match: route.query.match } : {} })

async function load() {
  loading.value = true; error.value = ''
  try { items.value = (await api.get('/resumes')).items } catch (e) { error.value = e.message } finally { loading.value = false }
}
onMounted(async () => {
  load()
  if (route.query.match) {
    try { matchTitle.value = (await api.get('/opportunities', { status: 'all', per_page: 48 })).items.find((o) => String(o.id) === String(route.query.match))?.title || '' } catch { /* optional */ }
  }
})
function openNew() { Object.assign(form, { title: matchTitle.value ? `Resume for ${matchTitle.value}`.slice(0, 120) : 'My resume', target_role: '', template: 'classic', from_profile: true }); newOpen.value = true }
async function create() {
  busy.value = true
  try {
    const r = (await api.post('/resumes', { ...form, title: form.title.trim(), target_role: form.target_role.trim() || null })).resume
    newOpen.value = false
    router.push(editorLink(r))
  } catch (e) { ui.error(e) } finally { busy.value = false }
}
async function duplicate(r) { try { await api.post(`/resumes/${r.id}/duplicate`); ui.toast('Copy created.'); load() } catch (e) { ui.error(e) } }
async function remove(r) {
  if (!(await ui.confirm({ title: `Delete “${r.title}”?`, message: 'This resume will be permanently deleted.', confirmText: 'Delete', danger: true }))) return
  try { await api.delete(`/resumes/${r.id}`); ui.toast('Resume deleted.'); load() } catch (e) { ui.error(e) }
}
</script>
