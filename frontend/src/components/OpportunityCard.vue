<template>
  <article class="fs-card fs-card-hover fs-card-pad opp-card" :style="{ '--accent': `var(--accent-${o.category.color || 'lavender'})` }">
    <div class="d-flex align-items-start gap-3 mb-3">
      <CategoryIcon :name="o.category.icon" :color="o.category.color" small />
      <div class="min-w-0 flex-grow-1">
        <div class="small text-muted text-truncate">{{ o.organization.name }}</div>
        <div class="d-flex flex-wrap gap-1 mt-1">
          <span class="fs-chip">{{ o.category.name }}</span>
          <DataBadge :o="o" />
        </div>
      </div>
      <button v-if="showSave" class="btn btn-ghost btn-icon flex-shrink-0" :aria-pressed="o.saved"
              :aria-label="o.saved ? 'Remove from saved' : 'Save opportunity'" :disabled="busy" @click="toggleSave">
        <BookmarkCheck v-if="o.saved" :size="20" style="color: var(--fs-primary)" />
        <Bookmark v-else :size="20" />
      </button>
    </div>

    <router-link :to="detailLink" class="opp-title text-decoration-none d-block mb-1">{{ o.title }}</router-link>
    <p class="text-muted small mb-3 line-clamp-2">{{ o.summary }}</p>

    <div class="small mb-2 d-flex gap-2"><Users :size="16" class="text-muted flex-shrink-0 mt-1" /><span class="line-clamp-2">{{ o.eligibility_summary }}</span></div>
    <div class="small mb-3 d-flex gap-2"><Gift :size="16" class="text-muted flex-shrink-0 mt-1" /><span class="line-clamp-2">{{ benefitAmount(o) || o.benefits }}</span></div>

    <div v-if="o.match?.reasons?.length" class="d-flex flex-wrap gap-1 mb-3">
      <span v-for="r in o.match.reasons" :key="r" class="fs-badge fs-badge-ai"><Sparkles /> {{ r }}</span>
    </div>

    <div class="mt-auto d-flex align-items-center justify-content-between gap-2 flex-wrap pt-2 border-top border-soft">
      <span class="deadline-pill" :class="dl.tone"><CalendarClock /> {{ dl.text }}</span>
      <div class="d-flex gap-1 align-items-center">
        <span v-if="o.application_status" class="fs-chip"><span class="status-dot" :style="{ background: STATUS_COLORS[o.application_status] }" /> {{ label('status', o.application_status) }}</span>
        <a :href="o.official_url || o.source_url" target="_blank" rel="noopener noreferrer" class="btn btn-ghost btn-sm" :title="o.data_origin === 'demo' ? 'Demo link (example.org)' : 'Official source'">
          <ExternalLink :size="15" /><span class="visually-hidden">Official link</span>
        </a>
      </div>
    </div>
  </article>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { Bookmark, BookmarkCheck, CalendarClock, ExternalLink, Gift, Sparkles, Users } from 'lucide-vue-next'
import api from '@/api'
import { useAuth } from '@/stores/auth'
import { useUi } from '@/stores/ui'
import { benefitAmount, deadlineInfo, label, STATUS_COLORS } from '@/utils/format'
import CategoryIcon from './CategoryIcon.vue'
import DataBadge from './DataBadge.vue'

const props = defineProps({ o: { type: Object, required: true }, showSave: { type: Boolean, default: true } })
const emit = defineEmits(['saved-change'])
const auth = useAuth()
const ui = useUi()
const router = useRouter()
const busy = ref(false)
const dl = computed(() => deadlineInfo(props.o))
const detailLink = computed(() => (auth.isLoggedIn ? `/app/opportunities/${props.o.slug}` : `/opportunities/${props.o.slug}`))

async function toggleSave() {
  if (!auth.isLoggedIn) return router.push({ name: 'login', query: { next: router.currentRoute.value.fullPath } })
  busy.value = true
  try {
    if (props.o.saved) await api.delete(`/saved/${props.o.id}`)
    else await api.post('/saved', { opportunity_id: props.o.id })
    props.o.saved = !props.o.saved
    ui.toast(props.o.saved ? 'Saved. We’ll remind you before the deadline.' : 'Removed from saved.')
    emit('saved-change', props.o)
  } catch (e) { ui.error(e) } finally { busy.value = false }
}
</script>
