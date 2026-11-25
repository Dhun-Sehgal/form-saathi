<template>
  <div class="fs-card overflow-hidden">
    <div class="chat-wrap">
      <aside class="chat-history" :class="{ 'show-mobile': showHistory }" aria-label="Conversations">
        <div class="p-3 d-flex gap-2 align-items-center border-bottom border-soft">
          <button class="btn btn-primary btn-sm flex-grow-1" @click="newChat()"><Plus :size="16" /> New chat</button>
          <button class="btn btn-ghost btn-icon d-lg-none" aria-label="Close history" @click="showHistory = false"><X :size="18" /></button>
        </div>
        <div class="p-2 d-grid gap-1">
          <p v-if="!sessions.length" class="small text-muted p-2 mb-0">No conversations yet.</p>
          <div v-for="s in sessions" :key="s.id" class="d-flex align-items-center rounded-3" :class="{ 'bg-lavender': current?.id === s.id }">
            <button class="btn btn-ghost flex-grow-1 text-start justify-content-start small text-truncate" @click="open(s.id)"><MessageSquare :size="15" class="flex-shrink-0" /><span class="text-truncate">{{ s.title }}</span></button>
            <button class="btn btn-ghost btn-sm" :aria-label="'Delete ' + s.title" @click="remove(s)"><Trash2 :size="14" /></button>
          </div>
        </div>
      </aside>

      <section class="chat-main">
        <header class="d-flex align-items-center gap-2 px-3 py-2 border-bottom border-soft">
          <button class="btn btn-ghost btn-icon d-lg-none" aria-label="Show conversations" @click="showHistory = true"><History :size="18" /></button>
          <span class="icon-tile icon-tile-sm tint-lavender"><Bot /></span>
          <div class="min-w-0 flex-grow-1">
            <div class="fw-bold small">Saathi AI</div>
            <div class="small text-muted text-truncate">
              <template v-if="current?.opportunity">About: <router-link :to="`/app/opportunities/${current.opportunity.slug}`">{{ current.opportunity.title }}</router-link></template>
              <template v-else>Your application guide</template>
            </div>
          </div>
          <select v-model="language" class="form-select form-select-sm" style="width:auto" aria-label="Answer language"><option value="en">English</option><option value="hi">हिन्दी</option><option value="mr">मराठी</option></select>
        </header>

        <div ref="scroller" class="chat-scroll" aria-live="polite">
          <div v-if="!configured" class="alert alert-warning d-flex gap-2 small">
            <CircleAlert :size="18" class="flex-shrink-0" />
            <div><strong>Saathi AI isn’t available here yet.</strong> {{ IS_PREVIEW ? 'This browser-only preview has no AI server.' : 'The server administrator needs to add an AI API key (LLM_API_KEY).' }} Eligibility checks, checklists and everything else still work.</div>
          </div>

          <div v-if="!messages.length" class="text-center py-4">
            <span class="icon-tile mx-auto mb-3 tint-lavender" style="width:4rem;height:4rem"><Bot /></span>
            <h1 class="h4 fw-bold">Namaste! How can I help?</h1>
            <p class="text-muted small mx-auto" style="max-width: 460px">I explain forms, rules and difficult terms in simple English, Hindi or Marathi. I don’t make up rules — for exact details, I’ll point you to the official source.</p>
            <div class="d-flex flex-wrap justify-content-center gap-2 mt-3">
              <button v-for="p in prompts" :key="p" class="choice-chip" :disabled="!configured" @click="send(p)">{{ p }}</button>
            </div>
          </div>

          <div v-for="m in messages" :key="m.id" class="d-flex mb-3" :class="m.role === 'user' ? 'justify-content-end' : ''">
            <div class="bubble" :class="m.role === 'user' ? 'bubble-user' : 'bubble-ai'">
              {{ m.content }}
              <div v-if="m.role === 'assistant'" class="mt-2"><span class="fs-badge fs-badge-ai"><Sparkles /> AI guidance · not official advice</span></div>
            </div>
          </div>
          <div v-if="sending" class="d-flex mb-3"><div class="bubble bubble-ai typing" aria-label="Saathi is typing"><span /><span /><span /></div></div>
        </div>

        <form class="border-top border-soft p-2 p-md-3 d-flex gap-2" @submit.prevent="send()">
          <textarea v-model="draft" class="form-control" rows="1" style="resize:none" :placeholder="configured ? 'Ask about a form, a rule or a word you don’t understand…' : 'Saathi AI is not configured'" :disabled="!configured || sending" maxlength="2000" aria-label="Message" @keydown.enter.exact.prevent="send()" />
          <button class="btn btn-primary btn-icon flex-shrink-0" :disabled="!configured || sending || !draft.trim()" aria-label="Send"><SendHorizontal :size="18" /></button>
        </form>
        <p class="small text-muted text-center mb-2 px-3" style="font-size:.72rem">Saathi AI can make mistakes. It is not official government advice — always confirm on the official source.</p>
      </section>
    </div>
  </div>
