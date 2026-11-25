<!-- Shared shell for the user app and the admin panel: collapsible sidebar, top bar, mobile tab bar. -->
<template>
  <div class="app-shell">
    <aside class="app-sidebar" :class="{ collapsed: ui.sidebarCollapsed }" aria-label="Sidebar">
      <div class="d-flex align-items-center justify-content-between px-3 py-3">
        <router-link :to="home" class="text-decoration-none"><AppLogo :size="32" :icon-only="ui.sidebarCollapsed" /></router-link>
      </div>
      <nav class="flex-grow-1 overflow-auto px-2 pb-3 d-grid gap-1 align-content-start">
        <template v-for="item in nav" :key="item.to || item.section">
          <div v-if="item.section" class="side-section small-caps">{{ item.section }}</div>
          <router-link v-else :to="item.to" class="side-link" :title="item.label" :exact-active-class="item.exact ? 'router-link-active' : ''" :active-class="item.exact ? '' : 'router-link-active'">
            <component :is="item.icon" /><span class="side-label flex-grow-1">{{ item.label }}</span>
            <span v-if="item.badge" class="badge rounded-pill text-bg-danger side-label">{{ item.badge }}</span>
          </router-link>
        </template>
      </nav>
      <div class="p-2 border-top border-soft">
        <button class="side-link w-100 border-0 bg-transparent d-none d-lg-flex" :aria-label="ui.sidebarCollapsed ? 'Expand sidebar' : 'Collapse sidebar'" @click="ui.toggleSidebar()">
          <PanelLeftOpen v-if="ui.sidebarCollapsed" /><PanelLeftClose v-else /><span class="side-label">Collapse</span>
        </button>
      </div>
    </aside>

    <div class="app-main">
      <header class="app-topbar">
        <div class="d-flex align-items-center gap-2 px-3 px-md-4 py-2">
          <router-link :to="home" class="d-md-none text-decoration-none me-1"><AppLogo :size="30" icon-only /></router-link>
          <form class="d-none d-md-flex align-items-center flex-grow-1" style="max-width: 460px" role="search" @submit.prevent="search">
            <div class="smart-search w-100 py-1" style="box-shadow:none">
              <Search :size="18" class="text-muted" />
              <input v-model="q" type="search" placeholder="Search opportunities…" aria-label="Search opportunities" />
            </div>
          </form>
          <div class="ms-auto d-flex align-items-center gap-1">
            <button class="btn btn-ghost btn-icon d-md-none" aria-label="Search" @click="$router.push('/app/discover')"><Search :size="20" /></button>
            <LanguageSwitcher />
            <button class="btn btn-ghost btn-icon" :aria-label="ui.theme === 'dark' ? 'Light mode' : 'Dark mode'" @click="ui.toggleTheme()"><Sun v-if="ui.theme === 'dark'" :size="19" /><Moon v-else :size="19" /></button>
            <router-link to="/app/notifications" class="btn btn-ghost btn-icon position-relative" aria-label="Notifications">
              <Bell :size="20" />
              <span v-if="ui.unread" class="position-absolute badge rounded-pill bg-danger" style="top:4px; right:2px; font-size:.6rem">{{ ui.unread > 9 ? '9+' : ui.unread }}</span>
            </router-link>
            <DropMenu>
              <template #trigger>
                <button class="btn btn-ghost d-flex align-items-center gap-2 px-2" aria-label="Account menu">
                  <span class="rounded-circle d-grid fw-bold" style="width:34px;height:34px;place-items:center;background:var(--fs-lavender);color:var(--fs-primary);font-size:.8rem">{{ initials(auth.profile.full_name) }}</span>
                  <ChevronDown :size="16" class="d-none d-sm-block" />
                </button>
              </template>
              <div class="px-3 py-2 small"><div class="fw-semibold text-truncate">{{ auth.profile.full_name }}</div><div class="text-muted text-truncate">{{ auth.user?.email }}</div></div>
              <hr class="my-1" />
              <router-link class="dropdown-item" to="/app/profile"><User :size="16" /> Profile</router-link>
              <router-link class="dropdown-item" to="/app/settings"><Settings :size="16" /> Settings</router-link>
              <router-link v-if="auth.isAdmin && variant === 'app'" class="dropdown-item" to="/admin"><ShieldCheck :size="16" /> Admin panel</router-link>
              <router-link v-if="variant === 'admin'" class="dropdown-item" to="/app"><LayoutDashboard :size="16" /> User app</router-link>
              <hr class="my-1" />
              <button class="dropdown-item" @click="logout"><LogOut :size="16" /> {{ t('nav.logout') }}</button>
            </DropMenu>
          </div>
        </div>
      </header>
      <main id="main" class="app-content"><slot /></main>
    </div>

    <nav class="mobile-tabbar d-md-none" aria-label="Primary">
      <router-link v-for="tab in tabs" :key="tab.to" :to="tab.to" :exact-active-class="tab.exact ? 'router-link-active' : ''" :active-class="tab.exact ? '' : 'router-link-active'">
        <component :is="tab.icon" /><span>{{ tab.label }}</span>
      </router-link>
      <button :class="{ 'router-link-active': more }" @click="more = !more"><Menu /><span>{{ t('nav.more') }}</span></button>
    </nav>
    <AppModal :open="more" title="Menu" @close="more = false">
      <div class="d-grid gap-1" @click="more = false">
        <router-link v-for="item in nav.filter((n) => n.to)" :key="item.to" :to="item.to" class="side-link border rounded-3 border-soft"><component :is="item.icon" :size="20" /> {{ item.label }}</router-link>
        <button class="side-link border rounded-3 border-soft bg-transparent text-start" @click="logout"><LogOut :size="20" /> {{ t('nav.logout') }}</button>
      </div>
    </AppModal>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { Bell, ChevronDown, LayoutDashboard, LogOut, Menu, Moon, PanelLeftClose, PanelLeftOpen, Search, Settings, ShieldCheck, Sun, User } from 'lucide-vue-next'
import AppLogo from '@/components/AppLogo.vue'
import AppModal from '@/components/AppModal.vue'
import DropMenu from '@/components/DropMenu.vue'
import LanguageSwitcher from '@/components/LanguageSwitcher.vue'
import { useAuth } from '@/stores/auth'
import { useUi } from '@/stores/ui'
import { initials } from '@/utils/format'

defineProps({ nav: Array, tabs: Array, home: String, variant: { type: String, default: 'app' } })
const { t } = useI18n()
const auth = useAuth()
const ui = useUi()
const router = useRouter()
const q = ref('')
const more = ref(false)

function search() { router.push({ path: '/app/discover', query: q.value ? { q: q.value } : {} }) }
async function logout() {
  more.value = false
  await auth.logout()
  ui.toast('You have been logged out.')
  router.push('/')
}
</script>
