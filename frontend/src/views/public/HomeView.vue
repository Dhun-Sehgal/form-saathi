<template>
  <!-- HERO ------------------------------------------------------------------>
  <section class="hero">
    <div class="container">
      <div class="row align-items-center g-4 g-lg-5">
        <div class="col-lg-6">
          <span class="eyebrow-pill mb-3"><span class="dot"><Sparkles /></span> Your personal opportunity assistant</span>
          <h1 class="hero-title text-balance mb-3">{{ t('hero.title1') }} <span class="hero-highlight">{{ t('hero.title2') }}</span></h1>
          <p class="lead text-muted mb-4" style="max-width: 540px">{{ t('hero.sub') }}</p>
          <form class="smart-search mb-3" role="search" @submit.prevent="search">
            <Search :size="20" class="text-muted flex-shrink-0" />
            <input v-model="q" type="search" :placeholder="t('hero.search')" aria-label="Search opportunities" />
            <button class="btn btn-primary" type="submit"><span class="d-none d-sm-inline">{{ t('common.search') }}</span><ArrowRight class="d-sm-none" :size="18" /></button>
          </form>
          <div class="d-flex flex-wrap align-items-center gap-2 mb-4">
            <span class="small text-muted fw-semibold me-1">Popular:</span>
            <router-link v-for="c in quickCats" :key="c.slug" :to="{ path: '/explore', query: { category: c.slug } }" class="fs-badge text-decoration-none py-1 px-3" :class="`tint-${c.color}`" style="font-size: .8rem">{{ c.name }}</router-link>
          </div>
          <div class="d-flex flex-wrap gap-2 mb-4">
            <router-link to="/register" class="btn btn-primary btn-lg btn-pill">{{ t('hero.start') }} <ArrowRight :size="18" /></router-link>
            <router-link to="/explore" class="btn btn-outline-primary btn-lg btn-pill bg-surface">{{ t('hero.explore') }}</router-link>
          </div>
          <ul class="list-unstyled d-flex flex-wrap gap-3 small text-muted mb-0">
            <li class="d-flex align-items-center gap-1"><CircleCheck :size="17" style="color: var(--fs-success)" /> Free to use</li>
            <li class="d-flex align-items-center gap-1"><CircleCheck :size="17" style="color: var(--fs-success)" /> English · हिन्दी · मराठी</li>
            <li class="d-flex align-items-center gap-1"><CircleCheck :size="17" style="color: var(--fs-success)" /> Your documents stay private</li>
          </ul>
        </div>
        <div class="col-lg-6">
          <div class="mx-auto" style="max-width: 600px"><HeroScene /></div>
        </div>
      </div>
    </div>
  </section>

  <!-- TRUST ------------------------------------------------------------------>
  <section class="pb-4">
    <div class="container">
      <div class="row g-3">
        <div v-for="f in trust" :key="f.title" class="col-6 col-lg-3">
          <div class="trust-item">
            <span class="icon-tile icon-tile-sm" :class="f.tint"><component :is="f.icon" /></span>
            <div class="min-w-0"><div class="fw-bold small">{{ f.title }}</div><div class="text-muted" style="font-size:.78rem">{{ f.text }}</div></div>
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- CATEGORIES ------------------------------------------------------------->
  <section class="section">
    <div class="container">
      <div class="d-flex align-items-end justify-content-between flex-wrap gap-3 mb-4">
        <div>
          <span class="section-eyebrow mb-2"><Shapes :size="14" /> Explore by category</span>
          <h2 class="section-title mt-2 mb-1">Everything you might be missing</h2>
          <p class="section-lead mb-0">Scholarships, internships, schemes and more — in one place, matched to you.</p>
        </div>
        <router-link to="/explore" class="btn btn-soft btn-pill">Browse all <ArrowRight :size="16" /></router-link>
      </div>
      <div class="row g-3">
        <div v-for="c in meta.categories" :key="c.slug" class="col-6 col-md-4 col-lg-3">
          <router-link :to="{ path: '/explore', query: { category: c.slug } }" class="cat-tile" :style="{ '--tile-tint': `var(--tint-${c.color})` }">
            <CategoryIcon :name="c.icon" :color="c.color" />
            <div><div class="cat-name">{{ c.name }}</div><div class="cat-desc d-none d-sm-block">{{ c.description }}</div></div>
          </router-link>
        </div>
      </div>
    </div>
  </section>

  <!-- HOW IT WORKS ----------------------------------------------------------->
  <section id="how" class="section bg-mist">
    <div class="container">
      <div class="text-center mb-5">
        <span class="section-eyebrow"><Route :size="14" /> How it works</span>
        <h2 class="section-title mt-2 mb-2">From “Am I eligible?” to “Applied!” in four steps</h2>
        <p class="section-lead mx-auto mb-0">FormSaathi stays with you through the whole journey — not just the search.</p>
      </div>
      <div class="position-relative">
        <div class="steps-line d-none d-lg-block" />
        <div class="row g-4 position-relative">
          <div v-for="(s, i) in steps" :key="s.title" class="col-sm-6 col-lg-3">
            <div class="step-card">
              <SpotArt :name="s.art" />
              <div class="d-flex align-items-center justify-content-center gap-2 mb-2"><span class="step-num" style="width:2rem;height:2rem;font-size:.9rem;border-radius:.65rem">{{ i + 1 }}</span><h3 class="h6 fw-bold mb-0">{{ s.title }}</h3></div>
              <p class="text-muted small mb-0">{{ s.text }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- SEE IT IN ACTION ------------------------------------------------------->
  <section class="section">
    <div class="container">
      <div class="row align-items-center g-4 g-lg-5">
        <div class="col-lg-5 order-lg-2">
          <span class="section-eyebrow"><Smartphone :size="14" /> See it in action</span>
          <h2 class="section-title mt-2 mb-3">Clear answers, not confusing forms</h2>
          <p class="section-lead mb-4">Every rule is checked against your profile and explained in plain language — with the official wording right there.</p>
          <div class="d-grid gap-3">
            <div v-for="f in showcase" :key="f.title" class="d-flex gap-3">
              <span class="icon-tile icon-tile-sm" :class="f.tint"><component :is="f.icon" /></span>
              <div><div class="fw-bold">{{ f.title }}</div><div class="small text-muted">{{ f.text }}</div></div>
            </div>
          </div>
          <router-link to="/register" class="btn btn-primary btn-lg btn-pill mt-4">Check your eligibility <ArrowRight :size="18" /></router-link>
        </div>
        <div class="col-lg-7 order-lg-1">
          <div class="position-relative py-3" aria-label="Example of the FormSaathi app on a phone" role="img">
            <div class="hero-blob" style="width:min(380px, 80vw);height:min(380px, 80vw);background:#D9CEFF;top:40px;left:50%;transform:translateX(-50%);opacity:.7" />
            <div class="phone">
              <div class="phone-notch" />
              <div class="phone-screen p-3 pt-5" aria-hidden="true">
                <div class="d-flex align-items-center justify-content-between mb-3"><AppLogo :size="24" /><span class="fs-badge fs-badge-coral"><Bell /> 2</span></div>
                <div class="small text-muted mb-1">Eligibility check</div>
                <div class="fw-bold mb-2" style="font-size:.95rem">PM-USP Central Sector Scholarship</div>
                <div class="verdict verdict-possibly_eligible p-2 mb-2 align-items-center" style="border-radius:1rem">
                  <span class="crit-icon" style="background: var(--fs-surface)"><HelpCircle /></span>
                  <div class="small fw-bold">Possibly eligible — 2 rules to confirm</div>
                </div>
                <div class="fs-card p-2 mb-2" style="border-radius:1rem">
                  <div v-for="r in phoneRules" :key="r.t" class="d-flex align-items-center gap-2 py-1 small">
                    <span class="crit-icon" :class="`crit-${r.o}`" style="width:1.5rem;height:1.5rem"><component :is="r.o === 'met' ? Check : HelpCircle" /></span>
                    <span class="fw-semibold" style="font-size:.78rem">{{ r.t }}</span>
                  </div>
                </div>
                <div class="fs-card p-2 mb-2" style="border-radius:1rem">
                  <div class="d-flex justify-content-between small fw-bold mb-1"><span style="font-size:.78rem">Documents ready</span><span style="font-size:.78rem">2 / 3</span></div>
                  <div class="progress"><div class="progress-bar" style="width: 66%" /></div>
                </div>
                <div class="bubble bubble-user small ms-auto mb-2" style="max-width: 85%; font-size:.76rem">डोमिसाइल सर्टिफिकेट क्या होता है?</div>
                <div class="bubble bubble-ai small mb-2" style="max-width: 92%; font-size:.76rem">यह इस बात का प्रमाण है कि आप किसी राज्य के स्थायी निवासी हैं। इसे तहसील कार्यालय या राज्य के ऑनलाइन पोर्टल से बनवाया जाता है।</div>
                <div class="btn btn-primary btn-sm w-100 btn-pill" style="font-size:.8rem">Track application</div>
              </div>
            </div>
            <div class="phone-chip float d-none d-sm-flex align-items-center gap-2" style="top: 18%; left: 2%">
              <span class="icon-tile icon-tile-sm tint-butter"><CalendarClock /></span><div><div class="fw-bold">3 days left</div><div class="text-muted" style="font-size:.72rem">Deadline reminder</div></div>
            </div>
            <div class="phone-chip float-2 d-none d-sm-flex align-items-center gap-2" style="top: 52%; right: 1%">
              <span class="icon-tile icon-tile-sm tint-lavender"><Bot /></span><div><div class="fw-bold">Saathi AI</div><div class="text-muted" style="font-size:.72rem">Answers in हिन्दी · मराठी</div></div>
            </div>
            <div class="phone-chip float-3 d-none d-sm-flex align-items-center gap-2" style="bottom: 8%; left: 6%">
              <span class="icon-tile icon-tile-sm tint-mint"><FileCheck2 /></span><div><div class="fw-bold">Checklist ready</div><div class="text-muted" style="font-size:.72rem">Know what to bring</div></div>
            </div>
          </div>
          <p class="text-center small text-muted mt-2 mb-0">Example screen. AI answers are guidance, not official advice.</p>
        </div>
      </div>
    </div>
  </section>

  <!-- ATS RESUME BUILDER ------------------------------------------------------->
  <section class="section bg-mist">
    <div class="container">
      <div class="row align-items-center g-4 g-lg-5">
        <div class="col-lg-6">
          <span class="section-eyebrow"><ScrollText :size="14" /> New · ATS resume builder</span>
          <h2 class="section-title mt-2 mb-3">Found the internship? Make your resume ready for it.</h2>
          <p class="section-lead mb-4">Build a clean one-column resume that applicant tracking systems can read, run 15 clear readiness checks, and see which keywords from any internship or job on FormSaathi your resume is missing.</p>
          <div class="d-grid gap-3 mb-4">
            <div v-for="f in resumeFeatures" :key="f.title" class="d-flex gap-3">
              <span class="icon-tile icon-tile-sm" :class="f.tint"><component :is="f.icon" /></span>
              <div><div class="fw-bold">{{ f.title }}</div><div class="small text-muted">{{ f.text }}</div></div>
            </div>
          </div>
          <router-link to="/register" class="btn btn-primary btn-lg btn-pill">Build my resume <ArrowRight :size="18" /></router-link>
        </div>
        <div class="col-lg-6">
          <div class="position-relative mx-auto" style="max-width: 520px" aria-hidden="true">
            <div class="fs-card p-4 shadow-soft" style="border-radius: 1.25rem; font-size: .78rem">
              <div class="text-center mb-2"><div class="fw-bold" style="font-size: 1.15rem; font-variant: small-caps; letter-spacing: .03em">Riya Deshmukh</div><div class="text-muted">Pune, Maharashtra | riya@email.com | GitHub | LinkedIn</div></div>
              <div v-for="sec in mockResume" :key="sec.h" class="mb-2">
                <div class="fw-bold text-uppercase pb-1 mb-1" style="font-size: .72rem; letter-spacing: .06em; border-bottom: 1px solid var(--fs-text)">{{ sec.h }}</div>
                <div v-for="ln in sec.lines" :key="ln" class="d-flex gap-2"><span class="text-muted">•</span><span>{{ ln }}</span></div>
              </div>
            </div>
            <div class="phone-chip float d-flex align-items-center gap-2" style="top: -18px; right: -10px">
              <span class="icon-tile icon-tile-sm tint-mint"><ListChecks /></span><div><div class="fw-bold">14 / 15 checks</div><div class="text-muted" style="font-size: .72rem">ATS readiness</div></div>
            </div>
            <div class="phone-chip float-2 d-flex align-items-center gap-2" style="bottom: -20px; left: -10px">
              <span class="icon-tile icon-tile-sm tint-peach"><Target /></span><div><div class="fw-bold">82% keyword match</div><div class="text-muted" style="font-size: .72rem">RBI Summer Placement</div></div>
            </div>
          </div>
          <p class="text-center small text-muted mt-4 mb-0">Example resume for illustration.</p>
        </div>
      </div>
    </div>
  </section>

  <!-- FEATURED --------------------------------------------------------------->
  <section class="section pt-0">
    <div class="container">
      <div class="d-flex align-items-end justify-content-between flex-wrap gap-3 mb-3">
        <div><span class="section-eyebrow"><Flame :size="14" /> Featured</span><h2 class="section-title mt-2 mb-0">Open right now</h2></div>
        <router-link to="/explore" class="btn btn-soft btn-pill">{{ t('common.viewAll') }} <ArrowRight :size="16" /></router-link>
      </div>
      <div class="d-flex gap-2 align-items-start mb-4 p-3 rounded-4" style="background: var(--fs-success-bg); color: var(--fs-text)"><BadgeCheck :size="18" class="flex-shrink-0 mt-1" style="color: var(--fs-success)" /><span class="small">Every listing comes from an <strong>official source</strong> — ministries, AICTE, UGC, RBI, UPSC and others — and shows when it was last verified. Authorities can extend or change dates, so always confirm on the official site before applying.</span></div>
      <StateBlock v-if="loading" kind="loading" />
      <StateBlock v-else-if="error" kind="error" message="We couldn't load featured opportunities." @retry="load" />
      <div v-else class="row g-3">
        <div v-for="o in featured" :key="o.id" class="col-md-6 col-xl-4"><OpportunityCard :o="o" /></div>
      </div>
    </div>
  </section>

  <!-- MADE FOR --------------------------------------------------------------->
  <section class="section bg-mist">
    <div class="container">
      <div class="text-center mb-5">
        <span class="section-eyebrow"><Users :size="14" /> Made for you</span>
        <h2 class="section-title mt-2 mb-2">Built for every step of life</h2>
        <p class="section-lead mx-auto mb-0">Starting with students — growing to job seekers and every citizen.</p>
      </div>
      <div class="row g-4">
        <div v-for="p in personas" :key="p.title" class="col-md-4">
          <div class="persona-card">
            <SpotArt :name="p.art" />
            <h3 class="h5 fw-bold">{{ p.title }}</h3>
            <p class="text-muted small">{{ p.text }}</p>
            <div class="d-flex flex-wrap gap-1 mb-4">
              <router-link v-for="c in p.cats" :key="c" :to="{ path: '/explore', query: { category: c } }" class="fs-badge text-decoration-none" :class="`tint-${meta.category(c)?.color || 'lavender'}`">{{ meta.category(c)?.name || c }}</router-link>
            </div>
            <router-link :to="{ path: '/explore', query: { category: p.cats.join(',') } }" class="btn btn-soft btn-pill mt-auto align-self-start">{{ p.cta }} <ArrowRight :size="16" /></router-link>
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- WHY -------------------------------------------------------------------->
  <section class="section">
    <div class="container">
      <div class="row g-4 g-lg-5 align-items-center">
        <div class="col-lg-4">
          <span class="section-eyebrow"><Heart :size="14" /> Why FormSaathi</span>
          <h2 class="section-title mt-2 mb-3">Not another listing site. A personal application assistant.</h2>
          <p class="text-muted mb-4">Listing sites stop at “here’s a link”. FormSaathi stays with you until you’ve applied — and is honest about what it knows and what it doesn’t.</p>
          <router-link to="/register" class="btn btn-primary btn-lg btn-pill">{{ t('nav.start') }} <ArrowRight :size="18" /></router-link>
        </div>
        <div class="col-lg-8">
          <div class="row g-3">
            <div v-for="w in why" :key="w.title" class="col-sm-6">
              <div class="feature-tile">
                <span class="icon-tile icon-tile-sm" :class="w.tint"><component :is="w.icon" /></span>
                <div><div class="fw-bold mb-1">{{ w.title }}</div><div class="small text-muted">{{ w.text }}</div></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- FAQ -------------------------------------------------------------------->
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

  <!-- CTA -------------------------------------------------------------------->
  <section class="pb-5">
    <div class="container">
      <div class="cta-band">
        <div class="row align-items-center g-4">
          <div class="col-lg-7">
            <h2 class="section-title mb-2">Your opportunities are waiting.</h2>
            <p class="mb-4" style="color: rgba(255,255,255,.9); font-size: 1.08rem">Create a free profile in 3 minutes. Optional details stay optional — and you can delete everything any time.</p>
            <div class="d-flex flex-wrap gap-2">
              <router-link to="/register" class="btn btn-white btn-lg btn-pill">{{ t('hero.start') }} <ArrowRight :size="18" /></router-link>
              <router-link to="/explore" class="btn btn-glass btn-lg btn-pill">{{ t('hero.explore') }}</router-link>
            </div>
          </div>
          <div class="col-lg-5 d-none d-lg-block">
            <div class="bg-surface rounded-xl p-3 mx-auto float" style="max-width: 300px; transform: rotate(3deg); box-shadow: 0 30px 60px -30px rgba(27,23,64,.6)"><SpotArt name="celebrate" /></div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import {
  ArrowRight, BadgeCheck, Bell, Bot, CalendarClock, Check, CircleCheck, FileCheck2, Flame, Heart, HelpCircle,
  KanbanSquare, Languages, ListChecks, MessageCircleQuestion, Route, Scale, ScrollText, Search, Shapes, ShieldCheck, Smartphone, Sparkles, Target,
  UserRoundCheck, Users,
} from 'lucide-vue-next'
import api from '@/api'
import { useMeta } from '@/stores/meta'
import AppLogo from '@/components/AppLogo.vue'
import CategoryIcon from '@/components/CategoryIcon.vue'
import OpportunityCard from '@/components/OpportunityCard.vue'
import StateBlock from '@/components/StateBlock.vue'
import HeroScene from '@/components/art/HeroScene.vue'
import SpotArt from '@/components/art/SpotArt.vue'

const { t } = useI18n()
const meta = useMeta()
const router = useRouter()
const q = ref('')
const featured = ref([])
const loading = ref(true)
const error = ref(false)
const openFaq = ref(0)
const quickCats = computed(() => meta.categories.slice(0, 4))

function search() { router.push({ path: '/explore', query: q.value.trim() ? { q: q.value.trim() } : {} }) }
async function load() {
  loading.value = true; error.value = false
  try { featured.value = (await api.get('/opportunities/featured')).items } catch { error.value = true } finally { loading.value = false }
}
onMounted(load)

const trust = [
  { icon: BadgeCheck, title: 'Verified official sources', text: 'Every listing links to its source', tint: 'tint-mint' },
  { icon: UserRoundCheck, title: 'Personalised matches', text: 'Based on your own profile', tint: 'tint-lavender' },
  { icon: Languages, title: 'Multilingual help', text: 'English, हिन्दी, मराठी', tint: 'tint-sky' },
  { icon: KanbanSquare, title: 'Application tracking', text: 'From interested to approved', tint: 'tint-peach' },
]
const steps = [
  { art: 'profile', title: 'Create your profile', text: 'Education, location and interests. Sensitive details are optional and explained.' },
  { art: 'discover', title: 'Discover matches', text: 'Opportunities that fit you, with clear reasons why they were recommended.' },
  { art: 'checklist', title: 'Check & prepare', text: 'Rule-by-rule eligibility and a document checklist for each opportunity.' },
  { art: 'track', title: 'Apply & track', text: 'Apply on the official site, then track status, notes and reminders.' },
]
const phoneRules = [
  { t: 'Regular degree course', o: 'met' },
  { t: 'Family income up to ₹4.5 lakh', o: 'met' },
  { t: 'Above 80th percentile in Class XII', o: 'needs_review' },
  { t: 'No other scholarship or fee waiver', o: 'needs_review' },
]
const showcase = [
  { icon: Scale, title: 'Rule-by-rule eligibility', text: 'Met, not met or needs info — never a made-up percentage.', tint: 'tint-lavender' },
  { icon: ListChecks, title: 'Your document checklist', text: 'See what each application needs and what you already have.', tint: 'tint-mint' },
  { icon: Bot, title: 'Saathi AI in your language', text: 'Ask about any form or term in English, Hindi or Marathi.', tint: 'tint-peach' },
  { icon: Bell, title: 'Reminders that matter', text: 'Before deadlines, and when a document is missing.', tint: 'tint-butter' },
]
const personas = [
  { art: 'student', cta: 'Explore for students', title: 'Students', text: 'Scholarships, internships, fellowships and exams that match your course, year and marks.', cats: ['scholarships', 'internships', 'fellowships', 'exams'] },
  { art: 'jobseeker', cta: 'Explore jobs & skills', title: 'Job seekers', text: 'Jobs, apprenticeships and skill programmes — with deadlines and documents organised.', cats: ['jobs', 'skill-programs'] },
  { art: 'family', cta: 'Explore schemes', title: 'Families & citizens', text: 'Government schemes and grants explained simply, with the documents you’ll need.', cats: ['government-schemes', 'grants'] },
]
const why = [
  { icon: Scale, title: 'Transparent eligibility', text: 'Every rule shown as met, not met or needs info — with the official wording.', tint: 'tint-lavender' },
  { icon: ListChecks, title: 'Document checklists', text: 'Know exactly which documents each application needs.', tint: 'tint-mint' },
  { icon: Bot, title: 'Saathi AI', text: 'Explains forms and difficult terms simply, in three languages.', tint: 'tint-sky' },
  { icon: Bell, title: 'Deadline reminders', text: 'In-app and email reminders before deadlines and for missing documents.', tint: 'tint-peach' },
  { icon: ShieldCheck, title: 'Private by design', text: 'Your documents are never public. Optional fields stay optional.', tint: 'tint-butter' },
  { icon: FileCheck2, title: 'Honest data labels', text: 'Verified, demo and AI-generated content are always clearly marked.', tint: 'tint-lilac' },
  { icon: ScrollText, title: 'ATS resume builder', text: 'One-column resumes recruiters’ systems can read, with keyword matching for every opportunity.', tint: 'tint-sky' },
  { icon: KanbanSquare, title: 'Application tracker', text: 'Every application from interested to approved, with notes, dates and reminders.', tint: 'tint-peach' },
]
const resumeFeatures = [
  { icon: ListChecks, title: '15 transparent ATS checks', text: 'Contact details, action verbs, real numbers, length, dates and more — no made-up score.', tint: 'tint-mint' },
  { icon: Target, title: 'Keyword match for any opportunity', text: 'Pick an internship on FormSaathi or paste a job description to see missing keywords.', tint: 'tint-peach' },
  { icon: FileCheck2, title: 'PDF that parsers can read', text: 'Single column, standard headings, real text. Starts from your FormSaathi profile.', tint: 'tint-lavender' },
]
const mockResume = [
  { h: 'Experience', lines: ['Built a Flask dashboard used by 40 classmates to track deadlines', 'Reduced report time by 35% by automating SQL queries'] },
  { h: 'Projects', lines: ['Designed a 7-table schema for a hospital booking app (Vue.js, Flask)'] },
  { h: 'Skills', lines: ['Python, SQL, Flask, Vue.js, Pandas, Git'] },
]
const faqs = [
  { q: 'Is FormSaathi free?', a: 'Yes. Creating a profile, discovering opportunities, checking eligibility and tracking applications are free.' },
  { q: 'Does FormSaathi submit applications for me?', a: 'No. You always apply on the official website. FormSaathi helps you prepare, and you confirm in your tracker when you have applied.' },
  { q: 'How do you make sure information is correct?', a: 'Each opportunity links to its official source and shows when it was last verified. Listings that are not yet verified are labelled, and you can report a correction on any listing.' },
  { q: 'Why do you ask about income or category?', a: 'Many scholarships and schemes depend on them. These fields are optional — if you skip them, eligibility checks simply show “more information needed” for those rules.' },
  { q: 'Is Saathi AI official advice?', a: 'No. Saathi AI explains things in simple language, but it is not a government official. Always confirm on the official source before applying.' },
]
</script>
