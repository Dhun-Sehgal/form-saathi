<template>
  <div class="min-vh-100 d-flex flex-column" style="background: radial-gradient(1200px 500px at 10% -10%, var(--fs-lavender), transparent 60%), var(--fs-bg)">
    <header class="container d-flex align-items-center py-3">
      <router-link to="/" class="me-auto text-decoration-none"><AppLogo :size="34" /></router-link>
      <LanguageSwitcher />
      <button class="btn btn-ghost btn-icon" aria-label="Toggle dark mode" @click="ui.toggleTheme()"><Sun v-if="ui.theme === 'dark'" :size="18" /><Moon v-else :size="18" /></button>
    </header>
    <main id="main" class="flex-grow-1 d-flex align-items-start align-items-md-center justify-content-center px-3 pb-5 pt-2">
      <slot />
    </main>
  </div>
</template>

<script setup>
import { Moon, Sun } from 'lucide-vue-next'
import AppLogo from '@/components/AppLogo.vue'
import LanguageSwitcher from '@/components/LanguageSwitcher.vue'
import { useUi } from '@/stores/ui'
const ui = useUi()
</script>
