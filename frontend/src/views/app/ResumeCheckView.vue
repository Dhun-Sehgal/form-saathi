<!-- Check a resume you already have: read it in the browser (nothing is uploaded), run the same
     transparent ATS checks as the builder, and show the score, the reasons and what an ATS reads. -->
<template>
  <div>
    <section class="welcome-banner mb-4">
      <div class="d-flex align-items-center gap-4">
        <div class="flex-grow-1 min-w-0">
          <h1 class="page-title mb-1">Check your resume’s ATS score</h1>
          <p class="page-sub mb-3">Upload the resume you already have. We read it the way an applicant tracking system does and show exactly what to fix.</p>
          <p class="small mb-0 d-flex align-items-center gap-2" style="color: var(--fs-muted-strong)"><ShieldCheck :size="16" /> Your file is read in this browser and never uploaded.</p>
        </div>
        <div class="d-none d-md-block flex-shrink-0 bg-surface rounded-xl p-2 float" style="transform: rotate(-3deg); box-shadow: var(--fs-shadow-lg)"><SpotArt name="checklist" style="width: 160px" /></div>
      </div>
    </section>

    <div class="row g-4">
      <!-- Input -->
      <div class="col-lg-5">
        <div class="fs-card fs-card-pad resume-side">
          <h2 class="h6 fw-bold mb-3">1. Add your resume</h2>
          <label class="drop-zone" :class="{ over: dragOver }" for="resume-file"
                 @dragover.prevent="dragOver = true" @dragleave.prevent="dragOver = false" @drop.prevent="onDrop">
            <FileUp :size="26" aria-hidden="true" />
            <span class="fw-bold">{{ fileName || 'Drop your resume here or browse' }}</span>
            <span class="small text-muted">PDF, Word (.docx) or .txt · up to 5 MB</span>
            <input id="resume-file" ref="fileInput" type="file" class="visually-hidden" :accept="ACCEPTED_RESUME_TYPES" @change="onPick" />
          </label>

          <button class="btn btn-link btn-sm px-0 mt-2" type="button" :aria-expanded="showPaste" @click="showPaste = !showPaste">
            <ClipboardPaste :size="15" /> {{ showPaste ? 'Hide pasted text' : 'Or paste the text instead' }}
          </button>
          <textarea v-if="showPaste" v-model="pasted" class="form-control mt-1" rows="7" aria-label="Resume text" placeholder="Paste the full text of your resume here" @input="source = 'paste'; fileName = ''" />

          <h2 class="h6 fw-bold mt-4 mb-2">2. Compare with a job <span class="text-muted fw-normal">(optional)</span></h2>
          <select v-model="matchOppId" class="form-select form-select-sm mb-2" aria-label="Choose an opportunity">
            <option value="">Choose an internship, job or fellowship on FormSaathi…</option>
            <option v-for="o in opportunities" :key="o.id" :value="String(o.id)">{{ o.title }}</option>
          </select>
          <textarea v-model="jobText" class="form-control form-control-sm" rows="3" aria-label="Job description" placeholder="…or paste any job description" />

          <div v-if="error" class="alert alert-danger small d-flex gap-2 mt-3 mb-0" role="alert"><CircleAlert :size="17" class="flex-shrink-0 mt-1" /> <span>{{ error }}</span></div>
          <button class="btn btn-primary btn-pill w-100 mt-3" :disabled="busy || !canCheck" @click="check">
            <Loader2 v-if="busy" :size="17" class="spin" /><ScanSearch v-else :size="17" /> {{ busy ? 'Reading your resume…' : 'Check my resume' }}
          </button>
        </div>
      </div>

      <!-- Results -->
      <div class="col-lg-7" aria-live="polite">
        <div v-if="!result" class="fs-card">
          <StateBlock title="Your ATS score will appear here" message="Add your resume on the left and press “Check my resume”. You get a score out of 100, every check behind it, and tips for each bullet." />
        </div>

        <template v-else>
          <section class="fs-card fs-card-pad mb-3">
            <div class="d-flex flex-wrap align-items-center gap-3">
              <ProgressRing :value="result.score" :size="96" :stroke="9" />
              <div class="flex-grow-1 min-w-0">
                <div class="d-flex flex-wrap align-items-center gap-2 mb-1">
                  <h2 class="h5 fw-bold mb-0">ATS score {{ result.score }}/100</h2>
                  <span class="fs-badge" :class="`fs-badge-${band.tone}`">{{ band.label }}</span>
                </div>
                <p class="small text-muted mb-1">{{ result.passed }} of {{ result.total }} checks passed<span v-if="!result.unreadable"> · {{ result.stats.words }} words · {{ result.stats.bullets }} bullets · {{ result.stats.skills }} skills<span v-if="result.stats.pages"> · {{ result.stats.pages }} page{{ result.stats.pages === 1 ? '' : 's' }}</span></span></p>
                <p class="small text-muted mb-0 text-truncate" :title="checkedName">{{ checkedName }}</p>
              </div>
            </div>
            <details class="small mt-3">
              <summary class="fw-semibold" style="cursor: pointer">How this score works</summary>
              <p class="text-muted mt-2 mb-0">Each check below counts equally: pass = 1 point, warning = ½, fail = 0. The score is those points out of 100. Real applicant tracking systems differ between companies, so treat it as a readiness guide, not a prediction — and never add numbers or skills you don’t really have.</p>
            </details>
          </section>

          <section class="fs-card fs-card-pad mb-3">
            <h2 class="h6 fw-bold mb-2">What we checked</h2>
            <ul class="list-unstyled mb-0">
              <li v-for="c in sortedChecks" :key="c.id" class="crit-row py-2">
                <span class="crit-icon" :class="c.status === 'pass' ? 'crit-met' : c.status === 'fail' ? 'crit-not_met' : 'crit-unknown'"><Check v-if="c.status === 'pass'" /><X v-else-if="c.status === 'fail'" /><AlertTriangle v-else /></span>
                <div><div class="fw-semibold small">{{ c.label }}</div><div class="small text-muted">{{ c.detail }}</div></div>
              </li>
            </ul>
          </section>

          <section v-if="match" class="fs-card fs-card-pad mb-3">
            <div class="d-flex justify-content-between align-items-center mb-2"><h2 class="h6 fw-bold mb-0">Keyword match</h2><span class="fs-badge fs-badge-ai">{{ match.percent }}%</span></div>
            <p class="small text-muted">{{ match.matched.length }} of {{ match.keywords.length }} important words from the job appear in your resume. Add the missing ones only where they are true for you.</p>
            <div v-if="match.matched.length" class="d-flex flex-wrap gap-1 mb-2"><span v-for="k in match.matched" :key="k" class="fs-badge fs-badge-verified"><Check /> {{ k }}</span></div>
            <div v-if="match.missing.length" class="d-flex flex-wrap gap-1"><span v-for="k in match.missing" :key="k" class="fs-badge fs-badge-pending">{{ k }}</span></div>
          </section>

          <section v-if="result.tips.length" class="fs-card fs-card-pad mb-3">
            <h2 class="h6 fw-bold mb-1">Bullets to improve</h2>
            <p class="small text-muted">{{ result.tips.length }} of {{ result.stats.bullets }} bullets could be stronger.</p>
            <ul class="list-unstyled d-grid gap-2 mb-0">
              <li v-for="tip in result.tips.slice(0, showAllTips ? undefined : 5)" :key="tip.i" class="p-2 rounded-3" style="background: var(--fs-surface-2)">
                <div class="small mb-1">{{ tip.text }}</div>
                <div class="d-flex flex-wrap gap-1"><span v-for="is in tip.issues" :key="is.code" class="fs-badge fs-badge-pending" style="white-space: normal">{{ is.label }}</span></div>
              </li>
            </ul>
            <button v-if="result.tips.length > 5" class="btn btn-link btn-sm px-0 mt-1" @click="showAllTips = !showAllTips">{{ showAllTips ? 'Show fewer' : `Show all ${result.tips.length}` }}</button>
          </section>

          <section class="fs-card fs-card-pad mb-3">
            <details>
              <summary class="h6 fw-bold mb-0" style="cursor: pointer">What an ATS reads from your file</summary>
              <p class="small text-muted mt-2">This is the text we got out of your resume, in reading order. If parts are missing, jumbled or shown as “�”, an ATS will likely have the same problem.</p>
              <pre class="ats-text mb-0">{{ extracted.slice(0, 6000) }}<template v-if="extracted.length > 6000">…</template></pre>
            </details>
          </section>

          <div class="fs-card fs-card-pad d-flex flex-wrap align-items-center gap-3">
            <div class="flex-grow-1"><div class="fw-bold">Want a resume that passes these checks?</div><div class="small text-muted">Build a clean one-column resume from your FormSaathi profile and export it as a PDF.</div></div>
            <router-link to="/app/resume" class="btn btn-primary btn-pill">Open the builder <ArrowRight :size="16" /></router-link>
          </div>
        </template>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { AlertTriangle, ArrowRight, Check, CircleAlert, ClipboardPaste, FileUp, Loader2, ScanSearch, ShieldCheck, X } from 'lucide-vue-next'
