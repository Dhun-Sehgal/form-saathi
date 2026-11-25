<template>
  <StateBlock v-if="loading" kind="loading" :count="1" col-class="col-12" />
  <StateBlock v-else-if="error" kind="error" :message="error" @retry="run" />
  <div v-else style="max-width: 900px">
    <router-link :to="`/app/opportunities/${r.opportunity.slug}`" class="small text-muted d-inline-flex align-items-center gap-1 mb-3"><ArrowLeft :size="16" /> {{ r.opportunity.title }}</router-link>
    <h1 class="page-title mb-1">Eligibility check</h1>
    <p class="page-sub mb-4">Your profile compared with each rule of this opportunity. Rules come from the listing’s source; this check is not an official decision.</p>

    <div v-if="r.opportunity.data_origin === 'demo'" class="demo-ribbon mb-3 d-flex gap-2"><FlaskConical :size="18" class="flex-shrink-0 mt-1" /> These are demo rules on a sample listing — useful to see how checks work.</div>

    <div class="verdict mb-4" :class="`verdict-${r.report.verdict}`">
      <span class="icon-tile" style="background: var(--fs-surface)"><component :is="verdictIcon" /></span>
      <div>
        <h2 class="h4 fw-bold mb-1">{{ verdictText }}</h2>
        <p class="mb-2">{{ r.explanation.summary }}</p>
        <span class="fs-badge" :class="r.explanation_source === 'ai' ? 'fs-badge-ai' : 'fs-badge-expired'"><Sparkles v-if="r.explanation_source === 'ai'" /><ListChecks v-else /> {{ r.explanation_source === 'ai' ? 'Explained by AI guidance' : 'Rule-based explanation' }}</span>
      </div>
    </div>

    <div class="row g-4">
      <div class="col-lg-8">
        <section class="fs-card fs-card-pad">
          <h2 class="h6 fw-bold mb-1">Rule by rule</h2>
          <p class="small text-muted mb-2">{{ r.report.counts.met }} met · {{ r.report.counts.not_met }} not met · {{ r.report.counts.unknown }} need info · {{ r.report.counts.needs_review }} need your review</p>
          <ul class="list-unstyled mb-0">
            <li v-for="(c, i) in r.report.results" :key="i" class="crit-row">
              <span class="crit-icon" :class="`crit-${c.outcome}`"><component :is="ICONS[c.outcome]" /></span>
              <div class="min-w-0">
                <div class="fw-semibold">{{ c.description }} <span v-if="!c.is_mandatory" class="fs-chip ms-1">Optional</span></div>
                <div class="small"><span class="fw-semibold">{{ OUTCOME[c.outcome] }}:</span> <span class="text-muted">{{ r.explanation.per_criterion?.[i] || c.reason }}</span></div>
                <div v-if="c.source_excerpt" class="source-quote">Official text: “{{ c.source_excerpt }}”</div>
                <router-link v-if="c.missing_field" to="/app/profile" class="small">Add to profile →</router-link>
              </div>
            </li>
          </ul>
        </section>
      </div>
      <div class="col-lg-4 d-grid gap-3 align-content-start">
        <section class="fs-card fs-card-pad">
          <h2 class="h6 fw-bold">Next steps</h2>
          <ol class="small ps-3 mb-0 d-grid gap-1"><li v-for="s in r.explanation.next_steps" :key="s">{{ s }}</li></ol>
        </section>
        <section class="fs-card fs-card-pad d-grid gap-2">
          <button class="btn btn-primary" @click="track"><KanbanSquare :size="16" /> Track this application</button>
          <button class="btn btn-soft" @click="ask"><Bot :size="16" /> Ask Saathi</button>
          <router-link to="/app/profile" class="btn btn-soft"><UserRound :size="16" /> Update profile</router-link>
          <button class="btn btn-ghost" @click="run"><RotateCcw :size="16" /> Check again</button>
        </section>
        <p v-if="!r.ai_configured" class="small text-muted">Saathi AI isn’t configured on this server, so the explanation above is generated from the rules directly. Results are the same either way — AI only rephrases them.</p>
        <p class="small text-muted">Always confirm on the <a :href="r.opportunity.source_url" target="_blank" rel="noopener">official source</a>.</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ArrowLeft, Bot, CircleCheck, CircleHelp, CircleX, FlaskConical, KanbanSquare, ListChecks, RotateCcw, ScanSearch, Sparkles, UserRound } from 'lucide-vue-next'
import api from '@/api'
import { useAuth } from '@/stores/auth'
import { useUi } from '@/stores/ui'
import StateBlock from '@/components/StateBlock.vue'

const ICONS = { met: CircleCheck, not_met: CircleX, unknown: CircleHelp, needs_review: ScanSearch }
const OUTCOME = { met: 'Met', not_met: 'Not met', unknown: 'More info needed', needs_review: 'Needs your review' }
const route = useRoute()
const router = useRouter()
const auth = useAuth()
const ui = useUi()
const r = ref(null)
const loading = ref(true)
const error = ref('')

async function run() {
  loading.value = true; error.value = ''
  try { r.value = await api.post(`/eligibility/${route.params.id}`, { language: auth.profile.preferred_language || 'en' }) } catch (e) { error.value = e.message } finally { loading.value = false }
}
onMounted(run)
const verdictText = computed(() => ({ eligible: 'You appear to be eligible', possibly_eligible: 'Possibly eligible — more information needed', not_eligible: 'Not eligible based on your profile' })[r.value.report.verdict])
const verdictIcon = computed(() => ({ eligible: CircleCheck, possibly_eligible: CircleHelp, not_eligible: CircleX })[r.value.report.verdict])

async function track() {
  try { const res = await api.post('/applications', { opportunity_id: r.value.opportunity.id }); router.push(`/app/tracker/${res.application.id}`) } catch (e) { ui.error(e) }
}
async function ask() {
  try { const res = await api.post('/ai/sessions', { opportunity_id: r.value.opportunity.id, language: auth.profile.preferred_language || 'en' }); router.push({ path: '/app/saathi', query: { session: res.session.id } }) } catch (e) { ui.error(e) }
}
</script>
