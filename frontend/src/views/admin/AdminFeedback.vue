<template>
  <div style="max-width: 900px">
    <h1 class="page-title">Feedback</h1>
    <p class="page-sub mb-4">Messages from the contact form and in-app feedback.</p>
    <p v-if="!items.length" class="text-muted">No feedback yet.</p>
    <div class="d-grid gap-3">
      <div v-for="f in items" :key="f.id" class="fs-card fs-card-pad">
        <div class="d-flex gap-2 align-items-center flex-wrap mb-1"><span class="fs-chip">{{ f.kind }}</span><span class="fs-chip">{{ f.status }}</span><span v-if="f.contact_email" class="small text-muted">{{ f.contact_email }}</span><span class="small text-muted ms-auto">{{ timeAgo(f.created_at) }}</span></div>
        <p class="mb-2 prewrap">{{ f.message }}</p>
        <div class="d-flex gap-1"><button v-for="s in ['read', 'closed']" :key="s" class="btn btn-ghost btn-sm" :disabled="f.status === s" @click="setStatus(f, s)">Mark {{ s }}</button></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import api from '@/api'
import { useUi } from '@/stores/ui'
import { timeAgo } from '@/utils/format'

const ui = useUi()
const items = ref([])
async function load() { try { items.value = (await api.get('/admin/feedback')).items } catch (e) { ui.error(e) } }
onMounted(load)
async function setStatus(f, status) { try { await api.patch(`/admin/feedback/${f.id}`, { status }); f.status = status } catch (e) { ui.error(e) } }
</script>