import api from '@/api'
import ProgressRing from '@/components/ProgressRing.vue'
import StateBlock from '@/components/StateBlock.vue'
import SpotArt from '@/components/art/SpotArt.vue'
import { analyzeText, matchKeywordsText, opportunityText, scoreBand } from '@/utils/ats'
import { ACCEPTED_RESUME_TYPES, readResumeFile, ResumeFileError } from '@/utils/resumeFile'

const fileInput = ref(null)
const file = ref(null)
const fileName = ref('')
const pasted = ref('')
const showPaste = ref(false)
const source = ref('file')
const dragOver = ref(false)
const busy = ref(false)
const error = ref('')
const result = ref(null)
const extracted = ref('')
const checkedName = ref('')
const showAllTips = ref(false)
const opportunities = ref([])
const matchOppId = ref('')
const jobText = ref('')
const detailText = ref('')

const canCheck = computed(() => (source.value === 'paste' ? pasted.value.trim().length > 0 : !!file.value))
const band = computed(() => scoreBand(result.value?.score ?? 0))
const order = { fail: 0, warn: 1, pass: 2 }
const sortedChecks = computed(() => [...(result.value?.checks || [])].sort((a, b) => order[a.status] - order[b.status]))
const match = computed(() => {
  const job = [jobText.value, detailText.value].filter(Boolean).join('\n')
  return result.value && !result.value.unreadable && job.trim() ? matchKeywordsText(extracted.value, job) : null
})

