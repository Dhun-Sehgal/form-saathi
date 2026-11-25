<template>
  <StateBlock v-if="loading" kind="loading" :count="6" />
  <StateBlock v-else-if="error" kind="error" :message="error" @retry="load" />
  <div v-else>
    <section class="welcome-banner mb-4">
      <div class="d-flex align-items-center gap-4">
        <div class="flex-grow-1 min-w-0">
          <h1 class="page-title mb-1">{{ t('dash.welcome', { name: d.name || auth.firstName }) }} 👋</h1>
          <p class="page-sub mb-3">{{ t('dash.sub') }}</p>
          <div class="d-flex flex-wrap gap-2">
            <router-link to="/app/discover" class="btn btn-white btn-pill"><Compass :size="17" /> {{ t('nav.discover') }}</router-link>
            <router-link to="/app/tracker" class="btn btn-glass btn-pill"><KanbanSquare :size="17" /> {{ t('nav.tracker') }}</router-link>
          </div>
        </div>
        <div class="d-none d-md-block flex-shrink-0 bg-surface rounded-xl p-2 float" style="transform: rotate(-3deg); box-shadow: 0 24px 50px -28px rgba(27,23,64,.7)"><SpotArt name="student" style="width: 190px" /></div>
      </div>
    </section>

    <div v-for="a in d.announcements" :key="a.id" class="alert d-flex gap-2 mb-3" :class="a.level === 'important' ? 'alert-warning' : 'alert-info'"><Megaphone :size="18" class="flex-shrink-0 mt-1" /><div><strong>{{ a.title }}</strong> — {{ a.body }}</div></div>

    <!-- Stats -->
    <div class="row g-3 mb-4">
      <div v-for="s in stats" :key="s.label" class="col-6 col-lg-3">
        <router-link :to="s.to" class="fs-card fs-card-hover stat-card pastel d-flex gap-3 align-items-center text-decoration-none h-100" :class="s.tint">
          <span class="icon-tile icon-tile-sm"><component :is="s.icon" /></span>
          <div><div class="stat-value" style="color: var(--fs-text)">{{ s.value }}</div><div class="stat-label">{{ s.label }}</div></div>
        </router-link>
      </div>
    </div>

    <div class="row g-4">
      <div class="col-xl-8 d-grid gap-4 align-content-start">
        <!-- Profile completion -->
        <div v-if="d.profile_completion.percent < 100" class="fs-card fs-card-pad d-flex flex-wrap gap-4 align-items-center">
          <ProgressRing :value="d.profile_completion.percent" />
          <div class="flex-grow-1" style="min-width: 220px">
            <h2 class="h6 fw-bold mb-1">{{ t('dash.completion') }}</h2>
            <p class="small text-muted mb-2">A complete profile gives more accurate eligibility checks. Still missing: {{ d.profile_completion.missing.slice(0, 4).join(', ') }}<span v-if="d.profile_completion.missing.length > 4">…</span></p>
            <router-link to="/app/profile" class="btn btn-soft btn-sm">Complete profile</router-link>
          </div>
        </div>

        <!-- Recommended -->
        <section>
          <div class="d-flex justify-content-between align-items-center mb-3"><h2 class="h5 fw-bold mb-0">{{ t('dash.recommended') }}</h2><router-link to="/app/discover" class="small">{{ t('common.viewAll') }}</router-link></div>
          <div v-if="d.recommended.length" class="row g-3"><div v-for="o in d.recommended" :key="o.id" class="col-md-6"><OpportunityCard :o="o" /></div></div>
          <div v-else class="fs-card"><StateBlock title="No matches yet" message="Complete your profile or browse all opportunities — we only recommend ones you might be eligible for."><router-link to="/app/discover" class="btn btn-soft">Browse opportunities</router-link></StateBlock></div>
        </section>

        <!-- Application progress -->
        <section class="fs-card fs-card-pad">
          <div class="d-flex justify-content-between align-items-center mb-3"><h2 class="h6 fw-bold mb-0">{{ t('dash.progress') }}</h2><router-link to="/app/tracker" class="small">Open tracker</router-link></div>
          <div v-if="d.stats.tracked" class="d-grid gap-2">
            <div v-for="s in progressRows" :key="s.key" class="d-flex align-items-center gap-3 small">
              <span class="text-nowrap" style="width: 150px">{{ s.label }}</span>
              <div class="progress flex-grow-1" :aria-label="`${s.label}: ${s.count}`"><div class="progress-bar" :style="{ width: (s.count / d.stats.tracked) * 100 + '%', background: STATUS_COLORS[s.key] }" /></div>
              <span class="fw-semibold text-end" style="width: 24px">{{ s.count }}</span>
            </div>
          </div>
          <p v-else class="text-muted small mb-0">You aren’t tracking any applications yet. Open an opportunity and click <strong>Track application</strong>.</p>
        </section>

        <!-- Recently added -->
        <section>
          <h2 class="h5 fw-bold mb-3">{{ t('dash.recent') }}</h2>
          <div class="row g-3"><div v-for="o in d.recent" :key="o.id" class="col-md-6"><OpportunityCard :o="o" /></div></div>
        </section>
      </div>

      <div class="col-xl-4 d-grid gap-4 align-content-start">
        <!-- Quick actions -->
        <section class="fs-card fs-card-pad">
          <h2 class="h6 fw-bold mb-3">{{ t('dash.quick') }}</h2>
          <div class="row g-2">
            <div v-for="q in quick" :key="q.label" class="col-6"><router-link :to="q.to" class="btn btn-soft w-100 flex-column py-3 h-100"><component :is="q.icon" :size="20" /><span class="small">{{ q.label }}</span></router-link></div>
          </div>
        </section>

        <!-- Deadlines -->
        <section class="fs-card fs-card-pad">
          <h2 class="h6 fw-bold mb-3">{{ t('dash.deadlines') }}</h2>
          <ul v-if="d.upcoming_deadlines.length" class="list-unstyled mb-0 d-grid gap-2">
            <li v-for="o in d.upcoming_deadlines" :key="o.id">
              <router-link :to="`/app/opportunities/${o.slug}`" class="d-flex gap-2 align-items-center text-decoration-none p-2 rounded-3 border border-soft">
                <div class="text-center rounded-3 px-2 py-1 flex-shrink-0" :class="o.days_left <= 7 ? 'tint-peach' : 'tint-lavender'" style="min-width: 52px"><div class="fw-bold font-display">{{ o.days_left }}</div><div style="font-size:.65rem">days</div></div>
                <div class="min-w-0"><div class="small fw-semibold text-truncate" style="color: var(--fs-text)">{{ o.title }}</div><div class="small text-muted">{{ formatDate(o.deadline) }}</div></div>
              </router-link>
            </li>
          </ul>
          <p v-else class="small text-muted mb-0">No deadlines for your saved or tracked opportunities. Save something to get reminders.</p>
        </section>

        <!-- Pending documents -->
        <section class="fs-card fs-card-pad">
          <div class="d-flex justify-content-between align-items-center mb-3"><h2 class="h6 fw-bold mb-0">{{ t('dash.pendingDocs') }}</h2><router-link to="/app/documents" class="small">Upload</router-link></div>
          <ul v-if="d.pending_documents.length" class="list-unstyled mb-0 d-grid gap-2">
            <li v-for="(p, i) in d.pending_documents" :key="i" class="d-flex gap-2 small"><FileWarning :size="17" class="flex-shrink-0" style="color: var(--fs-warning)" /><div><span class="fw-semibold">{{ p.document_type.name }}</span><span class="text-muted"> for {{ p.opportunity_title }}</span></div></li>
          </ul>
          <p v-else class="small text-muted mb-0 d-flex gap-2"><CircleCheck :size="17" style="color: var(--fs-success)" /> Nothing missing for your tracked applications.</p>
        </section>

        <!-- Notifications -->
        <section class="fs-card fs-card-pad">
          <div class="d-flex justify-content-between align-items-center mb-3"><h2 class="h6 fw-bold mb-0">{{ t('nav.notifications') }}</h2><router-link to="/app/notifications" class="small">{{ t('common.viewAll') }}</router-link></div>
          <ul v-if="d.notifications.length" class="list-unstyled mb-0 d-grid gap-2">
            <li v-for="n in d.notifications" :key="n.id" class="small"><router-link :to="n.link || '/app/notifications'" class="text-decoration-none" style="color: var(--fs-text)"><span class="fw-semibold">{{ n.title }}</span></router-link><div class="text-muted">{{ timeAgo(n.created_at) }}</div></li>
          </ul>
          <p v-else class="small text-muted mb-0">You’re all caught up.</p>
        </section>

        <!-- Weekly activity: single series -> one hue, no legend; hover title + screen-reader list -->
        <section class="fs-card fs-card-pad">
          <h2 class="h6 fw-bold mb-1">{{ t('dash.activity') }}</h2>
          <p class="small text-muted mb-3">Actions per day: saves, status updates, uploads and questions.</p>
          <div class="d-flex align-items-end gap-2" style="height: 96px" aria-hidden="true">
            <div v-for="w in d.weekly_activity" :key="w.date" class="flex-fill d-flex flex-column align-items-center justify-content-end h-100" :title="`${formatDate(w.date, { weekday: 'short', day: 'numeric', month: 'short' })}: ${w.count} action${w.count === 1 ? '' : 's'}`">
              <span class="small fw-semibold mb-1" style="font-size:.7rem">{{ w.count || '' }}</span>
              <div class="w-100" style="max-width: 26px; border-radius: 4px 4px 0 0; background: var(--fs-primary)" :style="{ height: Math.max(3, (w.count / maxActivity) * 64) + 'px', opacity: w.count ? 1 : .25 }" />
            </div>
          </div>
          <div class="d-flex gap-2 mt-1" aria-hidden="true"><span v-for="w in d.weekly_activity" :key="w.date" class="flex-fill text-center text-muted" style="font-size:.68rem">{{ formatDate(w.date, { weekday: 'narrow' }) }}</span></div>
          <ul class="visually-hidden"><li v-for="w in d.weekly_activity" :key="w.date">{{ formatDate(w.date) }}: {{ w.count }} actions</li></ul>
        </section>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { Bookmark, Bot, CalendarDays, CircleCheck, Compass, FileText, FileWarning, KanbanSquare, Megaphone, Send, UserRound } from 'lucide-vue-next'
