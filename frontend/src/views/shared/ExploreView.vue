<template>
  <div :class="inApp ? '' : 'container py-4 py-lg-5'">
    <div class="d-flex flex-wrap align-items-end gap-2 mb-3">
      <div class="me-auto">
        <h1 class="page-title">{{ inApp ? 'Discover opportunities' : 'Explore opportunities' }}</h1>
        <p class="page-sub">{{ result.total }} {{ result.total === 1 ? 'opportunity' : 'opportunities' }} {{ filters.status === 'open' ? 'open now' : '' }}</p>
      </div>
      <router-link v-if="compareIds.length" :to="{ path: '/app/compare', query: { ids: compareIds.join(',') } }" class="btn btn-soft"><Columns3 :size="16" /> Compare ({{ compareIds.length }})</router-link>
    </div>

    <form class="smart-search mb-3" role="search" @submit.prevent="apply()">
      <Search :size="20" class="text-muted flex-shrink-0" />
      <input v-model="filters.q" type="search" placeholder="Search by title, keyword or organisation" aria-label="Search" />
      <button type="button" class="btn btn-ghost d-lg-none" @click="sheet = true"><SlidersHorizontal :size="18" /> {{ t('common.filters') }}<span v-if="activeCount" class="badge rounded-pill text-bg-primary">{{ activeCount }}</span></button>
      <button class="btn btn-primary" type="submit">{{ t('common.search') }}</button>
    </form>

    <div v-if="inApp && meta.loaded && profileHint" class="d-flex flex-wrap gap-2 mb-3">
      <button class="fs-chip border-0" @click="matchMe"><Sparkles :size="14" /> Match my profile</button>
    </div>

    <div class="row g-4">
      <aside class="col-lg-3 d-none d-lg-block">
        <div class="fs-card fs-card-pad filter-panel"><FilterFields v-model="filters" :in-app="inApp" @change="apply()" @clear="clearAll" /></div>
      </aside>

      <div class="col-lg-9">
        <div class="d-flex flex-wrap align-items-center gap-2 mb-3">
          <div class="d-flex gap-1 flex-wrap">
            <button v-for="s in statusTabs" :key="s.value" class="choice-chip" :class="{ active: filters.status === s.value }" @click="filters.status = s.value; apply()">{{ s.label }}</button>
          </div>
          <div class="ms-auto d-flex align-items-center gap-2">
            <label for="sort" class="small text-muted text-nowrap">Sort by</label>
            <select id="sort" v-model="filters.sort" class="form-select form-select-sm" style="width:auto" @change="apply()">
              <option value="relevance">Relevance</option><option value="deadline">Deadline (soonest)</option><option value="recent">Recently added</option>
            </select>
          </div>
        </div>

        <StateBlock v-if="loading" kind="loading" :count="4" col-class="col-md-6" />
        <StateBlock v-else-if="error" kind="error" :message="error" @retry="load" />
        <StateBlock v-else-if="!result.items.length" title="No matches" message="Try removing a filter or searching for a broader keyword.">
          <button class="btn btn-soft" @click="clearAll">{{ t('common.clear') }}</button>
        </StateBlock>
        <template v-else>
          <div class="row g-3">
            <div v-for="o in result.items" :key="o.id" class="col-md-6">
              <div class="position-relative h-100">
                <OpportunityCard :o="o" />
                <label v-if="inApp" class="position-absolute small d-flex align-items-center gap-1 bg-surface px-2 rounded-pill border border-soft" style="top:-10px; right:14px; font-size:.72rem">
                  <input type="checkbox" :checked="compareIds.includes(o.id)" :disabled="!compareIds.includes(o.id) && compareIds.length >= 3" @change="toggleCompare(o.id)" /> Compare
                </label>
              </div>
            </div>
          </div>
          <nav v-if="result.pages > 1" class="d-flex justify-content-center align-items-center gap-2 mt-4" aria-label="Pagination">
            <button class="btn btn-soft btn-sm" :disabled="result.page <= 1" @click="go(result.page - 1)"><ChevronLeft :size="16" /> Prev</button>
            <span class="small text-muted">Page {{ result.page }} of {{ result.pages }}</span>
            <button class="btn btn-soft btn-sm" :disabled="result.page >= result.pages" @click="go(result.page + 1)">Next <ChevronRight :size="16" /></button>
          </nav>
        </template>
      </div>
    </div>

    <AppModal :open="sheet" :title="t('common.filters')" @close="sheet = false">
      <FilterFields v-model="filters" :in-app="inApp" @change="() => {}" @clear="clearAll" />
      <template #footer><button class="btn btn-primary w-100" @click="sheet = false; apply()">Show results</button></template>
    </AppModal>
  </div>
