<template>
  <section class="section">
    <div class="container" style="max-width: 640px">
      <div class="section-eyebrow mb-2">Contact</div>
      <h1 class="section-title mb-2">We’d love to hear from you</h1>
      <p class="text-muted mb-4">Questions, ideas, or a listing that needs fixing — send us a message.</p>
      <form class="fs-card fs-card-pad d-grid gap-3" novalidate @submit.prevent="submit">
        <div>
          <label class="form-label" for="kind">Topic</label>
          <select id="kind" v-model="form.kind" class="form-select">
            <option value="contact">General question</option><option value="idea">Idea / suggestion</option><option value="bug">Something isn’t working</option><option value="praise">Say thanks</option>
          </select>
        </div>
        <div v-if="!auth.isLoggedIn">
          <label class="form-label" for="email">Your email <span class="text-muted fw-normal">(so we can reply)</span></label>
          <input id="email" v-model="form.contact_email" type="email" class="form-control" :class="{ 'is-invalid': errors.contact_email }" autocomplete="email" />
          <div v-if="errors.contact_email" class="invalid-feedback">{{ errors.contact_email }}</div>
        </div>
        <div>
          <label class="form-label" for="msg">Message</label>
          <textarea id="msg" v-model="form.message" rows="5" class="form-control" :class="{ 'is-invalid': errors.message }" maxlength="3000" />
          <div v-if="errors.message" class="invalid-feedback">{{ errors.message }}</div>
        </div>
        <button class="btn btn-primary" :disabled="busy">{{ busy ? 'Sending…' : 'Send message' }}</button>
      </form>
    </div>
  </section>
</template>

<script setup>
import { reactive, ref } from 'vue'
import api from '@/api'
import { useAuth } from '@/stores/auth'
import { useUi } from '@/stores/ui'

const auth = useAuth()
const ui = useUi()
const form = reactive({ kind: 'contact', contact_email: '', message: '', page: '/contact' })
const errors = ref({})
const busy = ref(false)
async function submit() {
  errors.value = {}
  if (form.message.trim().length < 5) { errors.value.message = 'Please write at least a few words.'; return }
  busy.value = true
  try {
    const payload = { ...form }
    if (!payload.contact_email) delete payload.contact_email
    const r = await api.post('/feedback', payload)
    ui.toast(r.message)
    form.message = ''
  } catch (e) { errors.value = e.fields || {}; ui.error(e) } finally { busy.value = false }
}
</script>
