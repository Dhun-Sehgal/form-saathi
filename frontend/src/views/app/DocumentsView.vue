<template>
  <div>
    <div class="d-flex flex-wrap align-items-end gap-2 mb-3">
      <div class="me-auto"><h1 class="page-title">Documents</h1><p class="page-sub">Your private vault. Files are never public — only you can open them.</p></div>
      <button class="btn btn-primary" @click="openUpload()"><Upload :size="17" /> Upload document</button>
    </div>
    <div class="alert d-flex gap-2 small mb-4" style="background: var(--fs-primary-50); color: var(--fs-text)"><ShieldCheck :size="18" class="flex-shrink-0" style="color: var(--fs-primary)" /> Tip: upload only what applications need. For Aadhaar, use a masked copy where the form allows it. PDF, JPG, PNG or WebP up to {{ maxMb }} MB.</div>

    <div class="row g-4">
      <div class="col-lg-7">
        <StateBlock v-if="loading" kind="loading" :count="2" col-class="col-12" />
        <StateBlock v-else-if="error" kind="error" :message="error" @retry="load" />
        <StateBlock v-else-if="!docs.length" title="Your vault is empty" message="Upload documents once and reuse them for every application."><button class="btn btn-soft" @click="openUpload()">Upload your first document</button></StateBlock>
        <div v-else class="d-grid gap-3">
          <section v-for="g in grouped" :key="g.type.id" class="fs-card fs-card-pad">
            <h2 class="h6 fw-bold mb-2 d-flex align-items-center gap-2">{{ g.type.name }} <span v-if="g.type.sensitivity === 'high'" class="fs-badge fs-badge-pending" title="Sensitive document"><Lock /> Sensitive</span></h2>
            <div v-for="d in g.docs" :key="d.id" class="d-flex gap-3 align-items-center py-2 border-top border-soft flex-wrap">
              <span class="icon-tile icon-tile-sm" :class="d.mime_type === 'application/pdf' ? 'tint-peach' : 'tint-sky'"><FileText v-if="d.mime_type === 'application/pdf'" /><ImageIcon v-else /></span>
              <div class="min-w-0 flex-grow-1">
                <div class="small fw-semibold text-truncate">{{ d.label || d.original_filename }}</div>
                <div class="small text-muted">{{ bytes(d.size_bytes) }} · uploaded {{ formatDate(d.created_at) }}<span v-if="d.expires_on"> · <span :class="d.status === 'expired' ? 'text-danger fw-semibold' : ''">{{ d.status === 'expired' ? 'expired' : 'valid until' }} {{ formatDate(d.expires_on) }}</span></span></div>
              </div>
              <div class="d-flex gap-1">
                <button class="btn btn-soft btn-sm" @click="view(d)"><Eye :size="15" /> View</button>
                <button class="btn btn-ghost btn-sm" aria-label="Delete document" @click="remove(d)"><Trash2 :size="15" /></button>
              </div>
            </div>
          </section>
        </div>
      </div>

      <div class="col-lg-5">
        <section class="fs-card fs-card-pad">
          <h2 class="h6 fw-bold mb-1">Checklist by application</h2>
          <p class="small text-muted">Pick a tracked application to see what’s missing.</p>
          <select v-model="selectedApp" class="form-select mb-3" aria-label="Choose application" @change="loadChecklist">
            <option value="">Choose…</option>
            <option v-for="a in apps" :key="a.id" :value="a.opportunity.id">{{ a.opportunity.title }}</option>
          </select>
          <p v-if="!apps.length" class="small text-muted mb-0">Track an application first to get its checklist.</p>
          <div v-if="checklist">
            <div class="d-flex justify-content-between small mb-1"><span>{{ checklist.ready }} of {{ checklist.total }} ready</span><button class="btn btn-link btn-sm p-0" style="min-height:auto" @click="download"><Download :size="14" /> Download</button></div>
            <div class="progress mb-3"><div class="progress-bar" :style="{ width: (checklist.ready / Math.max(1, checklist.total)) * 100 + '%', background: 'var(--fs-success)' }" /></div>
            <div v-for="i in checklist.items" :key="i.document_type.id" class="d-flex gap-2 py-2 border-top border-soft align-items-center">
              <CircleCheck v-if="i.status === 'ready'" :size="18" style="color: var(--fs-success)" /><CircleDashed v-else :size="18" class="text-muted" />
              <div class="flex-grow-1 small"><div class="fw-semibold">{{ i.document_type.name }}</div><div v-if="i.status !== 'ready'" class="text-muted">{{ { missing: 'Missing', expired: 'Expired', expiring: 'Expires before deadline' }[i.status] }}</div></div>
              <button v-if="i.status !== 'ready'" class="btn btn-soft btn-sm" @click="openUpload(i.document_type.id)">Upload</button>
            </div>
          </div>
        </section>
      </div>
    </div>

    <AppModal :open="uploadOpen" title="Upload a document" subtitle="Stored privately in your vault." @close="uploadOpen = false">
      <form class="d-grid gap-3" @submit.prevent="upload">
        <div><label class="form-label" for="dt">Document type</label><select id="dt" v-model="up.document_type_id" class="form-select" required><option value="">Choose…</option><option v-for="t in meta.document_types" :key="t.id" :value="t.id">{{ t.name }}</option></select></div>
        <div><label class="form-label" for="file">File</label><input id="file" ref="fileInput" type="file" class="form-control" accept=".pdf,.jpg,.jpeg,.png,.webp,application/pdf,image/*" required @change="pick" /><div class="form-text">PDF, JPG, PNG or WebP · max {{ maxMb }} MB</div></div>
        <div><label class="form-label" for="lbl">Label <span class="text-muted fw-normal">(optional)</span></label><input id="lbl" v-model="up.label" class="form-control" maxlength="120" placeholder="e.g. Semester 5 marksheet" /></div>
        <div class="row g-2">
          <div class="col-6"><label class="form-label" for="iss">Issued on</label><input id="iss" v-model="up.issued_on" type="date" class="form-control" /></div>
          <div class="col-6"><label class="form-label" for="exp">Valid until</label><input id="exp" v-model="up.expires_on" type="date" class="form-control" /></div>
        </div>
        <div v-if="upError" class="alert alert-danger py-2 small mb-0">{{ upError }}</div>
        <button class="btn btn-primary" :disabled="busy || !up.document_type_id || !file">{{ busy ? 'Uploading…' : 'Upload' }}</button>
      </form>
    </AppModal>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { CircleCheck, CircleDashed, Download, Eye, FileText, Image as ImageIcon, Lock, ShieldCheck, Trash2, Upload } from 'lucide-vue-next'
