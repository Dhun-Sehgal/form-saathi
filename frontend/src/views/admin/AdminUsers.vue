<template>
  <div>
    <h1 class="page-title">Users</h1>
    <p class="page-sub mb-3">Manage roles and access. Admins can’t see users’ documents or chats from here.</p>
    <div class="fs-card p-3 mb-3 d-flex gap-2 flex-wrap">
      <input v-model="q" class="form-control" style="max-width: 280px" placeholder="Search by email" aria-label="Search" @keydown.enter="load(1)" />
      <select v-model="role" class="form-select" style="max-width: 160px" aria-label="Role" @change="load(1)"><option value="">All roles</option><option value="user">Users</option><option value="admin">Admins</option></select>
      <button class="btn btn-soft" @click="load(1)">Search</button>
    </div>
    <div class="fs-card table-responsive">
      <table class="table table-stack mb-0">
        <thead><tr class="small text-muted"><th>User</th><th>Role</th><th>Joined</th><th>Last login</th><th class="text-end">Actions</th></tr></thead>
        <tbody>
          <tr v-for="u in r.items" :key="u.id">
            <td data-label="User"><div class="fw-semibold">{{ u.full_name || '—' }}</div><div class="small text-muted">{{ u.email }}</div></td>
            <td data-label="Role"><span class="fs-chip">{{ u.role }}</span> <span v-if="!u.is_active" class="fs-badge fs-badge-danger">Deactivated</span></td>
            <td data-label="Joined" class="small">{{ formatDate(u.created_at) }}</td>
            <td data-label="Last login" class="small">{{ u.last_login_at ? timeAgo(u.last_login_at) : 'Never' }}</td>
            <td data-label="Actions" class="text-end">
              <div class="d-inline-flex gap-1">
                <button class="btn btn-ghost btn-sm" @click="patch(u, { role: u.role === 'admin' ? 'user' : 'admin' })">{{ u.role === 'admin' ? 'Make user' : 'Make admin' }}</button>
                <button class="btn btn-ghost btn-sm" @click="patch(u, { is_active: !u.is_active })">{{ u.is_active ? 'Deactivate' : 'Activate' }}</button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <nav v-if="r.pages > 1" class="d-flex justify-content-center gap-2 mt-3"><button class="btn btn-soft btn-sm" :disabled="r.page <= 1" @click="load(r.page - 1)">Prev</button><button class="btn btn-soft btn-sm" :disabled="r.page >= r.pages" @click="load(r.page + 1)">Next</button></nav>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import api from '@/api'
import { useUi } from '@/stores/ui'
import { formatDate, timeAgo } from '@/utils/format'

const ui = useUi()
const q = ref('')
const role = ref('')
const r = ref({ items: [], page: 1, pages: 1 })
async function load(page = 1) { try { r.value = await api.get('/admin/users', { q: q.value || undefined, role: role.value || undefined, page }) } catch (e) { ui.error(e) } }
onMounted(load)
async function patch(u, body) {
  if (!(await ui.confirm({ title: 'Change this account?', message: `${u.email}: ${JSON.stringify(body).replace(/[{}"]/g, '').replace(':', ' → ')}`, confirmText: 'Confirm' }))) return
  try { await api.patch(`/admin/users/${u.id}`, body); ui.toast('User updated.'); load(r.value.page) } catch (e) { ui.error(e) }
}
</script>
