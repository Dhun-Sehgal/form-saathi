<template>
  <AuthShell heading="Welcome back!" sub="Pick up right where you left off — your matches, checklists and deadlines are waiting.">
    <h1 class="h3 fw-bold mb-1">Log in to FormSaathi 👋</h1>
    <p class="text-muted mb-4">Log in to continue your applications.</p>
    <div v-if="IS_PREVIEW" class="demo-ribbon small mb-3">
      <strong>Preview:</strong> create an account, or try the admin panel with
      <code>{{ PREVIEW_ADMIN.email }}</code> / <code>{{ PREVIEW_ADMIN.password }}</code>.
      <button class="btn btn-link btn-sm p-0 align-baseline" style="min-height:auto" @click="fillAdmin">Fill it in</button>
    </div>
    <form class="d-grid gap-3" novalidate @submit.prevent="submit">
      <div>
        <label class="form-label" for="email">Email</label>
        <input id="email" v-model.trim="email" type="email" class="form-control" autocomplete="email" required />
      </div>
      <div>
        <div class="d-flex justify-content-between"><label class="form-label" for="pw">Password</label><router-link to="/forgot-password" class="small">Forgot password?</router-link></div>
        <div class="input-group">
          <input id="pw" v-model="password" :type="show ? 'text' : 'password'" class="form-control" autocomplete="current-password" required />
          <button type="button" class="btn btn-outline-secondary" :aria-label="show ? 'Hide password' : 'Show password'" @click="show = !show"><EyeOff v-if="show" :size="18" /><Eye v-else :size="18" /></button>
        </div>
      </div>
      <div v-if="error" class="alert alert-danger py-2 small mb-0" role="alert">{{ error }}</div>
      <button class="btn btn-primary btn-lg btn-pill" :disabled="busy || !email || !password">{{ busy ? 'Logging in…' : 'Log in' }}</button>
    </form>
    <p class="text-center text-muted small mt-4 mb-0">New to FormSaathi? <router-link :to="{ name: 'register', query: route.query }" class="fw-bold">Create a free account</router-link></p>
  </AuthShell>
</template>

<script setup>
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Eye, EyeOff } from 'lucide-vue-next'
import { IS_PREVIEW } from '@/api'
import { setLanguage } from '@/i18n'
import { useAuth } from '@/stores/auth'
import { useUi } from '@/stores/ui'
import AuthShell from '@/components/AuthShell.vue'

const PREVIEW_ADMIN = { email: 'admin@formsaathi.demo', password: 'admin1234' }
const route = useRoute()
const router = useRouter()
const auth = useAuth()
const ui = useUi()
const email = ref('')
const password = ref('')
const show = ref(false)
const busy = ref(false)
const error = ref('')

function fillAdmin() { email.value = PREVIEW_ADMIN.email; password.value = PREVIEW_ADMIN.password }
async function submit() {
  error.value = ''; busy.value = true
  try {
    const user = await auth.login(email.value, password.value)
    if (user.profile?.preferred_language) setLanguage(user.profile.preferred_language)
    ui.toast(`Welcome back, ${auth.firstName}!`)
    const next = typeof route.query.next === 'string' && route.query.next.startsWith('/') ? route.query.next : null
    router.push(next || (user.role === 'admin' ? '/admin' : '/app'))
  } catch (e) { error.value = e.message } finally { busy.value = false }
}
</script>