</template>

<script setup>
import { nextTick, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Bot, CircleAlert, History, MessageSquare, Plus, SendHorizontal, Sparkles, Trash2, X } from 'lucide-vue-next'
import api, { IS_PREVIEW } from '@/api'
import { useAuth } from '@/stores/auth'
import { useUi } from '@/stores/ui'

const route = useRoute()
const router = useRouter()
const auth = useAuth()
const ui = useUi()
const sessions = ref([])
const current = ref(null)
const messages = ref([])
const configured = ref(true)
const draft = ref('')
const sending = ref(false)
const showHistory = ref(false)
const scroller = ref(null)
const language = ref(auth.profile.preferred_language || 'en')
const prompts = ['What is a domicile certificate?', 'Make a checklist for a scholarship application', 'What does “non-creamy layer” mean?', 'How do I get an income certificate?']

async function loadSessions() {
  const r = await api.get('/ai/sessions')
  sessions.value = r.items; configured.value = r.configured
}
async function open(id) {
  showHistory.value = false
  const r = await api.get(`/ai/sessions/${id}`)
  current.value = r.session; messages.value = r.session.messages; configured.value = r.configured; language.value = r.session.language
  router.replace({ query: { session: id } })
  scrollDown()
}
async function newChat(opportunityId = null) {
  showHistory.value = false
  const r = await api.post('/ai/sessions', { language: language.value, opportunity_id: opportunityId })
  current.value = r.session; messages.value = []
  router.replace({ query: { session: r.session.id } })
  await loadSessions()
}
async function send(text) {
  const content = (text ?? draft.value).trim()
  if (!content || sending.value) return
  if (!current.value) await newChat()
  draft.value = ''
  const temp = { id: 'tmp' + Date.now(), role: 'user', content }
  messages.value.push(temp); sending.value = true; scrollDown()
  try {
    const r = await api.post(`/ai/sessions/${current.value.id}/messages`, { content })
    messages.value.splice(messages.value.indexOf(temp), 1, r.user_message, r.assistant_message)
    current.value.title = r.title
    loadSessions()
  } catch (e) {
    messages.value.splice(messages.value.indexOf(temp), 1)
    draft.value = content
    if (e.code === 'ai_not_configured') configured.value = false
    ui.error(e)
  } finally { sending.value = false; scrollDown() }
}
async function remove(s) {
  if (!(await ui.confirm({ title: 'Delete this conversation?', message: 'This removes the chat history permanently.', confirmText: 'Delete', danger: true }))) return
  await api.delete(`/ai/sessions/${s.id}`)
  if (current.value?.id === s.id) { current.value = null; messages.value = []; router.replace({ query: {} }) }
  loadSessions()
}
async function scrollDown() { await nextTick(); if (scroller.value) scroller.value.scrollTop = scroller.value.scrollHeight }
watch(language, async (lang) => {
  // Language is set per conversation; start a fresh one if the current chat already has messages.
  if (current.value && messages.value.length && current.value.language !== lang) { current.value = null; messages.value = []; router.replace({ query: {} }) }
})

onMounted(async () => {
  try {
    await loadSessions()
    if (route.query.session) await open(route.query.session)
  } catch (e) { ui.error(e) }
})
</script>
