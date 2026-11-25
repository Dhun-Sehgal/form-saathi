<template>
  <div class="w-100" style="max-width: 640px">
    <div class="mb-4">
      <div class="d-flex justify-content-between small text-muted mb-2"><span>Step {{ step + 1 }} of {{ steps.length }} · {{ steps[step].title }}</span><span>Profile {{ auth.user?.profile_completion?.percent || 0 }}% complete</span></div>
      <div class="progress" role="progressbar" :aria-valuenow="step + 1" aria-valuemin="1" :aria-valuemax="steps.length"><div class="progress-bar" :style="{ width: ((step + 1) / steps.length) * 100 + '%' }" /></div>
    </div>

    <div class="fs-card p-4 p-md-5 shadow-soft">
      <span class="icon-tile mb-3" :class="steps[step].tint"><component :is="steps[step].icon" /></span>
      <h1 class="h3 fw-bold mb-1">{{ steps[step].heading }}</h1>
      <p class="text-muted mb-4">{{ steps[step].sub }}</p>

      <!-- 1. Basics -->
      <div v-if="step === 0" class="d-grid gap-3">
        <Field id="name" label="Full name" :error="errors.full_name"><input id="name" v-model="p.full_name" class="form-control" autocomplete="name" /></Field>
        <Field id="dob" label="Date of birth" help="Used only to check age limits."><input id="dob" v-model="p.date_of_birth" type="date" class="form-control" :max="today" /></Field>
        <div><span class="form-label d-block">Preferred language</span><div class="d-flex flex-wrap gap-2">
          <label v-for="(n, c) in LABELS.language" :key="c" class="choice-chip" :class="{ active: p.preferred_language === c }"><input v-model="p.preferred_language" type="radio" :value="c" />{{ n }}</label>
        </div></div>
      </div>

      <!-- 2. Location -->
      <div v-else-if="step === 1" class="d-grid gap-3">
        <Field id="state" label="State / Union Territory" help="Many schemes are only for residents of a state."><select id="state" v-model="p.state_code" class="form-select"><option :value="null">Select…</option><option v-for="s in meta.states" :key="s.code" :value="s.code">{{ s.name }}</option></select></Field>
        <Field id="city" label="City / district"><input id="city" v-model="p.city" class="form-control" autocomplete="address-level2" /></Field>
      </div>

      <!-- 3. Education -->
      <div v-else-if="step === 2" class="row g-3">
        <div class="col-12"><Field id="edu" label="Current education level"><select id="edu" v-model="p.education_level" class="form-select"><option :value="null">Select…</option><option v-for="(n, k) in LABELS.education" :key="k" :value="k">{{ n }}</option></select></Field></div>
        <div class="col-12"><Field id="inst" label="College / institution"><input id="inst" v-model="p.institution" class="form-control" /></Field></div>
        <div class="col-md-7"><Field id="course" label="Course" help="e.g. B.Tech, B.Sc, BA, ITI Electrician"><input id="course" v-model="p.course" class="form-control" /></Field></div>
        <div class="col-md-5"><Field id="stream" label="Stream / branch"><input id="stream" v-model="p.stream" class="form-control" placeholder="e.g. Computer Science" /></Field></div>
        <div class="col-md-4"><Field id="year" label="Year of study"><select id="year" v-model.number="p.current_year" class="form-select"><option :value="null">—</option><option v-for="y in 6" :key="y" :value="y">Year {{ y }}</option></select></Field></div>
        <div class="col-md-4"><Field id="mt" label="Marks as"><select id="mt" v-model="p.marks_type" class="form-select"><option :value="null">—</option><option value="percentage">Percentage</option><option value="cgpa">CGPA (out of 10)</option></select></Field></div>
        <div class="col-md-4"><Field id="mv" label="Latest marks" :error="errors.marks_value"><input id="mv" v-model.number="p.marks_value" type="number" step="0.01" min="0" :max="p.marks_type === 'cgpa' ? 10 : 100" class="form-control" :disabled="!p.marks_type" /></Field></div>
      </div>

      <!-- 4. Optional context -->
      <div v-else-if="step === 3" class="d-grid gap-3">
        <div class="alert d-flex gap-2 mb-0" style="background: var(--fs-primary-50); color: var(--fs-text)"><Lock :size="18" class="flex-shrink-0 mt-1" style="color: var(--fs-primary)" /><div class="small"><strong>All optional.</strong> Many scholarships and schemes depend on these. We use them only to check eligibility rules — they’re never shown to anyone or sent to the AI. Skip any you’re not comfortable sharing.</div></div>
        <Field id="inc" label="Annual family income"><select id="inc" v-model="p.income_range" class="form-select"><option :value="null">Skip</option><option v-for="(n, k) in LABELS.income" :key="k" :value="k">{{ n }}</option></select></Field>
        <Field id="cat" label="Social category"><select id="cat" v-model="p.social_category" class="form-select"><option :value="null">Skip</option><option v-for="(n, k) in LABELS.social" :key="k" :value="k">{{ n }}</option></select></Field>
        <Field id="gen" label="Gender" help="Some scholarships are for women or specific groups."><select id="gen" v-model="p.gender" class="form-select"><option :value="null">Skip</option><option v-for="(n, k) in LABELS.gender" :key="k" :value="k">{{ n }}</option></select></Field>
        <div><span class="form-label d-block">Do you have a disability certificate (40% or more)?</span><div class="d-flex flex-wrap gap-2">
          <label v-for="opt in [[true, 'Yes'], [false, 'No'], [null, 'Skip']]" :key="String(opt[0])" class="choice-chip" :class="{ active: p.has_disability === opt[0] }"><input v-model="p.has_disability" type="radio" :value="opt[0]" />{{ opt[1] }}</label>
        </div></div>
      </div>

      <!-- 5. Interests -->
      <div v-else class="d-grid gap-4">
        <div><span class="form-label d-block">What are you looking for?</span><div class="d-flex flex-wrap gap-2">
          <label v-for="c in meta.categories" :key="c.slug" class="choice-chip" :class="{ active: p.interests.includes(c.slug) }"><input v-model="p.interests" type="checkbox" :value="c.slug" />{{ c.name }}</label>
        </div></div>
        <div>
          <label class="form-label" for="skill">Skills <span class="text-muted fw-normal">(press Enter to add)</span></label>
          <div class="d-flex flex-wrap gap-1 mb-2"><span v-for="(s, i) in p.skills" :key="s" class="fs-chip">{{ s }} <button class="btn-close" style="font-size:.5rem;min-height:auto" :aria-label="'Remove ' + s" @click="p.skills.splice(i, 1)" /></span></div>
          <input id="skill" v-model="skill" class="form-control" placeholder="e.g. Python, Excel, Public speaking" @keydown.enter.prevent="addSkill" />
        </div>
        <Field id="career" label="Career interests" help="Comma separated, e.g. software, civil services, research"><input id="career" v-model="career" class="form-control" /></Field>
      </div>

      <div v-if="error" class="alert alert-danger small mt-3 mb-0">{{ error }}</div>
      <div class="d-flex align-items-center gap-2 mt-4 flex-wrap">
        <button v-if="step > 0" class="btn btn-ghost" :disabled="busy" @click="step--"><ArrowLeft :size="16" /> {{ t('common.back') }}</button>
        <button class="btn btn-link text-muted ms-auto" :disabled="busy" @click="next(true)">{{ step === steps.length - 1 ? 'Skip & finish' : t('common.skip') }}</button>
        <button class="btn btn-primary" :disabled="busy" @click="next(false)">{{ step === steps.length - 1 ? t('common.finish') : t('common.continue') }} <ArrowRight :size="16" /></button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { h, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { ArrowLeft, ArrowRight, GraduationCap, Heart, Lock, MapPin, UserRound } from 'lucide-vue-next'
import { setLanguage } from '@/i18n'
import { useAuth } from '@/stores/auth'
import { useMeta } from '@/stores/meta'
import { useUi } from '@/stores/ui'
import { LABELS } from '@/utils/format'

const Field = (props, { slots }) => h('div', [
  h('label', { class: 'form-label', for: props.id }, props.label),
  slots.default(),
  props.error ? h('div', { class: 'invalid-feedback' }, props.error) : props.help ? h('div', { class: 'form-text' }, props.help) : null,
])
Field.props = ['id', 'label', 'help', 'error']

const { t } = useI18n()
const auth = useAuth()
const meta = useMeta()
const ui = useUi()
const router = useRouter()
const route = useRoute()
const today = new Date().toISOString().slice(0, 10)
const steps = [
  { title: 'Basics', heading: `Hi ${auth.firstName}! Let’s personalise FormSaathi`, sub: 'A few details help us find opportunities that fit you.', icon: UserRound, tint: 'tint-lavender' },
  { title: 'Location', heading: 'Where do you live?', sub: 'State-specific schemes need this.', icon: MapPin, tint: 'tint-sky' },
  { title: 'Education', heading: 'Tell us about your studies', sub: 'Most opportunities depend on your course, year and marks.', icon: GraduationCap, tint: 'tint-mint' },
  { title: 'Optional details', heading: 'A little more context (optional)', sub: 'Helps us check income- and category-based eligibility.', icon: Lock, tint: 'tint-butter' },
  { title: 'Interests', heading: 'What are you interested in?', sub: 'We’ll prioritise these in your recommendations.', icon: Heart, tint: 'tint-peach' },
]
const FIELDS = [
  ['full_name', 'date_of_birth', 'preferred_language'], ['state_code', 'city'],
  ['education_level', 'institution', 'course', 'stream', 'current_year', 'marks_type', 'marks_value'],
  ['income_range', 'social_category', 'gender', 'has_disability'], ['interests', 'skills', 'career_interests'],
]
const p = reactive({ ...auth.profile, interests: [...(auth.profile.interests || [])], skills: [...(auth.profile.skills || [])] })
const step = ref(Math.min(auth.profile.onboarding_step || 0, 4))
const skill = ref('')
const career = ref((auth.profile.career_interests || []).join(', '))
const busy = ref(false)
const error = ref('')
const errors = ref({})

onMounted(() => meta.load())
function addSkill() { const s = skill.value.trim(); if (s && !p.skills.includes(s) && p.skills.length < 30) p.skills.push(s); skill.value = '' }

async function next(skip) {
  error.value = ''; errors.value = {}
  busy.value = true
  try {
    const patch = { onboarding_step: Math.min(step.value + 1, 5) }
    if (!skip) {
      p.career_interests = career.value.split(',').map((s) => s.trim()).filter(Boolean).slice(0, 20)
      for (const f of FIELDS[step.value]) patch[f] = p[f] === '' ? null : p[f]
      if (patch.marks_value === '' || Number.isNaN(patch.marks_value)) patch.marks_value = null
    }
    await auth.updateProfile(patch)
    if (step.value === 0 && p.preferred_language) setLanguage(p.preferred_language)
    if (step.value < steps.length - 1) { step.value++; return }
    const r = await (await import('@/api')).default.post('/profile/onboarding/complete')
    auth.setUser(r.user)
    ui.toast('Your profile is ready! Here are your first matches.')
    const n = route.query.next
    router.push(typeof n === 'string' && n.startsWith('/app') ? n : '/app')
  } catch (e) {
    errors.value = e.fields || {}
    error.value = e.fields ? 'Please check the highlighted fields.' : e.message
  } finally { busy.value = false }
}
</script>
