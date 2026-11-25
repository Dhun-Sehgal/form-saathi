<template>
  <section class="section">
    <div class="container" style="max-width: 860px">
      <div class="section-eyebrow mb-2">About</div>
      <h1 class="section-title mb-3">We help people claim the opportunities they deserve.</h1>
      <p class="lead text-muted">Every year, students and families miss scholarships, schemes and jobs — not because they aren’t eligible, but because the information is scattered, the rules are confusing and the forms are hard. FormSaathi exists to fix that.</p>

      <div class="row g-3 my-4">
        <div v-for="v in values" :key="v.title" class="col-md-6">
          <div class="fs-card fs-card-pad h-100">
            <span class="icon-tile icon-tile-sm mb-2" :class="v.tint"><component :is="v.icon" /></span>
            <h2 class="h6 fw-bold">{{ v.title }}</h2>
            <p class="small text-muted mb-0">{{ v.text }}</p>
          </div>
        </div>
      </div>

      <h2 class="h4 fw-bold mt-5">Our data-accuracy policy</h2>
      <ul class="text-muted">
        <li>Real opportunities are added only from official sources and show their source link and last-verified date.</li>
        <li>Listings stay labelled <em>Pending verification</em> until a reviewer checks them.</li>
        <li>We never publish made-up listings — the system itself refuses to mark sample data as verified.</li>
        <li>Expired opportunities are marked automatically and are never recommended as open.</li>
        <li>We don’t scrape websites against their terms.</li>
      </ul>

      <h2 class="h4 fw-bold mt-4">Start with official portals</h2>
      <p class="text-muted">These government platforms are good places to look as well:</p>
      <div class="row g-2">
        <div v-for="p in meta.portals" :key="p.url" class="col-md-6">
          <a :href="p.url" target="_blank" rel="noopener" class="fs-card fs-card-hover p-3 d-block text-decoration-none h-100">
            <div class="fw-semibold d-flex align-items-center gap-1" style="color: var(--fs-text)">{{ p.name }} <ExternalLink :size="14" class="text-muted" /></div>
            <div class="small text-muted">{{ p.description }}</div>
          </a>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { BadgeCheck, ExternalLink, HeartHandshake, Languages, Lock } from 'lucide-vue-next'
import { useMeta } from '@/stores/meta'
const meta = useMeta()
const values = [
  { icon: BadgeCheck, title: 'Truth over volume', text: 'Fewer listings that are right beat thousands that might be wrong.', tint: 'tint-mint' },
  { icon: HeartHandshake, title: 'Guidance, not just links', text: 'We stay with you from discovery to submission.', tint: 'tint-lavender' },
  { icon: Languages, title: 'In your language', text: 'Help in English, Hindi and Marathi — more to come.', tint: 'tint-sky' },
  { icon: Lock, title: 'Privacy first', text: 'We collect only what helps you, and you can export or delete it anytime.', tint: 'tint-peach' },
]
</script>
