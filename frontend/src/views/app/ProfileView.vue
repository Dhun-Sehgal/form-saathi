<template>
  <div style="max-width: 980px">
    <div class="d-flex flex-wrap align-items-center gap-3 mb-4">
      <ProgressRing :value="auth.user.profile_completion.percent" :size="72" :stroke="8" />
      <div class="me-auto"><h1 class="page-title">Your profile</h1><p class="page-sub">Used to match opportunities and check eligibility. Optional fields stay optional.</p></div>
      <button class="btn btn-primary" :disabled="busy" @click="save">{{ busy ? 'Saving…' : 'Save changes' }}</button>
    </div>
    <div v-if="auth.user.profile_completion.missing.length" class="alert alert-light border small mb-4">Missing for better matches: {{ auth.user.profile_completion.missing.join(', ') }}</div>

    <div class="row g-4">
      <div class="col-lg-6 d-grid gap-4 align-content-start">
        <section class="fs-card fs-card-pad">
          <h2 class="h6 fw-bold mb-3">Personal</h2>
          <div class="row g-3">
            <div class="col-12"><label class="form-label" for="n">Full name</label><input id="n" v-model="p.full_name" class="form-control" :class="{ 'is-invalid': errors.full_name }" /><div v-if="errors.full_name" class="invalid-feedback">{{ errors.full_name }}</div></div>
            <div class="col-md-6"><label class="form-label" for="dob">Date of birth</label><input id="dob" v-model="p.date_of_birth" type="date" class="form-control" /></div>
            <div class="col-md-6"><label class="form-label" for="lang">Preferred language</label><select id="lang" v-model="p.preferred_language" class="form-select"><option v-for="(n, k) in LABELS.language" :key="k" :value="k">{{ n }}</option></select></div>
            <div class="col-md-6"><label class="form-label" for="st">State</label><select id="st" v-model="p.state_code" class="form-select"><option :value="null">—</option><option v-for="s in meta.states" :key="s.code" :value="s.code">{{ s.name }}</option></select></div>
            <div class="col-md-6"><label class="form-label" for="city">City</label><input id="city" v-model="p.city" class="form-control" /></div>
          </div>
        </section>
        <section class="fs-card fs-card-pad">
          <h2 class="h6 fw-bold mb-1">Optional details</h2>
          <p class="small text-muted">Only used to check eligibility rules. Never shared with other users or sent to the AI.</p>
          <div class="row g-3">
            <div class="col-md-6"><label class="form-label" for="inc">Family income</label><select id="inc" v-model="p.income_range" class="form-select"><option :value="null">Not provided</option><option v-for="(n, k) in LABELS.income" :key="k" :value="k">{{ n }}</option></select></div>
            <div class="col-md-6"><label class="form-label" for="cat">Social category</label><select id="cat" v-model="p.social_category" class="form-select"><option :value="null">Not provided</option><option v-for="(n, k) in LABELS.social" :key="k" :value="k">{{ n }}</option></select></div>
            <div class="col-md-6"><label class="form-label" for="g">Gender</label><select id="g" v-model="p.gender" class="form-select"><option :value="null">Not provided</option><option v-for="(n, k) in LABELS.gender" :key="k" :value="k">{{ n }}</option></select></div>
            <div class="col-md-6"><label class="form-label" for="dis">Disability (40%+)</label><select id="dis" v-model="p.has_disability" class="form-select"><option :value="null">Not provided</option><option :value="true">Yes</option><option :value="false">No</option></select></div>
          </div>
        </section>
      </div>
      <div class="col-lg-6 d-grid gap-4 align-content-start">
        <section class="fs-card fs-card-pad">
          <h2 class="h6 fw-bold mb-3">Education</h2>
          <div class="row g-3">
            <div class="col-12"><label class="form-label" for="edu">Education level</label><select id="edu" v-model="p.education_level" class="form-select"><option :value="null">—</option><option v-for="(n, k) in LABELS.education" :key="k" :value="k">{{ n }}</option></select></div>
            <div class="col-12"><label class="form-label" for="inst">Institution</label><input id="inst" v-model="p.institution" class="form-control" /></div>
            <div class="col-md-6"><label class="form-label" for="c">Course</label><input id="c" v-model="p.course" class="form-control" /></div>
            <div class="col-md-6"><label class="form-label" for="s">Stream</label><input id="s" v-model="p.stream" class="form-control" /></div>
            <div class="col-4"><label class="form-label" for="y">Year</label><select id="y" v-model.number="p.current_year" class="form-select"><option :value="null">—</option><option v-for="y in 6" :key="y" :value="y">{{ y }}</option></select></div>
            <div class="col-4"><label class="form-label" for="mt">Marks as</label><select id="mt" v-model="p.marks_type" class="form-select"><option :value="null">—</option><option value="percentage">%</option><option value="cgpa">CGPA</option></select></div>
            <div class="col-4"><label class="form-label" for="mv">Marks</label><input id="mv" v-model.number="p.marks_value" type="number" step="0.01" class="form-control" :class="{ 'is-invalid': errors.marks_value }" :disabled="!p.marks_type" /><div v-if="errors.marks_value" class="invalid-feedback">{{ errors.marks_value }}</div></div>
          </div>
        </section>
        <section class="fs-card fs-card-pad">
          <h2 class="h6 fw-bold mb-3">Interests & skills</h2>
          <div class="d-flex flex-wrap gap-2 mb-3"><label v-for="c in meta.categories" :key="c.slug" class="choice-chip" :class="{ active: p.interests.includes(c.slug) }"><input v-model="p.interests" type="checkbox" :value="c.slug" />{{ c.name }}</label></div>
          <label class="form-label" for="sk">Skills <span class="text-muted fw-normal">(comma separated)</span></label>
          <input id="sk" v-model="skills" class="form-control mb-3" />
          <label class="form-label" for="ci">Career interests <span class="text-muted fw-normal">(comma separated)</span></label>
          <input id="ci" v-model="careers" class="form-control" />
        </section>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { setLanguage } from '@/i18n'
import { useAuth } from '@/stores/auth'
import { useMeta } from '@/stores/meta'
import { useUi } from '@/stores/ui'
import { LABELS } from '@/utils/format'
import ProgressRing from '@/components/ProgressRing.vue'

const auth = useAuth()
const meta = useMeta()
const ui = useUi()
const p = reactive({ ...auth.profile, interests: [...(auth.profile.interests || [])] })
const skills = ref((auth.profile.skills || []).join(', '))
const careers = ref((auth.profile.career_interests || []).join(', '))
const busy = ref(false)
const errors = ref({})
onMounted(() => meta.load())

const split = (s) => s.split(',').map((x) => x.trim()).filter(Boolean)
async function save() {
  busy.value = true; errors.value = {}
  try {
    const { onboarding_step, onboarding_completed_at, ...rest } = p // eslint-disable-line no-unused-vars
    const payload = { ...rest, skills: split(skills.value).slice(0, 30), career_interests: split(careers.value).slice(0, 20) }
    for (const k of Object.keys(payload)) if (payload[k] === '') payload[k] = null
    if (!payload.marks_type) payload.marks_value = null
    await auth.updateProfile(payload)
    setLanguage(p.preferred_language)
    ui.toast('Profile saved. Your matches have been updated.')
  } catch (e) { errors.value = e.fields || {}; ui.error(e) } finally { busy.value = false }
}
</script>
