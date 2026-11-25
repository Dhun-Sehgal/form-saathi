<template>
  <div style="max-width: 860px">
    <div class="d-flex flex-wrap align-items-end gap-2 mb-4">
      <div class="me-auto"><h1 class="page-title">Notifications</h1><p class="page-sub">Deadlines, missing documents, reminders and updates.</p></div>
      <router-link to="/app/settings#notifications" class="btn btn-ghost btn-sm"><Settings2 :size="16" /> Preferences</router-link>
      <button class="btn btn-soft btn-sm" :disabled="!unread" @click="readAll"><CheckCheck :size="16" /> Mark all read</button>
    </div>
    <div class="d-flex gap-2 mb-3">
      <button class="choice-chip" :class="{ active: !onlyUnread }" @click="onlyUnread = false; load()">All</button>
      <button class="choice-chip" :class="{ active: onlyUnread }" @click="onlyUnread = true; load()">Unread <span class="text-muted">{{ unread }}</span></button>
    </div>
    <StateBlock v-if="loading" kind="loading" :count="3" col-class="col-12" />
    <StateBlock v-else-if="error" kind="error" :message="error" @retry="load" />
    <StateBlock v-else-if="!items.length" title="You’re all caught up" message="Save or track opportunities and we’ll let you know about deadlines and missing documents." />
    <div v-else class="fs-card">
      <button v-for="n in items" :key="n.id" class="d-flex gap-3 p-3 w-100 text-start border-0 border-bottom border-soft bg-transparent" :style="{ background: n.is_read ? '' : 'var(--fs-primary-50) !important' }" @click="openN(n)">
        <span class="icon-tile icon-tile-sm" :class="TYPES[n.type]?.tint || 'tint-lavender'"><component :is="TYPES[n.type]?.icon || Bell" /></span>
        <div class="flex-grow-1 min-w-0"><div class="small" :class="n.is_read ? '' : 'fw-bold'">{{ n.title }}</div><div v-if="n.body" class="small text-muted">{{ n.body }}</div><div class="small text-muted">{{ timeAgo(n.created_at) }}</div></div>
        <span v-if="!n.is_read" class="status-dot mt-2" style="background: var(--fs-primary)" aria-label="Unread" />
      </button>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { AlarmClock, Bell, CalendarClock, CheckCheck, FileWarning, Megaphone, MessageSquareReply, RefreshCw, Settings2 } from 'lucide-vue-next'
import api from '@/api'
import { useUi } from '@/stores/ui'
import { timeAgo } from '@/utils/format'
import StateBlock from '@/components/StateBlock.vue'

const TYPES = {
  deadline: { icon: CalendarClock, tint: 'tint-peach' }, document_missing: { icon: FileWarning, tint: 'tint-butter' },
  status_reminder: { icon: RefreshCw, tint: 'tint-sky' }, reminder: { icon: AlarmClock, tint: 'tint-lavender' },
  correction_update: { icon: MessageSquareReply, tint: 'tint-mint' }, announcement: { icon: Megaphone, tint: 'tint-lilac' },
}
const router = useRouter()
const ui = useUi()
const items = ref([])
const unread = ref(0)
const onlyUnread = ref(false)
const loading = ref(true)
const error = ref('')

async function load() {
  loading.value = true; error.value = ''
  try { const r = await api.get('/notifications', onlyUnread.value ? { unread: '1' } : {}); items.value = r.items; unread.value = r.unread; ui.unread = r.unread } catch (e) { error.value = e.message } finally { loading.value = false }
}
onMounted(load)
async function openN(n) {
  if (!n.is_read) { try { await api.post(`/notifications/${n.id}/read`); n.is_read = true; unread.value--; ui.unread = unread.value } catch { /* ignore */ } }
  if (n.link) router.push(n.link)
}
async function readAll() { try { await api.post('/notifications/read-all'); load() } catch (e) { ui.error(e) } }
</script>