function choose(f) {
  if (!f) return
  file.value = f; fileName.value = f.name; source.value = 'file'; error.value = ''
}
function onPick(e) { choose(e.target.files?.[0]) }
function onDrop(e) { dragOver.value = false; choose(e.dataTransfer?.files?.[0]) }

async function check() {
  error.value = ''; busy.value = true; showAllTips.value = false
  try {
    let text, pages = null, name
    if (source.value === 'paste') { text = pasted.value; name = 'Pasted text' } else {
      const read = await readResumeFile(file.value)
      text = read.text; pages = read.pages; name = read.fileName
    }
    extracted.value = text
    checkedName.value = name
    result.value = analyzeText(text, { pages })
  } catch (e) {
    result.value = null
    error.value = e instanceof ResumeFileError ? e.message : 'Something went wrong while reading this file. Try exporting it again as a PDF, or paste the text instead.'
  } finally {
    busy.value = false
    if (fileInput.value) fileInput.value.value = ''
  }
}

watch(matchOppId, async (id) => {
  detailText.value = ''
  const o = opportunities.value.find((x) => String(x.id) === id)
  if (!o) return
  try { detailText.value = opportunityText((await api.get(`/opportunities/${o.slug}`)).opportunity) } catch { detailText.value = opportunityText(o) }
})

onMounted(async () => {
  try { opportunities.value = (await api.get('/opportunities', { status: 'all', per_page: 48 })).items } catch { opportunities.value = [] }
})
</script>