import api from '@/api'
import { useAuth } from '@/stores/auth'
import { formatDate, label, STATUS_COLORS, timeAgo } from '@/utils/format'
import OpportunityCard from '@/components/OpportunityCard.vue'
import ProgressRing from '@/components/ProgressRing.vue'
import StateBlock from '@/components/StateBlock.vue'
import SpotArt from '@/components/art/SpotArt.vue'

const { t } = useI18n()
const auth = useAuth()
const d = ref(null)
const loading = ref(true)
const error = ref('')

async function load() {
  loading.value = true; error.value = ''
  try { d.value = await api.get('/dashboard') } catch (e) { error.value = e.message } finally { loading.value = false }
}
onMounted(load)

const stats = computed(() => [
  { label: 'Saved', value: d.value.stats.saved, icon: Bookmark, tint: 'tint-lavender', to: '/app/saved' },
  { label: 'Tracking', value: d.value.stats.tracked, icon: KanbanSquare, tint: 'tint-sky', to: '/app/tracker' },
  { label: 'Applied', value: d.value.stats.applied, icon: Send, tint: 'tint-mint', to: '/app/tracker' },
  { label: 'Deadlines this week', value: d.value.stats.deadlines_this_week, icon: CalendarDays, tint: 'tint-peach', to: '/app/calendar' },
])
const progressRows = computed(() => Object.entries(d.value.applications_by_status).filter(([, n]) => n).map(([key, count]) => ({ key, count, label: label('status', key) })))
const maxActivity = computed(() => Math.max(1, ...d.value.weekly_activity.map((w) => w.count)))
const quick = [
  { label: 'Find matches', to: '/app/discover', icon: Compass },
  { label: 'Upload document', to: '/app/documents', icon: FileText },
  { label: 'Ask Saathi', to: '/app/saathi', icon: Bot },
  { label: 'Update profile', to: '/app/profile', icon: UserRound },
]
</script>
