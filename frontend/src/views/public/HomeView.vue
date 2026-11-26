<template>
  <!-- HERO: warm desk photo, centred headline and search -------------------------->
  <section class="hero-photo">
    <div class="container text-center position-relative">
      <h1 class="hero-title text-balance mx-auto mb-3">{{ t('hero.title1') }} <span class="hero-accent">{{ t('hero.title2') }}</span></h1>
      <p class="hero-sub mb-4">{{ t('hero.sub') }}</p>
      <form class="smart-search hero-search mb-3" role="search" @submit.prevent="search">
        <Search :size="20" class="text-muted flex-shrink-0" />
        <input v-model="q" type="search" :placeholder="t('hero.search')" aria-label="Search opportunities" />
        <button class="btn btn-primary btn-pill" type="submit"><span class="d-none d-sm-inline">{{ t('common.search') }}</span><ArrowRight class="d-sm-none" :size="18" /></button>
      </form>
      <div class="d-flex flex-wrap justify-content-center align-items-center gap-2">
        <span class="small fw-semibold hero-popular">Popular:</span>
        <router-link v-for="c in quickCats" :key="c.slug" :to="{ path: '/explore', query: { category: c.slug } }" class="fs-badge text-decoration-none py-1 px-3" :class="`tint-${c.color}`" style="font-size: .8rem">{{ c.name }}</router-link>
      </div>
    </div>
  </section>

  <!-- BAND --------------------------------------------------------------------->
  <section class="hero-band" aria-label="How FormSaathi helps">
    <div class="container">
      <p class="band-words mb-0"><Sparkles :size="22" class="band-spark" aria-hidden="true" /> Discover <span class="sep" aria-hidden="true">|</span> Check <span class="sep" aria-hidden="true">|</span> Apply</p>
      <span class="band-divider d-none d-md-block" aria-hidden="true" />
      <router-link to="/register" class="btn btn-band btn-pill">Join FormSaathi <ArrowRight :size="18" /></router-link>
    </div>
  </section>

  <!-- ABOUT + WHAT YOU GET --------------------------------------------------------->
  <section id="about" class="section">
    <div class="container">
      <div class="text-center mx-auto mb-5" style="max-width: 720px">
        <h2 class="about-title mb-3"><em>About</em> FormSaathi</h2>
        <p class="section-lead mx-auto mb-0">One place to find the scholarships, internships, government schemes and jobs you are eligible for — and to prepare every application with confidence.</p>
      </div>
      <div class="row g-4">
        <div v-for="p in pillars" :key="p.title" class="col-md-6">
          <article class="plate" :class="`plate-${p.color}`">
            <div class="plate-head">
              <span class="plate-icon"><component :is="p.icon" aria-hidden="true" /></span>
              <div class="plate-stat"><span class="num">{{ p.stat }}</span><span class="lbl">{{ p.statLabel }}</span></div>
            </div>
            <h3 class="plate-title">{{ p.title }}</h3>
            <p class="plate-text">{{ p.text }}</p>
            <ul class="plate-list">
              <li v-for="b in p.points" :key="b">{{ b }}</li>
            </ul>
            <div class="plate-tags"><span v-for="tag in p.tags" :key="tag" class="pill">{{ tag }}</span></div>
            <div class="plate-foot">
              <router-link v-if="p.noteTo" :to="p.noteTo" class="small fw-semibold">{{ p.note }} →</router-link>
              <span v-else class="small text-muted">{{ p.note }}</span>
              <router-link :to="p.to" class="btn btn-primary btn-sm btn-pill">{{ p.cta }} <ArrowRight :size="15" /></router-link>
            </div>
          </article>
        </div>
      </div>
    </div>
  </section>

  <!-- CATEGORIES ----------------------------------------------------------------->
  <section class="section pt-0">
    <div class="container">
      <div class="d-flex align-items-end justify-content-between flex-wrap gap-3 mb-4">
        <div>
          <span class="section-eyebrow"><Shapes :size="14" /> Explore by category</span>
          <h2 class="section-title mt-2 mb-1">Everything you might be missing</h2>
          <p class="section-lead mb-0">Scholarships, internships, schemes and more — in one place.</p>
        </div>
        <router-link to="/explore" class="btn btn-outline-primary btn-pill">Browse all <ArrowRight :size="16" /></router-link>
      </div>
      <div class="row g-3">
        <div v-for="c in meta.categories" :key="c.slug" class="col-6 col-lg-3">
          <router-link :to="{ path: '/explore', query: { category: c.slug } }" class="plate plate-compact text-decoration-none" :class="`plate-${c.color}`">
            <span class="plate-icon plate-icon-sm"><CategoryIconGlyph :name="c.icon" /></span>
            <div class="plate-title">{{ c.name }}</div>
            <div class="plate-text small mb-0 d-none d-sm-block">{{ c.description }}</div>
          </router-link>
        </div>
      </div>
    </div>
  </section>

  <!-- HOW IT WORKS --------------------------------------------------------------->
  <section id="how" class="section section-wash">
    <div class="container">
      <div class="text-center mb-5">
        <span class="section-eyebrow"><Route :size="14" /> How it works</span>
        <h2 class="section-title mt-2 mb-2">From “Am I eligible?” to “Applied!”</h2>
        <p class="section-lead mx-auto mb-0">Four simple steps. You always apply on the official website.</p>
      </div>
      <div class="row g-4">
        <div v-for="(s, i) in steps" :key="s.title" class="col-sm-6 col-lg-3">
          <article class="plate plate-step" :class="`plate-${s.color}`">
            <div class="plate-head mb-3">
              <span class="plate-icon plate-icon-sm"><component :is="s.icon" aria-hidden="true" /></span>
              <div class="plate-stat"><span class="num">{{ String(i + 1).padStart(2, '0') }}</span></div>
            </div>
            <h3 class="plate-title h6">{{ s.title }}</h3>
            <p class="plate-text small mb-0">{{ s.text }}</p>
          </article>
        </div>
      </div>
    </div>
  </section>

  <!-- OPEN NOW -------------------------------------------------------------------->
  <section class="section">
    <div class="container">
      <div class="d-flex align-items-end justify-content-between flex-wrap gap-3 mb-3">
        <div><span class="section-eyebrow"><Flame :size="14" /> Featured</span><h2 class="section-title mt-2 mb-0">Open right now</h2></div>
        <router-link to="/explore" class="btn btn-outline-primary btn-pill">{{ t('common.viewAll') }} <ArrowRight :size="16" /></router-link>
      </div>
      <p class="source-note mb-4"><BadgeCheck :size="18" class="flex-shrink-0" /> <span>Every listing comes from an <strong>official source</strong> — ministries, AICTE, UGC, RBI, UPSC and others — and shows when it was last verified. Always confirm dates on the official site before applying.</span></p>
      <StateBlock v-if="loading" kind="loading" />
      <StateBlock v-else-if="error" kind="error" message="We couldn't load featured opportunities." @retry="load" />
      <div v-else class="row g-3">
        <div v-for="o in featured" :key="o.id" class="col-md-6 col-xl-4"><OpportunityCard :o="o" /></div>
      </div>
    </div>
  </section>

  <!-- FAQ -------------------------------------------------------------------------->
  <section class="section pt-0">
    <div class="container" style="max-width: 820px">
      <div class="text-center mb-4"><span class="section-eyebrow"><MessageCircleQuestion :size="14" /> FAQ</span><h2 class="section-title mt-2">Questions, answered</h2></div>
      <div class="accordion" id="faq">
        <div v-for="(f, i) in faqs" :key="i" class="accordion-item">
          <h3 class="accordion-header">
            <button class="accordion-button" :class="{ collapsed: openFaq !== i }" :aria-expanded="openFaq === i" @click="openFaq = openFaq === i ? -1 : i">{{ f.q }}</button>
          </h3>
          <div v-show="openFaq === i" class="accordion-collapse"><div class="accordion-body text-muted pt-0">{{ f.a }}</div></div>
        </div>
      </div>
    </div>
  </section>

  <!-- CTA -------------------------------------------------------------------------->
  <section class="pb-5">
    <div class="container">
      <div class="cta-band text-center">
        <h2 class="section-title mb-2">Your opportunities are waiting.</h2>
        <p class="lead-text mx-auto mb-4" style="max-width: 560px">Create a free profile in 3 minutes. Optional details stay optional — and you can delete everything any time.</p>
        <div class="d-flex flex-wrap gap-2 justify-content-center">
          <router-link to="/register" class="btn btn-primary btn-lg btn-pill">{{ t('hero.start') }} <ArrowRight :size="18" /></router-link>
          <router-link to="/explore" class="btn btn-outline-primary btn-lg btn-pill bg-surface">{{ t('hero.explore') }}</router-link>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed, h, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import {
  ArrowRight, Award, BadgeCheck, Briefcase, Building2, Compass, FilePenLine, Flame, GraduationCap, HandCoins, KanbanSquare,
  Landmark, Languages, ListChecks, MessageCircleQuestion, Route, Scale, ScrollText, Search, Shapes, Sparkles, UserRound, Wrench,
} from 'lucide-vue-next'
import api from '@/api'
import { useMeta } from '@/stores/meta'
import OpportunityCard from '@/components/OpportunityCard.vue'
import StateBlock from '@/components/StateBlock.vue'
import { analyze, emptyResume } from '@/utils/ats'
import { LABELS } from '@/utils/format'

