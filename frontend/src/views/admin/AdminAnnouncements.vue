<template>
  <div style="max-width: 900px">
    <div class="d-flex flex-wrap align-items-end gap-2 mb-4">
      <div class="me-auto"><h1 class="page-title">Announcements</h1><p class="page-sub">Banners shown on users’ dashboards.</p></div>
      <button class="btn btn-primary" @click="edit(null)"><Plus :size="17" /> New announcement</button>
    </div>
    <p v-if="!items.length" class="text-muted">No announcements yet.</p>
    <div class="d-grid gap-3">
      <div v-for="a in items" :key="a.id" class="fs-card fs-card-pad">
        <div class="d-flex gap-2 align-items-center flex-wrap mb-1"><span class="fw-bold">{{ a.title }}</span><span class="fs-chip">{{ a.audience }}</span><span class="fs-chip">{{ a.level }}</span><span v-if="!a.is_active" class="fs-chip">Inactive</span>
          <div class="ms-auto d-flex gap-1"><button class="btn btn-ghost btn-sm" @click="edit(a)">Edit</button><button class="btn btn-ghost btn-sm" aria-label="Delete" @click="remove(a)"><Trash2 :size="15" /></button></div></div>
        <p class="small text-muted mb-0">{{ a.body }}</p>
      </div>
    </div>
    <AppModal :open="!!form" :title="form?.id ? 'Edit announcement' : 'New announcement'" @close="form = null">
      <div v-if="form" class="d-grid gap-3">
        <div><label class="form-label" for="at">Title</label><input id="at" v-model="form.title" class="form-control" /></div>
        <div><label class="form-label" for="ab">Message</label><textarea id="ab" v-model="form.body" rows="3" class="form-control" /></div>
        <div class="row g-2"><div class="col-6"><label class="form-label" for="aa">Audience</label><select id="aa" v-model="form.audience" class="form-select"><option value="all">Everyone</option><option value="users">Users</option><option value="admins">Admins</option></select></div><div class="col-6"><label class="form-label" for="al">Level</label><select id="al" v-model="form.level" class="form-select"><option value="info">Info</option><option value="important">Important</option></select></div></div>
        <label class="form-check"><input v-model="form.is_active" type="checkbox" class="form-check-input" /> Active</label>
      </div>
      <template #footer><button class="btn btn-ghost" @click="form = null">Cancel</button><button class="btn btn-primary" @click="save">Save</button></template>
    </AppModal>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { Plus, Trash2 } from 'lucide-vue-next'
import api from '@/api'
import { useUi } from '@/stores/ui'
import AppModal from '@/components/AppModal.vue'

const ui = useUi()
const items = ref([])
const form = ref(null)
async function load() { try { items.value = (await api.get('/admin/announcements')).items } catch (e) { ui.error(e) } }
onMounted(load)
function edit(a) { form.value = a ? { ...a } : { title: '', body: '', audience: 'all', level: 'info', is_active: true } }
async function save() {
  const { id, title, body, audience, level, is_active } = form.value
  try { if (id) await api.put(`/admin/announcements/${id}`, { title, body, audience, level, is_active }); else await api.post('/admin/announcements', { title, body, audience, level, is_active }); form.value = null; ui.toast('Saved.'); load() } catch (e) { ui.toast(Object.values(e.fields || {})[0] || e.message, 'error') }
}
async function remove(a) { if (await ui.confirm({ title: 'Delete announcement?', message: a.title, confirmText: 'Delete', danger: true })) { try { await api.delete(`/admin/announcements/${a.id}`); load() } catch (e) { ui.error(e) } } }
</script>
