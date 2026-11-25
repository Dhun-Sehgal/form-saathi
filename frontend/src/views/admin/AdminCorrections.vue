<template>
  <div style="max-width: 980px">
    <h1 class="page-title">Corrections</h1>
    <p class="page-sub mb-3">Reports from users. Check the official source, fix the listing if needed, then resolve the report — the reporter is notified.</p>
    <div class="d-flex gap-2 mb-3"><button v-for="s in ['open','accepted','rejected','']" :key="s" class="choice-chip" :class="{ active: status === s }" @click="status = s; load()">{{ s ? s[0].toUpperCase() + s.slice(1) : 'All' }}</button></div>
    <StateBlock v-if="loading" kind="loading" :count="2" col-class="col-12" />
    <StateBlock v-else-if="!items.length" title="No reports here" message="When users report a problem with a listing, it shows up here." />
    <div v-else class="d-grid gap-3">
      <div v-for="c in items" :key="c.id" class="fs-card fs-card-pad">
        <div class="d-flex flex-wrap gap-2 align-items-center mb-2"><router-link :to="`/admin/opportunities/${c.opportunity.id}`" class="fw-bold">{{ c.opportunity.title }}</router-link><span class="fs-chip">{{ c.field }}</span><span class="fs-chip">{{ c.status }}</span><span class="small text-muted ms-auto">{{ timeAgo(c.created_at) }}</span></div>
        <p class="mb-2 prewrap">{{ c.message }}</p>
        <a v-if="c.suggested_source_url" :href="c.suggested_source_url" target="_blank" rel="noopener noreferrer" class="small d-block mb-2 text-break">{{ c.suggested_source_url }}</a>
        <div v-if="c.status === 'open'" class="d-flex gap-2 flex-wrap">
          <input v-model="notes[c.id]" class="form-control form-control-sm flex-grow-1" style="min-width: 200px" placeholder="Note to the reporter (optional)" aria-label="Note" />
          <button class="btn btn-soft btn-sm" @click="resolve(c, 'accepted')">Accept</button>
          <button class="btn btn-ghost btn-sm" @click="resolve(c, 'rejected')">Reject</button>
        </div>
        <p v-else-if="c.admin_note" class="small text-muted mb-0">Note: {{ c.admin_note }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import api from '@/api'
import { useUi } from '@/stores/ui'
import { timeAgo } from '@/utils/format'
import StateBlock from '@/components/StateBlock.vue'

const ui = useUi()
const status = ref('open')
const items = ref([])
const loading = ref(true)
const notes = reactive({})
async function load() { loading.value = true; try { items.value = (await api.get('/admin/corrections', status.value ? { status: status.value } : {})).items } catch (e) { ui.error(e) } finally { loading.value = false } }
onMounted(load)
async function resolve(c, s) { try { await api.patch(`/admin/corrections/${c.id}`, { status: s, admin_note: notes[c.id] || null }); ui.toast('Report resolved and reporter notified.'); load() } catch (e) { ui.error(e) } }
</script>
