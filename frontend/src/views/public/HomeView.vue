<template>
  <!-- HERO -->
  <section class="hero">
    <div class="hero-blob" style="width:520px;height:520px;background:#C7D2FE;top:-180px;right:-120px" />
    <div class="hero-blob" style="width:360px;height:360px;background:#FBCFE8;bottom:-160px;left:-120px;opacity:.35" />
    <div class="container">
      <div class="row align-items-center g-4 g-lg-5">
        <div class="col-lg-6">
          <span class="fs-badge fs-badge-ai mb-3"><Sparkles /> Discover → Check → Prepare → Apply → Track</span>
          <h1 class="hero-title text-balance mb-3">{{ t('hero.title1') }} <span class="hero-highlight">{{ t('hero.title2') }}</span></h1>
          <p class="lead text-muted mb-4" style="max-width: 540px">{{ t('hero.sub') }}</p>
          <form class="smart-search mb-3" role="search" @submit.prevent="search">
            <Search :size="20" class="text-muted flex-shrink-0" />
            <input v-model="q" type="search" :placeholder="t('hero.search')" aria-label="Search opportunities" />
            <button class="btn btn-primary" type="submit">{{ t('common.search') }}</button>
          </form>
          <div class="d-flex flex-wrap gap-2 mb-4">
            <router-link v-for="c in quickCats" :key="c.slug" :to="{ path: '/explore', query: { category: c.slug } }" class="fs-chip text-decoration-none">{{ c.name }}</router-link>
          </div>
          <div class="d-flex flex-wrap gap-2">
            <router-link to="/register" class="btn btn-primary btn-lg">{{ t('hero.start') }} <ArrowRight :size="18" /></router-link>
            <router-link to="/explore" class="btn btn-soft btn-lg">{{ t('hero.explore') }}</router-link>
          </div>
        </div>
        <div class="col-lg-6">
          <!-- Dashboard preview illustration (pure HTML/CSS, illustrative) -->
          <div class="position-relative mx-auto" style="max-width: 540px" aria-hidden="true">
            <div class="fs-card shadow-soft p-3 p-md-4 rounded-xl">
              <div class="d-flex align-items-center gap-2 mb-3">
                <span class="rounded-circle d-grid fw-bold" style="width:36px;height:36px;place-items:center;background:var(--fs-lavender);color:var(--fs-primary);font-size:.8rem">AP</span>
                <div><div class="fw-bold small">Namaste, Asha 👋</div><div class="text-muted" style="font-size:.75rem">3 things need your attention</div></div>
                <span class="ms-auto fs-badge fs-badge-coral"><Bell /> 2 deadlines</span>
              </div>
              <div class="row g-2 mb-3">
                <div v-for="s in previewStats" :key="s.label" class="col-4"><div class="rounded-3 p-2 text-center" :class="s.tint"><div class="fw-bold font-display">{{ s.value }}</div><div style="font-size:.7rem">{{ s.label }}</div></div></div>
              </div>
              <div class="rounded-3 border border-soft p-3 mb-2">
                <div class="d-flex align-items-center gap-2 mb-2"><span class="icon-tile icon-tile-sm tint-lavender"><GraduationCap /></span><div class="small fw-semibold">Merit-cum-Means Scholarship</div><span class="ms-auto fs-badge fs-badge-verified"><CircleCheck /> Eligible</span></div>
                <div class="d-flex gap-2 small text-muted"><span>✓ Income</span><span>✓ Marks</span><span>✓ Course</span></div>
              </div>
              <div class="rounded-3 border border-soft p-3">
                <div class="d-flex justify-content-between small mb-1"><span class="fw-semibold">Documents ready</span><span class="text-muted">4 / 6</span></div>
                <div class="progress"><div class="progress-bar" style="width:66%" /></div>
              </div>
            </div>
            <div class="fs-card shadow-soft p-3 position-absolute d-none d-sm-block" style="bottom:-28px;left:-28px;width:220px">
              <div class="d-flex gap-2 align-items-center"><span class="icon-tile icon-tile-sm tint-mint"><Bot /></span><div class="small"><div class="fw-semibold">Saathi AI</div><div class="text-muted" style="font-size:.72rem">“Domicile certificate kya hota hai?”</div></div></div>
            </div>
          </div>
          <p class="text-center text-muted small mt-5 mb-0">Illustration of the FormSaathi dashboard.</p>
        </div>
      </div>
    </div>
  </section>

  <!-- TRUST -->
  <section class="border-top border-bottom border-soft bg-surface">
    <div class="container py-4">
      <div class="row g-3">
        <div v-for="f in trust" :key="f.title" class="col-6 col-lg-3 d-flex gap-3 align-items-center">
          <span class="icon-tile icon-tile-sm" :class="f.tint"><component :is="f.icon" /></span>
          <div><div class="fw-semibold small">{{ f.title }}</div><div class="text-muted" style="font-size:.78rem">{{ f.text }}</div></div>
        </div>
      </div>
    </div>
  </section>

  <!-- HOW IT WORKS -->
  <section class="section" id="how">
    <div class="container">
      <div class="text-center mb-5"><div class="section-eyebrow mb-2">How it works</div><h2 class="section-title">From “Am I eligible?” to “Applied!” in four steps</h2></div>
      <div class="row g-4">
        <div v-for="(s, i) in steps" :key="s.title" class="col-sm-6 col-lg-3">
          <div class="fs-card fs-card-pad h-100">
            <div class="step-num mb-3">{{ i + 1 }}</div>
            <h3 class="h6 fw-bold">{{ s.title }}</h3>
            <p class="text-muted small mb-0">{{ s.text }}</p>
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- CATEGORIES -->
  <section class="section pt-0">
    <div class="container">
      <div class="d-flex align-items-end justify-content-between flex-wrap gap-2 mb-4">
        <div><div class="section-eyebrow mb-2">Categories</div><h2 class="section-title mb-0">Everything you might be missing</h2></div>
        <router-link to="/explore" class="btn btn-soft">Browse all <ArrowRight :size="16" /></router-link>
      </div>
      <div class="row g-3">
        <div v-for="c in meta.categories" :key="c.slug" class="col-6 col-md-4 col-lg-3">
          <router-link :to="{ path: '/explore', query: { category: c.slug } }" class="fs-card fs-card-hover fs-card-pad d-block text-decoration-none h-100">
            <CategoryIcon :name="c.icon" :color="c.color" class="mb-3" />
            <div class="fw-bold" style="color: var(--fs-text)">{{ c.name }}</div>
            <div class="small text-muted d-none d-sm-block">{{ c.description }}</div>
          </router-link>
        </div>
      </div>
    </div>
  </section>

  <!-- FEATURED -->
  <section class="section pt-0">
    <div class="container">
      <div class="d-flex align-items-end justify-content-between flex-wrap gap-2 mb-3">
        <div><div class="section-eyebrow mb-2">Featured</div><h2 class="section-title mb-0">Open right now</h2></div>
        <router-link to="/explore" class="btn btn-soft">{{ t('common.viewAll') }} <ArrowRight :size="16" /></router-link>
      </div>
      <div class="demo-ribbon d-flex gap-2 align-items-start mb-4"><FlaskConical :size="18" class="flex-shrink-0 mt-1" /><span>These listings are <strong>demo data</strong> used to show how FormSaathi works. Real opportunities appear with a <strong>Verified</strong> badge only after our team checks them against the official source.</span></div>
      <StateBlock v-if="loading" kind="loading" />
      <StateBlock v-else-if="error" kind="error" message="We couldn't load featured opportunities." @retry="load" />
      <div v-else class="row g-3">
        <div v-for="o in featured" :key="o.id" class="col-md-6 col-xl-4"><OpportunityCard :o="o" /></div>
      </div>
    </div>
  </section>

  <!-- WHY -->
  <section class="section bg-surface border-top border-bottom border-soft">
    <div class="container">
      <div class="row g-4 g-lg-5 align-items-center">
        <div class="col-lg-5">
          <div class="section-eyebrow mb-2">Why FormSaathi</div>
          <h2 class="section-title mb-3">Not another listing site. A personal application assistant.</h2>
          <p class="text-muted mb-4">Listing sites stop at “here’s a link”. FormSaathi stays with you until you’ve applied — and is honest about what it knows and what it doesn’t.</p>
          <router-link to="/register" class="btn btn-primary btn-lg">{{ t('nav.start') }}</router-link>
        </div>
        <div class="col-lg-7">
          <div class="row g-3">
            <div v-for="w in why" :key="w.title" class="col-sm-6">
              <div class="d-flex gap-3"><span class="icon-tile icon-tile-sm" :class="w.tint"><component :is="w.icon" /></span>
                <div><div class="fw-bold mb-1">{{ w.title }}</div><div class="small text-muted">{{ w.text }}</div></div></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- FAQ -->
  <section class="section">
    <div class="container" style="max-width: 820px">
      <div class="text-center mb-4"><div class="section-eyebrow mb-2">FAQ</div><h2 class="section-title">Questions, answered</h2></div>
      <div class="accordion" id="faq">
        <div v-for="(f, i) in faqs" :key="i" class="accordion-item border-soft">
          <h3 class="accordion-header">
            <button class="accordion-button fw-semibold" :class="{ collapsed: openFaq !== i }" :aria-expanded="openFaq === i" @click="openFaq = openFaq === i ? -1 : i">{{ f.q }}</button>
          </h3>
          <div v-show="openFaq === i" class="accordion-collapse"><div class="accordion-body text-muted">{{ f.a }}</div></div>
        </div>
      </div>
    </div>
  </section>

  <!-- CTA -->
  <section class="pb-5">
    <div class="container">
      <div class="rounded-xl p-4 p-md-5 text-center text-white position-relative overflow-hidden" style="background:#3730A3">
        <div class="hero-blob" style="width:300px;height:300px;background:#FB7185;top:-150px;right:-60px;opacity:.35;z-index:0" />
        <h2 class="section-title text-white position-relative">Your opportunities are waiting.</h2>
        <p class="position-relative mb-4" style="color:#C7D2FE">Create a free profile in 3 minutes. Optional details stay optional.</p>
        <router-link to="/register" class="btn btn-coral btn-lg position-relative">{{ t('hero.start') }}</router-link>
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { ArrowRight, BadgeCheck, Bell, Bot, CircleCheck, FileCheck2, FlaskConical, GraduationCap, KanbanSquare, Languages, ListChecks, Scale, Search, ShieldCheck, Sparkles, UserRoundCheck } from 'lucide-vue-next'
import api from '@/api'
import { useMeta } from '@/stores/meta'
import CategoryIcon from '@/components/CategoryIcon.vue'
import OpportunityCard from '@/components/OpportunityCard.vue'
import StateBlock from '@/components/StateBlock.vue'

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

