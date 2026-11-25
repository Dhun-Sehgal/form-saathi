<template>
  <a href="#main" class="skip-link">Skip to content</a>
  <div v-if="IS_PREVIEW && !bannerHidden" class="preview-banner" role="note">
    ✨ <strong>Preview mode:</strong> everything runs in your browser with demo data — nothing is sent to a server.
    <a href="https://github.com/anjalikokare/formsaathi#deploy-the-full-app" target="_blank" rel="noopener">Deploy the full app</a>
    <button class="btn-close position-absolute top-50 end-0 translate-middle-y me-3" style="font-size:.65rem" aria-label="Hide preview notice" @click="hideBanner" />
  </div>
  <component :is="layout">
    <router-view v-slot="{ Component, route }">
      <component :is="Component" :key="route.name === 'opportunity' || route.name === 'app-opportunity' ? route.fullPath : route.name" />
    </router-view>
  </component>
  <ToastHost />
  <ConfirmDialog />
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { IS_PREVIEW } from '@/api'
import { useUi } from '@/stores/ui'
import { useMeta } from '@/stores/meta'
import PublicLayout from '@/layouts/PublicLayout.vue'
import AppLayout from '@/layouts/AppLayout.vue'
import AdminLayout from '@/layouts/AdminLayout.vue'
import BareLayout from '@/layouts/BareLayout.vue'
import ToastHost from '@/components/ToastHost.vue'
import ConfirmDialog from '@/components/ConfirmDialog.vue'

const route = useRoute()
const ui = useUi()
const meta = useMeta()
ui.applyTheme()
const bannerHidden = ref(sessionStorage.getItem('fs-preview-banner') === 'hidden')
function hideBanner() { bannerHidden.value = true; sessionStorage.setItem('fs-preview-banner', 'hidden') }
onMounted(() => meta.load().catch(() => {}))

const layout = computed(() => {
  if (route.meta.bare) return BareLayout
  return { app: AppLayout, admin: AdminLayout, bare: BareLayout }[route.meta.layout] || PublicLayout
})
</script>
