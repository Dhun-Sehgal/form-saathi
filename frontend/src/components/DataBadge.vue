<!-- The trust labels: Verified / Demo / Pending / Expired. Always icon + text, never colour alone. -->
<template>
  <span v-if="o.data_origin === 'demo'" class="fs-badge fs-badge-demo" title="Sample data to demonstrate FormSaathi — not a real opportunity">
    <FlaskConical /> {{ t('common.demo') }}
  </span>
  <span v-if="o.verification_status === 'verified'" class="fs-badge fs-badge-verified" :title="o.last_verified_at ? 'Last verified ' + formatDate(o.last_verified_at) : ''">
    <BadgeCheck /> {{ t('common.verified') }}
  </span>
  <span v-else-if="o.verification_status === 'expired' || (o.days_left !== null && o.days_left < 0)" class="fs-badge fs-badge-expired">
    <CircleOff /> {{ t('common.expired') }}
  </span>
  <span v-else-if="o.verification_status === 'pending_verification' && o.data_origin !== 'demo'" class="fs-badge fs-badge-pending">
    <Clock /> {{ t('common.pending') }}
  </span>
</template>

<script setup>
import { BadgeCheck, CircleOff, Clock, FlaskConical } from 'lucide-vue-next'
import { useI18n } from 'vue-i18n'
import { formatDate } from '@/utils/format'
defineProps({ o: { type: Object, required: true } })
const { t } = useI18n()
</script>