</template>

<script setup>
import { computed, h, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { ChevronLeft, ChevronRight, Columns3, Search, SlidersHorizontal, Sparkles } from 'lucide-vue-next'
import api from '@/api'
import { useAuth } from '@/stores/auth'
import { useMeta } from '@/stores/meta'
import { LABELS } from '@/utils/format'
import AppModal from '@/components/AppModal.vue'
import OpportunityCard from '@/components/OpportunityCard.vue'
import StateBlock from '@/components/StateBlock.vue'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()
const auth = useAuth()
const meta = useMeta()
const inApp = computed(() => route.path.startsWith('/app'))
const KEYS = ['q', 'category', 'education', 'state', 'income', 'deadline_within', 'status', 'sort', 'mine', 'origin']
const blank = () => ({ q: '', category: '', education: '', state: '', income: '', deadline_within: '', status: 'open', sort: 'relevance', mine: '', origin: '' })
const filters = reactive({ ...blank(), ...Object.fromEntries(KEYS.filter((k) => route.query[k]).map((k) => [k, route.query[k]])) })
const result = ref({ items: [], total: 0, page: 1, pages: 1 })
const loading = ref(true)
const error = ref('')
const sheet = ref(false)
const compareIds = ref([])
const statusTabs = [{ value: 'open', label: 'Open' }, { value: 'closing_soon', label: 'Closing soon' }, { value: 'all', label: 'All' }, { value: 'closed', label: 'Closed' }]
const activeCount = computed(() => ['category', 'education', 'state', 'income', 'deadline_within', 'mine'].filter((k) => filters[k]).length)
const profileHint = computed(() => auth.profile.education_level || auth.profile.state_code)

function query() { return Object.fromEntries(KEYS.filter((k) => filters[k] && !(k === 'sort' && filters[k] === 'relevance')).map((k) => [k, filters[k]])) }
async function load(page = Number(route.query.page) || 1) {
  loading.value = true; error.value = ''
  try { result.value = await api.get('/opportunities', { ...query(), page, per_page: 12 }) } catch (e) { error.value = e.message } finally { loading.value = false }
}
function apply() { router.replace({ query: query() }); load(1) }
function go(p) { router.replace({ query: { ...query(), page: p } }); load(p); window.scrollTo({ top: 0, behavior: 'smooth' }) }
function clearAll() { Object.assign(filters, blank()); apply() }
function matchMe() {
  Object.assign(filters, { education: auth.profile.education_level || '', state: auth.profile.state_code || '', income: auth.profile.income_range && auth.profile.income_range !== 'prefer_not_say' ? auth.profile.income_range : '' })
  apply()
}
function toggleCompare(id) { compareIds.value = compareIds.value.includes(id) ? compareIds.value.filter((x) => x !== id) : [...compareIds.value, id] }
onMounted(() => load())

// Filter fields are shared by the sidebar and the mobile bottom sheet.
const FilterFields = {
  props: ['modelValue', 'inApp'],
  emits: ['change', 'clear'],
  setup(props, { emit }) {
    const f = props.modelValue
    const sel = (id, labelText, key, options) => h('div', { class: 'mb-3' }, [
      h('label', { class: 'form-label', for: id }, labelText),
      h('select', { id, class: 'form-select', value: f[key], onChange: (e) => { f[key] = e.target.value; emit('change') } },
        [h('option', { value: '' }, 'Any'), ...options.map(([v, l]) => h('option', { value: v, selected: f[key] === v }, l))]),
    ])
    return () => h('div', [
      h('div', { class: 'd-flex justify-content-between align-items-center mb-3' }, [h('span', { class: 'fw-bold' }, 'Filters'), h('button', { class: 'btn btn-link btn-sm p-0', style: 'min-height:auto', onClick: () => emit('clear') }, 'Clear all')]),
      sel('f-cat', 'Category', 'category', meta.categories.map((c) => [c.slug, c.name])),
      sel('f-edu', 'Education', 'education', Object.entries(LABELS.education)),
      sel('f-state', 'State', 'state', meta.states.map((s) => [s.code, s.name])),
      sel('f-inc', 'Family income', 'income', Object.entries(LABELS.income).filter(([k]) => k !== 'prefer_not_say')),
      sel('f-dl', 'Deadline', 'deadline_within', [['7', 'Within 7 days'], ['30', 'Within 30 days'], ['90', 'Within 90 days']]),
      props.inApp ? sel('f-mine', 'My status', 'mine', [['saved', 'Saved'], ['tracked', 'In my tracker'], ['not_tracked', 'Not tracked yet']]) : null,
    ])
  },
}
</script>
