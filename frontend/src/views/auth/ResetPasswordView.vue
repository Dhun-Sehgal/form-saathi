<template>
  <div class="fs-card p-4 p-md-5 w-100 shadow-soft" style="max-width: 460px; border-radius: 1.75rem">
    <SpotArt name="checklist" style="width: 140px; display: block; margin: -0.5rem auto 0.5rem" />
    <h1 class="h3 fw-bold mb-1">Choose a new password</h1>
    <p class="text-muted mb-4">At least 8 characters, with letters and numbers.</p>
    <form class="d-grid gap-3" @submit.prevent="submit">
      <div><label class="form-label" for="pw">New password</label><input id="pw" v-model="password" type="password" class="form-control" autocomplete="new-password" :class="{ 'is-invalid': fieldErr }" /><div v-if="fieldErr" class="invalid-feedback">{{ fieldErr }}</div></div>
      <div><label class="form-label" for="pw2">Confirm password</label><input id="pw2" v-model="confirm" type="password" class="form-control" autocomplete="new-password" /></div>
      <div v-if="error" class="alert alert-danger py-2 small mb-0">{{ error }} <router-link v-if="expired" to="/forgot-password">Request a new link</router-link></div>
      <button class="btn btn-primary btn-lg btn-pill" :disabled="busy || !password">{{ busy ? 'Saving…' : 'Update password' }}</button>
    </form>
  </div>
</template>

<script setup>
import SpotArt from '@/components/art/SpotArt.vue'
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '@/api'
import { useUi } from '@/stores/ui'

const route = useRoute()
const router = useRouter()
const ui = useUi()
const password = ref('')
const confirm = ref('')
const busy = ref(false)
const error = ref('')
const fieldErr = ref('')
const expired = ref(false)
async function submit() {
  error.value = ''; fieldErr.value = ''
  if (password.value !== confirm.value) { error.value = 'The two passwords don’t match.'; return }
  busy.value = true
  try {
    ui.toast((await api.post('/auth/reset-password', { token: route.params.token, password: password.value })).message)
    router.push('/login')
  } catch (e) {
    fieldErr.value = e.fields?.password || ''
    expired.value = e.code === 'invalid_token'
    if (!fieldErr.value) error.value = e.message
  } finally { busy.value = false }
}
</script>