import api, { IS_PREVIEW } from '@/api'
import { useMeta } from '@/stores/meta'
import { useUi } from '@/stores/ui'
import { bytes, downloadText, formatDate } from '@/utils/format'
import AppModal from '@/components/AppModal.vue'
import StateBlock from '@/components/StateBlock.vue'

const meta = useMeta()
const ui = useUi()
const maxMb = IS_PREVIEW ? 3 : 5
const docs = ref([])
const apps = ref([])
const loading = ref(true)
const error = ref('')
const selectedApp = ref('')
const checklist = ref(null)
const uploadOpen = ref(false)
const up = reactive({ document_type_id: '', label: '', issued_on: '', expires_on: '' })
const file = ref(null)
const fileInput = ref(null)
const busy = ref(false)
const upError = ref('')

const grouped = computed(() => {
  const m = new Map()
  for (const d of docs.value) { if (!m.has(d.document_type.id)) m.set(d.document_type.id, { type: d.document_type, docs: [] }); m.get(d.document_type.id).docs.push(d) }
  return [...m.values()]
})
async function load() {
  loading.value = true; error.value = ''
  try { const [d, a] = await Promise.all([api.get('/documents'), api.get('/applications')]); docs.value = d.items; apps.value = a.items } catch (e) { error.value = e.message } finally { loading.value = false }
  if (selectedApp.value) loadChecklist()
}
onMounted(() => { meta.load(); load() })
async function loadChecklist() {
  checklist.value = null
  if (!selectedApp.value) return
  try { checklist.value = await api.get(`/documents/checklist/${selectedApp.value}`) } catch (e) { ui.error(e) }
}
function openUpload(typeId = '') { Object.assign(up, { document_type_id: typeId, label: '', issued_on: '', expires_on: '' }); file.value = null; upError.value = ''; uploadOpen.value = true }
function pick(e) {
  const f = e.target.files[0]
  upError.value = ''
  if (f && f.size > maxMb * 1024 * 1024) { upError.value = `This file is ${bytes(f.size)}. The limit is ${maxMb} MB.`; file.value = null; return }
  file.value = f
}
async function upload() {
  busy.value = true; upError.value = ''
  try {
    const fd = new FormData()
    fd.append('file', file.value); fd.append('document_type_id', up.document_type_id)
    for (const k of ['label', 'issued_on', 'expires_on']) if (up[k]) fd.append(k, up[k])
    await api.upload('/documents', fd)
    uploadOpen.value = false; ui.toast('Document uploaded.'); load()
  } catch (e) { upError.value = e.message } finally { busy.value = false }
}
async function view(d) { try { await api.openDocument(d.id) } catch (e) { ui.error(e) } }
async function remove(d) {
  if (!(await ui.confirm({ title: 'Delete this document?', message: 'The file will be permanently removed from your vault.', confirmText: 'Delete', danger: true }))) return
  try { await api.delete(`/documents/${d.id}`); ui.toast('Document deleted.'); load() } catch (e) { ui.error(e) }
}
function download() {
  const c = checklist.value
  downloadText(`checklist-${c.opportunity.slug}.txt`, [`FormSaathi checklist — ${c.opportunity.title}`, `Deadline: ${c.opportunity.deadline ? formatDate(c.opportunity.deadline) : 'Rolling'}`, '', ...c.items.map((i) => `[${i.status === 'ready' ? 'x' : ' '}] ${i.document_type.name}${i.notes ? ' — ' + i.notes : ''}`)].join('\n'))
}
</script>
