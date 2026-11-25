<template>
  <div style="max-width: 820px" class="d-grid gap-4">
    <div><h1 class="page-title">Settings</h1><p class="page-sub">Appearance, notifications, security and privacy.</p></div>

    <section class="fs-card fs-card-pad">
      <h2 class="h6 fw-bold mb-3">Appearance & language</h2>
      <div class="d-flex flex-wrap gap-2 mb-3">
        <button class="choice-chip" :class="{ active: ui.theme === 'light' }" @click="ui.theme !== 'light' && ui.toggleTheme()"><Sun :size="16" /> Light</button>
        <button class="choice-chip" :class="{ active: ui.theme === 'dark' }" @click="ui.theme !== 'dark' && ui.toggleTheme()"><Moon :size="16" /> Dark</button>
      </div>
      <div class="d-flex flex-wrap gap-2">
        <button v-for="(n, k) in LABELS.language" :key="k" class="choice-chip" :class="{ active: locale === k }" @click="lang(k)">{{ n }}</button>
      </div>
    </section>

    <section id="notifications" class="fs-card fs-card-pad">
      <h2 class="h6 fw-bold mb-1">Notifications</h2>
      <p v-if="prefs && !emailConfigured" class="small text-muted">Email isn’t configured on this server yet, so you’ll receive notifications in the app only.</p>
      <div v-if="prefs" class="d-grid gap-2">
        <div v-for="row in PREF_ROWS" :key="row.key" class="form-check form-switch d-flex justify-content-between align-items-center ps-0 py-1">
          <label class="form-check-label" :for="row.key"><div class="fw-semibold small">{{ row.label }}</div><div class="small text-muted">{{ row.help }}</div></label>
          <input :id="row.key" v-model="prefs[row.key]" class="form-check-input ms-3 flex-shrink-0" type="checkbox" role="switch" style="width:2.6em;height:1.4em" @change="savePrefs" />
        </div>
        <div class="d-flex align-items-center gap-2 small">Remind me <select v-model.number="prefs.deadline_days_before" class="form-select form-select-sm" style="width:auto" @change="savePrefs"><option v-for="d in [1,3,7,14,30]" :key="d" :value="d">{{ d }}</option></select> days before a deadline.</div>
      </div>
      <div v-else class="skeleton" style="height: 120px" />
    </section>

    <section class="fs-card fs-card-pad">
      <h2 class="h6 fw-bold mb-3">Change password</h2>
      <form class="row g-2" @submit.prevent="changePw">
        <div class="col-md-5"><input v-model="pw.current_password" type="password" class="form-control" placeholder="Current password" autocomplete="current-password" aria-label="Current password" /></div>
        <div class="col-md-5"><input v-model="pw.new_password" type="password" class="form-control" placeholder="New password" autocomplete="new-password" aria-label="New password" /></div>
        <div class="col-md-2 d-grid"><button class="btn btn-soft" :disabled="!pw.current_password || !pw.new_password">Update</button></div>
      </form>
    </section>

    <section class="fs-card fs-card-pad">
      <h2 class="h6 fw-bold mb-1">Privacy</h2>
      <p class="small text-muted">Download everything FormSaathi stores about you, or delete your account and all personal data.</p>
      <div class="d-flex flex-wrap gap-2">
        <button class="btn btn-soft" @click="exportData"><Download :size="16" /> Download my data</button>
        <button class="btn btn-outline-danger" @click="deleteOpen = true"><Trash2 :size="16" /> Delete account</button>
        <button v-if="IS_PREVIEW" class="btn btn-ghost" @click="resetAll"><RotateCcw :size="16" /> Reset preview data</button>
      </div>
    </section>

    <section class="fs-card fs-card-pad">
      <h2 class="h6 fw-bold mb-1">Send feedback</h2>
      <p class="small text-muted">Found a bug or have an idea? We read everything.</p>
      <div class="d-flex gap-2 flex-wrap"><select v-model="fb.kind" class="form-select" style="max-width: 160px" aria-label="Feedback type"><option value="idea">Idea</option><option value="bug">Bug</option><option value="praise">Praise</option><option value="other">Other</option></select><input v-model="fb.message" class="form-control flex-grow-1" style="min-width: 200px" placeholder="Your feedback" aria-label="Feedback" /><button class="btn btn-soft" :disabled="fb.message.trim().length < 5" @click="sendFb">Send</button></div>
    </section>

    <AppModal :open="deleteOpen" title="Delete your account?" subtitle="This permanently deletes your profile, tracker, documents and chats. It can’t be undone." @close="deleteOpen = false">
      <label class="form-label" for="dpw">Enter your password to confirm</label>
      <input id="dpw" v-model="deletePw" type="password" class="form-control" :class="{ 'is-invalid': deleteErr }" autocomplete="current-password" />
      <div v-if="deleteErr" class="invalid-feedback">{{ deleteErr }}</div>
      <template #footer><button class="btn btn-ghost" @click="deleteOpen = false">Cancel</button><button class="btn btn-danger" :disabled="!deletePw" @click="deleteAccount">Delete everything</button></template>
    </AppModal>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { Download, Moon, RotateCcw, Sun, Trash2 } from 'lucide-vue-next'
