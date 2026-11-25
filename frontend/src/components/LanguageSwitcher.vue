<template>
  <DropMenu>
    <template #trigger>
      <button class="btn btn-ghost btn-sm" aria-label="Change language" title="Language"><Languages :size="18" /><span class="d-none d-sm-inline">{{ LABELS.language[locale] }}</span></button>
    </template>
    <button v-for="(name, code) in LABELS.language" :key="code" class="dropdown-item" :class="{ active: locale === code }" @click="change(code)">
      {{ name }}
    </button>
  </DropMenu>
</template>

<script setup>
import { Languages } from 'lucide-vue-next'
import { useI18n } from 'vue-i18n'
import api from '@/api'
import { setLanguage } from '@/i18n'
import { useAuth } from '@/stores/auth'
import { LABELS } from '@/utils/format'
import DropMenu from './DropMenu.vue'

const { locale } = useI18n()
const auth = useAuth()
function change(code) {
  setLanguage(code)
  if (auth.isLoggedIn) api.put('/profile', { preferred_language: code }).then((r) => auth.setUser(r.user)).catch(() => {})
}
</script>
