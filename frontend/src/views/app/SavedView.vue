<template>
  <div>
    <div class="d-flex flex-wrap align-items-end gap-2 mb-4">
      <div class="me-auto"><h1 class="page-title">Saved</h1><p class="page-sub">Organise bookmarks into collections. We remind you before their deadlines.</p></div>
      <button class="btn btn-soft" @click="openNew"><FolderPlus :size="17" /> New collection</button>
    </div>

    <div class="d-flex flex-wrap gap-2 mb-4">
      <button class="choice-chip" :class="{ active: active === null }" @click="select(null)">All</button>
      <span v-for="c in collections" :key="c.id" class="d-inline-flex align-items-center">
        <button class="choice-chip" :class="{ active: active === c.id }" @click="select(c.id)"><Folder :size="15" /> {{ c.name }} <span class="text-muted">{{ c.count }}</span></button>
        <button v-if="active === c.id" class="btn btn-ghost btn-sm ms-1" :aria-label="`Delete collection ${c.name}`" @click="removeCollection(c)"><Trash2 :size="15" /></button>
      </span>
    </div>

    <StateBlock v-if="loading" kind="loading" />
    <StateBlock v-else-if="error" kind="error" :message="error" @retry="load" />
    <StateBlock v-else-if="!items.length" title="No saved opportunities" message="Tap the bookmark on any opportunity to save it here."><router-link to="/app/discover" class="btn btn-soft">Discover opportunities</router-link></StateBlock>
    <div v-else class="row g-3">
      <div v-for="o in items" :key="o.id" class="col-md-6 col-xl-4">
        <div class="d-grid gap-2 h-100">
          <OpportunityCard :o="o" @saved-change="load" />
          <select v-if="collections.length" class="form-select form-select-sm" :value="o.collection_id || ''" aria-label="Move to collection" @change="move(o, $event.target.value)">
            <option value="">No collection</option><option v-for="c in collections" :key="c.id" :value="c.id">{{ c.name }}</option>
          </select>
        </div>
      </div>
    </div>

    <AppModal :open="newOpen" title="New collection" @close="newOpen = false">
      <label class="form-label" for="cname">Name</label>
      <input id="cname" v-model="newName" class="form-control" maxlength="60" placeholder="e.g. Final year, Summer 2027" @keydown.enter="create" />
      <template #footer><button class="btn btn-ghost" @click="newOpen = false">Cancel</button><button class="btn btn-primary" :disabled="!newName.trim()" @click="create">Create</button></template>
    </AppModal>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { Folder, FolderPlus, Trash2 } from 'lucide-vue-next'
import api from '@/api'
import { useUi } from '@/stores/ui'
import AppModal from '@/components/AppModal.vue'
import OpportunityCard from '@/components/OpportunityCard.vue'
import StateBlock from '@/components/StateBlock.vue'

const ui = useUi()
const items = ref([])
const collections = ref([])
const active = ref(null)
const loading = ref(true)
const error = ref('')
const newOpen = ref(false)
const newName = ref('')

async function load() {
  loading.value = true; error.value = ''
  try {
    const [s, c] = await Promise.all([api.get('/saved', active.value ? { collection_id: active.value } : {}), api.get('/collections')])
    items.value = s.items; collections.value = c.items
  } catch (e) { error.value = e.message } finally { loading.value = false }
}
onMounted(load)
function select(id) { active.value = id; load() }
function openNew() { newName.value = ''; newOpen.value = true }
async function create() {
  try { await api.post('/collections', { name: newName.value.trim() }); newOpen.value = false; ui.toast('Collection created.'); load() } catch (e) { ui.error(e) }
}
async function move(o, cid) {
  try { await api.post('/saved', { opportunity_id: o.id, collection_id: cid ? Number(cid) : null }); ui.toast('Moved.'); load() } catch (e) { ui.error(e) }
}
async function removeCollection(c) {
  if (!(await ui.confirm({ title: `Delete “${c.name}”?`, message: 'The opportunities stay saved; only the collection is removed.', confirmText: 'Delete', danger: true }))) return
  try { await api.delete(`/collections/${c.id}`); active.value = null; load() } catch (e) { ui.error(e) }
}
</script>
