<template>
  <StateBlock v-if="loading" kind="loading" :count="4" col-class="col-md-6 col-xl-3" />
  <StateBlock v-else-if="error" kind="error" :message="error" @retry="load" />
  <div v-else>
    <div class="d-flex flex-wrap align-items-end gap-2 mb-4">
      <div class="me-auto"><h1 class="page-title">Admin overview</h1><p class="page-sub">Platform health, verification queue and engagement.</p></div>
      <router-link to="/admin/opportunities/new" class="btn btn-primary"><Plus :size="17" /> Add opportunity</router-link>
    </div>
    <div class="row g-3 mb-4">
      <div v-for="c in cards" :key="c.label" class="col-6 col-xl-3">
        <router-link :to="c.to" class="fs-card fs-card-hover stat-card d-block text-decoration-none h-100"><div class="stat-value" style="color: var(--fs-text)">{{ c.value }}</div><div class="stat-label">{{ c.label }}</div><div v-if="c.sub" class="small text-muted mt-1">{{ c.sub }}</div></router-link>
      </div>
    </div>
    <div class="row g-4">
      <div class="col-lg-6">
        <section class="fs-card fs-card-pad h-100">
          <h2 class="h6 fw-bold mb-3">Verification status</h2>
          <div class="d-grid gap-2">
            <router-link v-for="(n, k) in s.opportunities.by_verification" :key="k" :to="{ path: '/admin/opportunities', query: { verification_status: k } }" class="d-flex justify-content-between small p-2 rounded-3 border border-soft text-decoration-none" style="color: var(--fs-text)"><span>{{ label('verification', k) }}</span><span class="fw-bold">{{ n }}</span></router-link>
          </div>
          <p v-if="s.opportunities.stale_verification" class="small text-warning mt-3 mb-0">{{ s.opportunities.stale_verification }} verified listing(s) were last checked more than 30 days ago.</p>
          <p class="small text-muted mt-3 mb-0">{{ s.opportunities.demo }} demo listing(s) are on the site. Remove them with <code>flask purge-demo</code> before launch.</p>
        </section>
      </div>
      <div class="col-lg-6">
        <section class="fs-card fs-card-pad h-100">
          <h2 class="h6 fw-bold mb-3">Applications by status</h2>
          <div v-if="s.applications.total" class="d-grid gap-2">
            <div v-for="(n, k) in s.applications.by_status" :key="k" class="d-flex align-items-center gap-3 small"><span style="width: 150px">{{ label('status', k) }}</span><div class="progress flex-grow-1"><div class="progress-bar" :style="{ width: (n / s.applications.total) * 100 + '%' }" /></div><span class="fw-semibold" style="width: 28px">{{ n }}</span></div>
          </div>
          <p v-else class="small text-muted mb-0">No applications tracked yet.</p>
          <h3 class="h6 fw-bold mt-4 mb-2">Most saved</h3>
          <ol v-if="s.top_saved.length" class="small ps-3 mb-0"><li v-for="t in s.top_saved" :key="t.title">{{ t.title }} <span class="text-muted">({{ t.count }})</span></li></ol>
          <p v-else class="small text-muted mb-0">Nothing saved yet.</p>
        </section>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { Plus } from 'lucide-vue-next'
import api from '@/api'
import { label } from '@/utils/format'
import StateBlock from '@/components/StateBlock.vue'

const s = ref(null)
const loading = ref(true)
const error = ref('')
async function load() { loading.value = true; error.value = ''; try { s.value = await api.get('/admin/stats') } catch (e) { error.value = e.message } finally { loading.value = false } }
onMounted(load)
const cards = computed(() => [
  { label: 'Users', value: s.value.users.total, sub: `+${s.value.users.new_7d} this week`, to: '/admin/users' },
  { label: 'Published listings', value: s.value.opportunities.published, sub: `${s.value.opportunities.total} total`, to: '/admin/opportunities' },
  { label: 'Open corrections', value: s.value.open_corrections, to: '/admin/corrections' },
  { label: 'New feedback', value: s.value.new_feedback, to: '/admin/feedback' },
  { label: 'Applications tracked', value: s.value.applications.total, to: '/admin' },
  { label: 'Saved', value: s.value.saved, to: '/admin' },
  { label: 'Documents stored', value: s.value.documents, to: '/admin' },
  { label: 'AI questions', value: s.value.ai_messages, to: '/admin' },
])
</script>