const previewStats = [
  { value: '6', label: 'Matches', tint: 'tint-lavender' },
  { value: '3', label: 'Tracking', tint: 'tint-sky' },
  { value: '1', label: 'Applied', tint: 'tint-mint' },
]
const trust = [
  { icon: BadgeCheck, title: 'Verified official sources', text: 'Every listing links to its source', tint: 'tint-mint' },
  { icon: UserRoundCheck, title: 'Personalised matches', text: 'Based on your own profile', tint: 'tint-lavender' },
  { icon: Languages, title: 'Multilingual help', text: 'English, हिन्दी, मराठी', tint: 'tint-sky' },
  { icon: KanbanSquare, title: 'Application tracking', text: 'From interested to approved', tint: 'tint-peach' },
]
const steps = [
  { title: 'Create your profile', text: 'Tell us your education, location and interests. Sensitive details are optional and explained.' },
  { title: 'Discover matches', text: 'See opportunities that fit you, with clear reasons why they were recommended.' },
  { title: 'Check eligibility & prepare', text: 'Rule-by-rule eligibility checks and a document checklist built for each opportunity.' },
  { title: 'Apply & track', text: 'Apply on the official site, then track status, notes and reminders in one place.' },
]
const why = [
  { icon: Scale, title: 'Transparent eligibility', text: 'Every rule shown as met, not met or needs info — no made-up match percentages.', tint: 'tint-lavender' },
  { icon: ListChecks, title: 'Document checklists', text: 'Know exactly which documents each application needs and which you already have.', tint: 'tint-mint' },
  { icon: Bot, title: 'Saathi AI', text: 'Explains forms and difficult terms in simple English, Hindi or Marathi.', tint: 'tint-sky' },
  { icon: Bell, title: 'Deadline reminders', text: 'Reminders before deadlines and for missing documents — in-app and by email.', tint: 'tint-peach' },
  { icon: ShieldCheck, title: 'Private by design', text: 'Your documents are never public. Optional fields stay optional.', tint: 'tint-butter' },
  { icon: FileCheck2, title: 'Honest data labels', text: 'Verified, demo and AI-generated content are always clearly marked.', tint: 'tint-lilac' },
]
const faqs = [
  { q: 'Is FormSaathi free?', a: 'Yes. Creating a profile, discovering opportunities, checking eligibility and tracking applications are free.' },
  { q: 'Does FormSaathi submit applications for me?', a: 'No. You always apply on the official website. FormSaathi helps you prepare, and you confirm in your tracker when you have applied.' },
  { q: 'How do you make sure information is correct?', a: 'Each opportunity links to its official source and shows when it was last verified. Listings that are not yet verified are labelled, and you can report a correction on any listing.' },
  { q: 'Why do you ask about income or category?', a: 'Many scholarships and schemes depend on them. These fields are optional — if you skip them, eligibility checks simply show “more information needed” for those rules.' },
  { q: 'Is Saathi AI official advice?', a: 'No. Saathi AI explains things in simple language, but it is not a government official. Always confirm on the official source before applying.' },
]
</script>