import api, { IS_PREVIEW } from '@/api'
import { setLanguage } from '@/i18n'
import { useAuth } from '@/stores/auth'
import { useUi } from '@/stores/ui'
import { LABELS } from '@/utils/format'
import AppModal from '@/components/AppModal.vue'

const PREF_ROWS = [
  { key: 'deadline_reminders', label: 'Deadline reminders', help: 'For saved and tracked opportunities.' },
  { key: 'document_reminders', label: 'Missing document reminders', help: 'When a tracked application is missing documents, or a certificate is expiring.' },
  { key: 'status_reminders', label: 'Status check-ins', help: 'A nudge to update applications that have been “Applied” for a while.' },
  { key: 'opportunity_updates', label: 'Opportunity updates', help: 'When a correction you reported is reviewed.' },
  { key: 'email_enabled', label: 'Also send by email', help: 'Deadline and reminder notifications by email.' },
]
const { locale } = useI18n()
const ui = useUi()
const auth = useAuth()
const router = useRouter()
const prefs = ref(null)
const emailConfigured = ref(false)
const pw = reactive({ current_password: '', new_password: '' })
const fb = reactive({ kind: 'idea', message: '' })
const deleteOpen = ref(false)
const deletePw = ref('')
const deleteErr = ref('')

onMounted(async () => {
  try { const r = await api.get('/notifications/preferences'); prefs.value = r.preferences; emailConfigured.value = r.email_configured } catch (e) { ui.error(e) }
})
function lang(k) { setLanguage(k); auth.updateProfile({ preferred_language: k }).catch(() => {}) }
async function savePrefs() { try { await api.put('/notifications/preferences', prefs.value); ui.toast('Preferences saved.') } catch (e) { ui.error(e) } }
async function changePw() {
  try { ui.toast((await api.post('/auth/change-password', pw)).message); pw.current_password = ''; pw.new_password = '' } catch (e) { ui.toast(Object.values(e.fields || {})[0] || e.message, 'error') }
}
async function exportData() {
  try {
    const data = await api.get('/profile/export')
    const a = document.createElement('a')
    a.href = URL.createObjectURL(new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' }))
    a.download = 'formsaathi-my-data.json'; a.click()
  } catch (e) { ui.error(e) }
}
async function deleteAccount() {
  deleteErr.value = ''
  try { await api.delete('/profile/account', { password: deletePw.value }); auth.setUser(null); ui.toast('Your account has been deleted.'); router.push('/') } catch (e) { deleteErr.value = e.fields?.password || e.message }
}
async function sendFb() { try { ui.toast((await api.post('/feedback', { ...fb, page: '/app/settings' })).message); fb.message = '' } catch (e) { ui.error(e) } }
async function resetAll() {
  if (!(await ui.confirm({ title: 'Reset the preview?', message: 'This clears all accounts and data stored in this browser and reloads the demo.', confirmText: 'Reset', danger: true }))) return
  const { resetPreview } = await import('@/api/preview/server.js')
  resetPreview(); window.location.reload()
}
</script>
