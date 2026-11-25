<template>
  <header class="fs-navbar" :class="{ scrolled, 'over-hero': overHero }">
    <nav class="container d-flex align-items-center gap-2 py-2" aria-label="Main">
      <router-link to="/" class="me-auto me-lg-4 text-decoration-none"><AppLogo :size="34" /></router-link>
      <div class="d-none d-lg-flex gap-1 me-auto">
        <router-link class="nav-link" to="/" exact-active-class="router-link-active">{{ t('nav.home') }}</router-link>
        <router-link class="nav-link" to="/explore">{{ t('nav.explore') }}</router-link>
        <router-link class="nav-link" to="/how-it-works">{{ t('nav.how') }}</router-link>
        <router-link class="nav-link" to="/about">{{ t('nav.about') }}</router-link>
      </div>
      <LanguageSwitcher />
      <button class="btn btn-ghost btn-icon" :aria-label="ui.theme === 'dark' ? 'Light mode' : 'Dark mode'" @click="ui.toggleTheme()">
        <Sun v-if="ui.theme === 'dark'" :size="18" /><Moon v-else :size="18" />
      </button>
      <template v-if="auth.isLoggedIn">
        <router-link :to="auth.isAdmin ? '/admin' : '/app'" class="btn btn-primary btn-pill d-none d-sm-inline-flex">{{ t('nav.dashboard') }}</router-link>
      </template>
      <template v-else>
        <router-link to="/login" class="btn btn-ghost d-none d-sm-inline-flex">{{ t('nav.login') }}</router-link>
        <router-link to="/register" class="btn btn-primary btn-pill d-none d-sm-inline-flex">{{ t('nav.start') }}</router-link>
      </template>
      <button class="btn btn-ghost btn-icon d-lg-none" :aria-expanded="menu" aria-label="Menu" @click="menu = !menu"><Menu :size="22" /></button>
    </nav>
    <div v-if="menu" class="d-lg-none border-top border-soft bg-surface">
      <div class="container py-3 d-grid gap-1" @click="menu = false">
        <router-link class="nav-link" to="/">{{ t('nav.home') }}</router-link>
        <router-link class="nav-link" to="/explore">{{ t('nav.explore') }}</router-link>
        <router-link class="nav-link" to="/how-it-works">{{ t('nav.how') }}</router-link>
        <router-link class="nav-link" to="/about">{{ t('nav.about') }}</router-link>
        <div class="d-flex gap-2 mt-2">
          <template v-if="auth.isLoggedIn"><router-link :to="auth.isAdmin ? '/admin' : '/app'" class="btn btn-primary flex-fill">{{ t('nav.dashboard') }}</router-link></template>
          <template v-else>
            <router-link to="/login" class="btn btn-outline-primary flex-fill">{{ t('nav.login') }}</router-link>
            <router-link to="/register" class="btn btn-primary flex-fill">{{ t('nav.start') }}</router-link>
          </template>
        </div>
      </div>
    </div>
  </header>

  <main id="main"><slot /></main>

  <footer class="footer border-top border-soft mt-5">
    <div class="container py-5">
      <div class="row g-4">
        <div class="col-lg-4">
          <AppLogo :size="32" />
          <p class="text-muted mt-3 mb-3" style="max-width: 320px">{{ t('footer.tagline') }} A personal assistant for scholarships, internships, schemes, exams and jobs.</p>
          <div class="d-flex gap-2">
            <a class="btn btn-ghost btn-icon" href="https://github.com/anjalikokare/formsaathi" target="_blank" rel="noopener" aria-label="FormSaathi on GitHub"><Github :size="18" /></a>
            <router-link class="btn btn-ghost btn-icon" to="/contact" aria-label="Contact us"><Mail :size="18" /></router-link>
          </div>
        </div>
        <div class="col-6 col-lg-2">
          <div class="small-caps mb-3">Product</div>
          <ul class="list-unstyled d-grid gap-2 small">
            <li><router-link to="/explore">Explore</router-link></li>
            <li><router-link to="/how-it-works">How it works</router-link></li>
            <li><router-link to="/register">Create account</router-link></li>
          </ul>
        </div>
        <div class="col-6 col-lg-2">
          <div class="small-caps mb-3">Company</div>
          <ul class="list-unstyled d-grid gap-2 small">
            <li><router-link to="/about">About</router-link></li>
            <li><router-link to="/contact">Contact</router-link></li>
            <li><router-link to="/help">Help Center</router-link></li>
          </ul>
        </div>
        <div class="col-6 col-lg-2">
          <div class="small-caps mb-3">Legal</div>
          <ul class="list-unstyled d-grid gap-2 small">
            <li><router-link to="/privacy">Privacy Policy</router-link></li>
            <li><router-link to="/terms">Terms</router-link></li>
          </ul>
        </div>
        <div class="col-6 col-lg-2">
          <div class="small-caps mb-3">Official portals</div>
          <ul class="list-unstyled d-grid gap-2 small">
            <li v-for="p in meta.portals.slice(0, 3)" :key="p.url"><a :href="p.url" target="_blank" rel="noopener">{{ p.name }}</a></li>
          </ul>
        </div>
      </div>
      <hr class="border-soft my-4" />
      <p class="small text-muted mb-0">© {{ new Date().getFullYear() }} FormSaathi. FormSaathi is an independent guide and is not affiliated with any government body. Always confirm details on the official source. AI guidance is not official advice.</p>
    </div>
  </footer>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { Github, Mail, Menu, Moon, Sun } from 'lucide-vue-next'
import AppLogo from '@/components/AppLogo.vue'
import LanguageSwitcher from '@/components/LanguageSwitcher.vue'
import { useAuth } from '@/stores/auth'
import { useMeta } from '@/stores/meta'
import { useUi } from '@/stores/ui'

const { t } = useI18n()
const auth = useAuth()
const meta = useMeta()
const ui = useUi()
const menu = ref(false)
const scrolled = ref(false)
const onScroll = () => { scrolled.value = window.scrollY > 8 }
// On the homepage the navbar sits transparently over the photo hero until the page scrolls.
const route = useRoute()
const overHero = computed(() => route.path === '/' && !scrolled.value && !menu.value)
onMounted(() => window.addEventListener('scroll', onScroll, { passive: true }))
onBeforeUnmount(() => window.removeEventListener('scroll', onScroll))
</script>
