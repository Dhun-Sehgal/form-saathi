<template>
  <AuthShell heading="Your opportunities, in one place." sub="Create a free profile in about 3 minutes. Optional details stay optional." art="student" :points="['Free forever for students', 'Explained in English, हिन्दी and मराठी', 'Export or delete your data any time']">
    <h1 class="h3 fw-bold mb-1">Create your free account ✨</h1>
    <p class="text-muted mb-4">Takes about 3 minutes, including your profile.</p>
    <form class="d-grid gap-3" novalidate @submit.prevent="submit">
      <div>
        <label class="form-label" for="name">Full name</label>
        <input id="name" v-model="form.full_name" class="form-control" :class="{ 'is-invalid': errors.full_name }" autocomplete="name" />
        <div v-if="errors.full_name" class="invalid-feedback">{{ errors.full_name }}</div>
      </div>
      <div>
        <label class="form-label" for="email">Email</label>
        <input id="email" v-model.trim="form.email" type="email" class="form-control" :class="{ 'is-invalid': errors.email }" autocomplete="email" />
        <div v-if="errors.email" class="invalid-feedback">{{ errors.email }}</div>
      </div>
      <div>
        <label class="form-label" for="pw">Password</label>
        <input id="pw" v-model="form.password" type="password" class="form-control" :class="{ 'is-invalid': errors.password }" autocomplete="new-password" aria-describedby="pwhelp" />
        <div v-if="errors.password" class="invalid-feedback">{{ errors.password }}</div>
        <div id="pwhelp" class="form-text">At least 8 characters, with letters and numbers.</div>
        <div class="d-flex gap-1 mt-2" aria-hidden="true"><div v-for="i in 3" :key="i" class="flex-fill rounded" style="height:4px" :style="{ background: strength >= i ? ['var(--accent-peach)', 'var(--accent-butter)', 'var(--accent-mint)'][strength - 1] : 'var(--fs-surface-2)' }" /></div>
      </div>
      <div class="form-check">
        <input id="terms" v-model="form.accept_terms" type="checkbox" class="form-check-input" :class="{ 'is-invalid': errors.accept_terms }" />
        <label class="form-check-label small" for="terms">I agree to the <router-link to="/terms" target="_blank">Terms</router-link> and <router-link to="/privacy" target="_blank">Privacy Policy</router-link>.</label>
        <div v-if="errors.accept_terms" class="invalid-feedback">{{ errors.accept_terms }}</div>
      </div>
      <div v-if="error" class="alert alert-danger py-2 small mb-0">{{ error }}</div>
      <button class="btn btn-primary btn-lg btn-pill" :disabled="busy">{{ busy ? 'Creating account…' : 'Create account' }}</button>
    </form>
    <p class="text-center text-muted small mt-4 mb-0">Already have an account? <router-link :to="{ name: 'login', query: route.query }" class="fw-bold">Log in</router-link></p>
  </AuthShell>
</template>

<script setup>
import { computed, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuth } from '@/stores/auth'
import { useUi } from '@/stores/ui'
import AuthShell from '@/components/AuthShell.vue'

const route = useRoute()
const router = useRouter()
const auth = useAuth()
const ui = useUi()
const form = reactive({ full_name: '', email: '', password: '', accept_terms: false })
const errors = ref({})
const error = ref('')
const busy = ref(false)
const strength = computed(() => {
  const p = form.password
  if (!p) return 0
  let s = 0
  if (p.length >= 8) s++
  if (/[A-Za-z]/.test(p) && /\d/.test(p)) s++
  if (p.length >= 12 || /[^A-Za-z0-9]/.test(p)) s++
  return s
})

function validate() {
  const e = {}
  if (form.full_name.trim().length < 2) e.full_name = 'Please enter your name.'
  if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(form.email)) e.email = 'Enter a valid email address.'
  if (form.password.length < 8 || !/[A-Za-z]/.test(form.password) || !/\d/.test(form.password)) e.password = 'Use at least 8 characters with letters and numbers.'
  if (!form.accept_terms) e.accept_terms = 'Please accept to continue.'
  errors.value = e
  return !Object.keys(e).length
}
async function submit() {
  error.value = ''
  if (!validate()) return
  busy.value = true
  try {
    await auth.register(form)
    ui.toast('Account created! Let’s set up your profile.')
    router.push({ name: 'onboarding', query: route.query.next ? { next: route.query.next } : {} })
  } catch (e) {
    errors.value = e.fields || {}
    if (!e.fields) error.value = e.message
  } finally { busy.value = false }
}
</script>
