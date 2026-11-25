<template>
  <div>
    <div class="d-flex flex-wrap align-items-end gap-2 mb-3">
      <div class="me-auto"><h1 class="page-title">Opportunities</h1><p class="page-sub">Add, verify, publish and archive listings. Official listings must be verified before publishing.</p></div>
      <router-link to="/admin/opportunities/new" class="btn btn-primary"><Plus :size="17" /> Add opportunity</router-link>
    </div>
    <div class="fs-card p-3 mb-3 d-flex flex-wrap gap-2">
      <input v-model="f.q" class="form-control" style="max-width: 260px" placeholder="Search title" aria-label="Search" @keydown.enter="load(1)" />
      <select v-model="f.verification_status" class="form-select" style="max-width: 200px" aria-label="Verification" @change="load(1)"><option value="">Any verification</option><option v-for="(n, k) in LABELS.verification" :key="k" :value="k">{{ n }}</option></select>
      <select v-model="f.publication_status" class="form-select" style="max-width: 180px" aria-label="Publication" @change="load(1)"><option value="">Any publication</option><option v-for="(n, k) in LABELS.publication" :key="k" :value="k">{{ n }}</option></select>
      <select v-model="f.data_origin" class="form-select" style="max-width: 160px" aria-label="Origin" @change="load(1)"><option value="">Official + demo</option><option value="official">Official</option><option value="demo">Demo</option></select>
      <button class="btn btn-soft" @click="load(1)"><Search :size="16" /> Filter</button>
    </div>
    <StateBlock v-if="loading" kind="loading" :count="3" col-class="col-12" />
    <StateBlock v-else-if="error" kind="error" :message="error" @retry="load()" />
    <StateBlock v-else-if="!r.items.length" title="No listings match" message="Change the filters or add a new opportunity." />
    <div v-else class="fs-card table-responsive">
      <table class="table table-stack mb-0">
        <thead><tr class="small text-muted"><th>Title</th><th>Status</th><th>Deadline</th><th>Featured</th><th class="text-end">Actions</th></tr></thead>
        <tbody>
          <tr v-for="o in r.items" :key="o.id">
            <td data-label="Title"><router-link :to="`/admin/opportunities/${o.id}`" class="fw-semibold">{{ o.title }}</router-link><div class="small text-muted">{{ o.organization.name }} · {{ o.category.name }}</div></td>
            <td data-label="Status"><div class="d-flex flex-wrap gap-1 justify-content-end justify-content-md-start"><DataBadge :o="o" /><span class="fs-chip">{{ label('publication', o.publication_status) }}</span></div></td>
            <td data-label="Deadline" class="small">{{ o.deadline ? formatDate(o.deadline) : 'Rolling' }}</td>
            <td data-label="Featured"><input type="checkbox" class="form-check-input" :checked="o.is_featured" :aria-label="'Feature ' + o.title" @change="toggleFeatured(o)" /></td>
            <td data-label="Actions" class="text-end">
              <div class="d-inline-flex gap-1 flex-wrap justify-content-end">
                <button v-if="o.data_origin === 'official' && o.verification_status !== 'verified'" class="btn btn-soft btn-sm" @click="act(o, 'verify')">Verify</button>
                <button v-if="o.publication_status !== 'published' && o.verification_status !== 'archived'" class="btn btn-soft btn-sm" @click="act(o, 'publish')">Publish</button>
                <button v-if="o.publication_status === 'published'" class="btn btn-ghost btn-sm" @click="act(o, 'unpublish')">Unpublish</button>
                <router-link :to="`/admin/opportunities/${o.id}`" class="btn btn-ghost btn-sm">Edit</router-link>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <nav v-if="r.pages > 1" class="d-flex justify-content-center gap-2 mt-3"><button class="btn btn-soft btn-sm" :disabled="r.page <= 1" @click="load(r.page - 1)">Prev</button><span class="small text-muted align-self-center">{{ r.page }} / {{ r.pages }}</span><button class="btn btn-soft btn-sm" :disabled="r.page >= r.pages" @click="load(r.page + 1)">Next</button></nav>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { useRoute } from 'vue-router'
import { Plus, Search } from 'lucide-vue-next'
import api from '@/api'
import { useUi } from '@/stores/ui'
import { formatDate, label, LABELS } from '@/utils/format'
import DataBadge from '@/components/DataBadge.vue'
import StateBlock from '@/components/StateBlock.vue'

const route = useRoute()
const ui = useUi()
const f = reactive({ q: '', verification_status: route.query.verification_status || '', publication_status: '', data_origin: '' })
const r = ref({ items: [], page: 1, pages: 1 })
const loading = ref(true)
const error = ref('')
async function load(page = 1) {
  loading.value = true; error.value = ''
  try { r.value = await api.get('/admin/opportunities', { ...Object.fromEntries(Object.entries(f).filter(([, v]) => v)), page }) } catch (e) { error.value = e.message } finally { loading.value = false }
}
onMounted(load)
async function act(o, action) {
  if (action === 'verify' && !(await ui.confirm({ title: 'Mark as verified?', message: `Confirm you have checked every detail of “${o.title}” against the official source: ${o.source_url}`, confirmText: 'I checked it — verify' }))) return
  try { await api.post(`/admin/opportunities/${o.id}/status`, { action }); ui.toast('Updated.'); load(r.value.page) } catch (e) { ui.error(e) }
}
async function toggleFeatured(o) {
  try {
    const all = (await api.get('/admin/opportunities', { per_page: 100 })).items
    let ids = all.filter((x) => x.is_featured).map((x) => x.id)
    ids = o.is_featured ? ids.filter((x) => x !== o.id) : [...ids, o.id]
    await api.put('/admin/featured', { ids: ids.slice(0, 12) })
    ui.toast(o.is_featured ? 'Removed from featured.' : 'Featured on the home page.'); load(r.value.page)
  } catch (e) { ui.error(e) }
}
</script>
