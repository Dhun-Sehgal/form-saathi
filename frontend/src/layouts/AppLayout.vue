<template>
  <ShellLayout :nav="nav" :tabs="tabs" home="/app"><slot /></ShellLayout>
</template>

<script setup>
import { computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { Bell, Bookmark, Bot, CalendarDays, Compass, FileText, KanbanSquare, LayoutDashboard, Settings, User } from 'lucide-vue-next'
import api from '@/api'
import { useUi } from '@/stores/ui'
import ShellLayout from './ShellLayout.vue'

const { t } = useI18n()
const ui = useUi()
const route = useRoute()

const nav = computed(() => [
  { to: '/app', label: t('nav.dashboard'), icon: LayoutDashboard, exact: true },
  { to: '/app/discover', label: t('nav.discover'), icon: Compass },
  { to: '/app/saved', label: t('nav.saved'), icon: Bookmark },
  { to: '/app/tracker', label: t('nav.tracker'), icon: KanbanSquare },
  { to: '/app/documents', label: t('nav.documents'), icon: FileText },
  { to: '/app/calendar', label: t('nav.calendar'), icon: CalendarDays },
  { to: '/app/saathi', label: t('nav.saathi'), icon: Bot },
  { section: 'Account' },
  { to: '/app/notifications', label: t('nav.notifications'), icon: Bell, badge: ui.unread || null },
  { to: '/app/profile', label: t('nav.profile'), icon: User },
  { to: '/app/settings', label: t('nav.settings'), icon: Settings },
])
const tabs = computed(() => [
  { to: '/app', label: t('nav.home'), icon: LayoutDashboard, exact: true },
  { to: '/app/discover', label: t('nav.discover'), icon: Compass },
  { to: '/app/tracker', label: t('nav.tracker'), icon: KanbanSquare },
  { to: '/app/saathi', label: 'Saathi', icon: Bot },
])

async function refreshUnread() {
  try { ui.unread = (await api.get('/notifications', { unread: '1', limit: 1 })).unread } catch { /* non-critical */ }
}
onMounted(refreshUnread)
watch(() => route.name, refreshUnread)
</script>