const { t } = useI18n()
const meta = useMeta()
const router = useRouter()
const q = ref('')
const featured = ref([])
const openNow = ref(null)
const loading = ref(true)
const error = ref(false)
const openFaq = ref(0)
const quickCats = computed(() => meta.categories.slice(0, 4))

// Category glyph only (the plate draws the tile around it).
const GLYPHS = { 'graduation-cap': GraduationCap, briefcase: Briefcase, award: Award, landmark: Landmark, 'file-pen-line': FilePenLine, 'building-2': Building2, wrench: Wrench, 'hand-coins': HandCoins }
const CategoryIconGlyph = (props) => h(GLYPHS[props.name] || Sparkles, { 'aria-hidden': 'true' })
CategoryIconGlyph.props = ['name']

function search() { router.push({ path: '/explore', query: q.value.trim() ? { q: q.value.trim() } : {} }) }
async function load() {
  loading.value = true; error.value = false
  try { featured.value = (await api.get('/opportunities/featured')).items } catch { error.value = true } finally { loading.value = false }
}
async function loadCount() {
  // Live count of verified listings that are open today (drops as deadlines pass).
  try { openNow.value = (await api.get('/opportunities', { verified: '1', per_page: 1 })).total } catch { openNow.value = null }
}
onMounted(() => { load(); loadCount() })

