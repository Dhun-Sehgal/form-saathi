<template>
  <div style="max-width: 900px">
    <div class="d-flex flex-wrap align-items-end gap-2 mb-4">
      <div class="me-auto"><h1 class="page-title">Categories</h1><p class="page-sub">Shown on the home page and in filters.</p></div>
      <button class="btn btn-primary" @click="edit(null)"><Plus :size="17" /> Add category</button>
    </div>
    <div class="fs-card">
      <div v-for="c in items" :key="c.id" class="d-flex align-items-center gap-3 p-3 border-bottom border-soft flex-wrap">
        <CategoryIcon :name="c.icon" :color="c.color" small />
        <div class="flex-grow-1"><div class="fw-semibold">{{ c.name }} <span v-if="!c.is_active" class="fs-chip">Inactive</span></div><div class="small text-muted">{{ c.slug }} · {{ c.count }} listing(s)</div></div>
        <button class="btn btn-ghost btn-sm" @click="edit(c)">Edit</button>
        <button class="btn btn-ghost btn-sm" :disabled="c.count > 0" :title="c.count ? 'Has listings — deactivate instead' : ''" @click="remove(c)"><Trash2 :size="15" /></button>
      </div>
    </div>
    <AppModal :open="!!form" :title="form?.id ? 'Edit category' : 'New category'" @close="form = null">
      <div v-if="form" class="d-grid gap-3">
        <div><label class="form-label" for="cn">Name</label><input id="cn" v-model="form.name" class="form-control" /></div>
        <div><label class="form-label" for="cs">Slug</label><input id="cs" v-model="form.slug" class="form-control" placeholder="lowercase-with-dashes" /></div>
        <div><label class="form-label" for="cd">Description</label><input id="cd" v-model="form.description" class="form-control" /></div>
        <div class="row g-2">
          <div class="col-6"><label class="form-label" for="ci">Icon</label><select id="ci" v-model="form.icon" class="form-select"><option v-for="i in ICONS" :key="i" :value="i">{{ i }}</option></select></div>
          <div class="col-6"><label class="form-label" for="cc">Colour</label><select id="cc" v-model="form.color" class="form-select"><option v-for="c in COLORS" :key="c" :value="c">{{ c }}</option></select></div>
        </div>
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
import { useMeta } from '@/stores/meta'
import { useUi } from '@/stores/ui'
import AppModal from '@/components/AppModal.vue'
import CategoryIcon from '@/components/CategoryIcon.vue'

const ICONS = ['graduation-cap', 'briefcase', 'award', 'landmark', 'file-pen-line', 'building-2', 'wrench', 'hand-coins', 'sparkles']
const COLORS = ['lavender', 'sky', 'lilac', 'mint', 'peach', 'butter', 'sand']
const ui = useUi()
const meta = useMeta()
const items = ref([])
const form = ref(null)
async function load() { try { items.value = (await api.get('/admin/categories')).items } catch (e) { ui.error(e) } }
onMounted(load)
function edit(c) { form.value = c ? { ...c } : { name: '', slug: '', description: '', icon: 'sparkles', color: 'lavender', sort_order: items.value.length, is_active: true } }
async function save() {
  const { id, count, ...body } = form.value // eslint-disable-line no-unused-vars
  try { if (id) await api.put(`/admin/categories/${id}`, body); else await api.post('/admin/categories', body); form.value = null; meta.loaded = false; meta.load(); ui.toast('Saved.'); load() } catch (e) { ui.toast(Object.values(e.fields || {})[0] || e.message, 'error') }
}
async function remove(c) { if (await ui.confirm({ title: `Delete “${c.name}”?`, confirmText: 'Delete', danger: true, message: 'This cannot be undone.' })) { try { await api.delete(`/admin/categories/${c.id}`); load() } catch (e) { ui.error(e) } } }
</script>
