<template>
  <div>
    <h1 class="page-title mb-1">Compare opportunities</h1>
    <p class="page-sub mb-4">Side by side, up to three. Select them with “Compare” on the Discover page.</p>
    <StateBlock v-if="loading" kind="loading" :count="3" col-class="col-md-4" />
    <StateBlock v-else-if="error" kind="error" :message="error" @retry="load" />
    <StateBlock v-else-if="!items.length" title="Nothing to compare" message="Pick two or three opportunities on the Discover page."><router-link to="/app/discover" class="btn btn-soft">Go to Discover</router-link></StateBlock>
    <div v-else class="table-responsive fs-card">
      <table class="table mb-0" style="min-width: 640px">
        <thead><tr><th style="width: 160px"></th><th v-for="o in items" :key="o.id"><router-link :to="`/app/opportunities/${o.slug}`" class="fw-bold">{{ o.title }}</router-link><div class="small text-muted fw-normal">{{ o.organization.name }}</div></th></tr></thead>
        <tbody>
          <tr v-for="row in rows" :key="row.label"><th class="small text-muted fw-semibold">{{ row.label }}</th><td v-for="o in items" :key="o.id" class="small">{{ row.value(o) }}</td></tr>
          <tr><th class="small text-muted fw-semibold">Documents</th><td v-for="o in items" :key="o.id" class="small"><ul class="ps-3 mb-0"><li v-for="d in o.required_documents" :key="d.document_type.id">{{ d.document_type.name }}</li></ul></td></tr>
          <tr><th></th><td v-for="o in items" :key="o.id"><router-link :to="`/app/eligibility/${o.id}`" class="btn btn-soft btn-sm">Check eligibility</router-link></td></tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import api from '@/api'
import { benefitAmount, deadlineInfo, label } from '@/utils/format'
import StateBlock from '@/components/StateBlock.vue'

const route = useRoute()
const items = ref([])
const loading = ref(true)
const error = ref('')
const rows = [
  { label: 'Category', value: (o) => o.category.name },
  { label: 'Data', value: (o) => (o.data_origin === 'demo' ? 'Demo' : label('verification', o.verification_status)) },
  { label: 'Deadline', value: (o) => deadlineInfo(o).text },
  { label: 'Benefit', value: (o) => benefitAmount(o) || o.benefits },
  { label: 'Eligibility', value: (o) => o.eligibility_summary },
  { label: 'Rules', value: (o) => `${o.criteria.length} (${o.criteria.filter((c) => c.criterion_type === 'custom').length} need manual review)` },
  { label: 'Mode', value: (o) => o.application_mode },
]
async function load() {
  loading.value = true; error.value = ''
  try { items.value = route.query.ids ? (await api.get('/opportunities/compare', { ids: route.query.ids })).items : [] } catch (e) { error.value = e.message } finally { loading.value = false }
}
onMounted(load)
</script>