// Every number below comes from the product itself, not from marketing copy.
const atsChecks = analyze(emptyResume()).total
const ruleTypes = Object.keys(LABELS.criterion).filter((k) => k !== 'custom').length

const pillars = computed(() => [
  {
    color: 'lavender', icon: BadgeCheck, stat: openNow.value ?? '—', statLabel: 'verified & open now',
    title: 'Real opportunities, checked at the source',
    text: 'Scholarships, internships, government schemes and jobs, each linked to its official page with the date it was last checked.',
    points: ['Official sources like UGC, AICTE, RBI and NITI Aayog', 'Deadlines, benefits and documents in one place', 'Clear labels: verified, pending or expired'],
    tags: ['Scholarships', 'Internships', 'Schemes', 'Jobs'], note: 'Free to browse', cta: 'Explore', to: '/explore',
  },
  {
    color: 'mint', icon: Scale, stat: ruleTypes, statLabel: 'kinds of rules checked',
    title: 'Know where you stand, rule by rule',
    text: 'Each official rule is checked against your profile and shown with the wording it came from — never a made-up score.',
    points: ['Met, not met or needs info for every rule', 'Income, marks, category, state, age and more', 'Optional details stay optional'],
    tags: ['Eligibility', 'Official wording'], note: 'Takes a minute', cta: 'Check yours', to: '/register',
  },
  {
    color: 'sky', icon: Languages, stat: 3, statLabel: 'languages',
    title: 'Help in your language',
    text: 'Use FormSaathi in English, हिन्दी or मराठी. Saathi AI explains forms and difficult terms in simple words.',
    points: ['Switch language any time', 'Plain-language explanations', 'Always confirm on the official site'],
    tags: ['English', 'हिन्दी', 'मराठी'], note: 'Guidance, not official advice', cta: 'How it works', to: '/how-it-works',
  },
  {
    color: 'butter', icon: ScrollText, stat: atsChecks, statLabel: 'resume checks',
    title: 'ATS resume builder',
    text: 'Build a clean one-column resume that applicant tracking systems can read — or upload yours to see its ATS score and what to fix.',
    points: [`${atsChecks} transparent readiness checks and a score out of 100`, 'Upload the resume you already have to check it', 'Keyword match for any opportunity'],
    tags: ['Resume', 'ATS score', 'PDF'], note: 'Check an existing resume', noteTo: '/app/resume/check', cta: 'Build resume', to: '/app/resume',
  },
])

const steps = [
  { color: 'lavender', icon: UserRound, title: 'Create your profile', text: 'Education, location and interests. Sensitive details are optional and explained.' },
  { color: 'mint', icon: Compass, title: 'Discover matches', text: 'Opportunities that fit you, with clear reasons why they were recommended.' },
  { color: 'sky', icon: ListChecks, title: 'Check & prepare', text: 'Rule-by-rule eligibility and a document checklist for each opportunity.' },
  { color: 'butter', icon: KanbanSquare, title: 'Apply & track', text: 'Apply on the official site, then track status, notes and reminders.' },
]

const faqs = [
  { q: 'Is FormSaathi free?', a: 'Yes. Creating a profile, discovering opportunities, checking eligibility and tracking applications are free.' },
  { q: 'Does FormSaathi submit applications for me?', a: 'No. You always apply on the official website. FormSaathi helps you prepare, and you confirm in your tracker when you have applied.' },
  { q: 'How do you make sure information is correct?', a: 'Each opportunity links to its official source and shows when it was last verified. Listings that are not yet verified are labelled, and you can report a correction on any listing.' },
  { q: 'Why do you ask about income or category?', a: 'Many scholarships and schemes depend on them. These fields are optional — if you skip them, eligibility checks simply show “more information needed” for those rules.' },
  { q: 'Is Saathi AI official advice?', a: 'No. Saathi AI explains things in simple language, but it is not a government official. Always confirm on the official source before applying.' },
]
</script>
