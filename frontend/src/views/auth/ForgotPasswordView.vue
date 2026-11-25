<template>
  <div class="fs-card p-4 p-md-5 w-100 shadow-soft" style="max-width: 440px">
    <h1 class="h3 fw-bold mb-1">Reset your password</h1>
    <p class="text-muted mb-4">Enter your email and we’ll send you a reset link.</p>
    <div v-if="done" class="d-grid gap-3">
      <div class="alert alert-success mb-0">{{ done.message }}</div>
      <div v-if="!done.email_configured && !done.link" class="alert alert-warning small mb-0">Email sending isn’t configured on this server yet, so the reset email can’t be delivered. Please contact the site administrator.</div>
      <router-link v-if="done.link" :to="done.link" class="btn btn-primary">Preview: open your reset link</router-link>
      <router-link to="/login" class="btn btn-soft">Back to log in</router-link>
    </div>
    <form v-else class="d-grid gap-3" @submit.prevent="submit">
      <div><label class="form-label" for="email">Email</label><input id="email" v-model.trim="email" type="email" class="form-control" required autocomplete="email" /></div>
      <div v-if="error" class="alert alert-danger py-2 small mb-0">{{ error }}</div>
      <button class="btn btn-primary btn-lg" :disabled="busy || !email">{{ busy ? 'Sending…' : 'Send reset link' }}</button>
      <router-link to="/login" class="text-center small">Back to log in</router-link>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import api from '@/api'

const email = ref('')
const busy = ref(false)
const error = ref('')
const done = ref(null)
async function submit() {
  busy.value = true; error.value = ''
  try {
    const r = await api.post('/auth/forgot-password', { email: email.value })
    let link = null
    if (r.preview_reset_token) link = `/reset-password/${r.preview_reset_token}`
    else if (r.dev_reset_link) link = '/reset-password/' + r.dev_reset_link.split('/').pop()
    done.value = { ...r, link }
  } catch (e) { error.value = e.message } finally { busy.value = false }
}
</script>
