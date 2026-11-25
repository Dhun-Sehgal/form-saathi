// Formatting + label helpers shared by all views.
export const LABELS = {
  education: { class_10: 'Class 10', class_12: 'Class 12', diploma: 'Diploma', iti: 'ITI', undergraduate: 'Undergraduate', postgraduate: 'Postgraduate', doctorate: 'Doctorate / PhD', not_studying: 'Not currently studying', other: 'Other' },
  income: { below_1l: 'Below ₹1 lakh', '1l_to_2_5l': '₹1 – 2.5 lakh', '2_5l_to_5l': '₹2.5 – 5 lakh', '5l_to_8l': '₹5 – 8 lakh', above_8l: 'Above ₹8 lakh', prefer_not_say: 'Prefer not to say' },
  social: { general: 'General', ews: 'EWS', obc: 'OBC', sc: 'SC', st: 'ST', prefer_not_say: 'Prefer not to say' },
  gender: { female: 'Female', male: 'Male', other: 'Other', prefer_not_say: 'Prefer not to say' },
  status: { interested: 'Interested', saved: 'Saved', preparing_documents: 'Preparing documents', ready_to_apply: 'Ready to apply', applied: 'Applied', under_review: 'Under review', approved: 'Approved', rejected: 'Rejected' },
  verification: { verified: 'Verified', pending_verification: 'Pending verification', expired: 'Expired', archived: 'Archived' },
  publication: { draft: 'Draft', published: 'Published', unpublished: 'Unpublished' },
  criterion: { age_min: 'Minimum age', age_max: 'Maximum age', education_level: 'Education level', course: 'Course / field', year_of_study: 'Year of study', marks_min_percentage: 'Minimum % marks', marks_min_cgpa: 'Minimum CGPA', income_max: 'Income limit', state_domicile: 'State / domicile', social_category: 'Social category', gender: 'Gender', disability: 'Disability', custom: 'Other rule (manual review)' },
  frequency: { one_time: 'one-time', annual: 'per year', monthly: 'per month', stipend: 'per month', other: '' },
  org: { central_government: 'Central Government', state_government: 'State Government', university: 'University / Institute', psu: 'PSU', private: 'Private company', ngo: 'NGO / Foundation', international: 'International', other: 'Other' },
  language: { en: 'English', hi: 'हिन्दी', mr: 'मराठी' },
}
export const label = (group, key) => (LABELS[group] && LABELS[group][key]) || (key ? String(key).replace(/_/g, ' ') : '')

export const STATUS_COLORS = {
  interested: '#A9A4C9', saved: '#B39DFF', preparing_documents: '#FFB020', ready_to_apply: '#36B6F5',
  applied: '#6A4CF0', under_review: '#B86BFF', approved: '#1FB57F', rejected: '#E5484D',
}

export function formatDate(value, opts = { day: 'numeric', month: 'short', year: 'numeric' }) {
  if (!value) return '—'
  const d = typeof value === 'string' && value.length === 10 ? new Date(value + 'T00:00:00') : new Date(value)
  return isNaN(d) ? '—' : d.toLocaleDateString('en-IN', opts)
}
export function formatDateTime(value) {
  if (!value) return '—'
  return new Date(value).toLocaleString('en-IN', { day: 'numeric', month: 'short', hour: 'numeric', minute: '2-digit' })
}
export function timeAgo(value) {
  if (!value) return ''
  const s = (Date.now() - new Date(value).getTime()) / 1000
  if (s < 60) return 'just now'
  if (s < 3600) return `${Math.floor(s / 60)} min ago`
  if (s < 86400) return `${Math.floor(s / 3600)} h ago`
  if (s < 86400 * 7) return `${Math.floor(s / 86400)} d ago`
  return formatDate(value)
}
export function inr(n) {
  if (n === null || n === undefined) return ''
  return '₹' + Number(n).toLocaleString('en-IN', { maximumFractionDigits: 0 })
}
export function benefitAmount(o) {
  const { benefit_amount_min: lo, benefit_amount_max: hi, benefit_frequency: f } = o
  if (lo == null && hi == null) return null
  const amount = lo != null && hi != null && lo !== hi ? `${inr(lo)} – ${inr(hi)}` : inr(hi ?? lo)
  const suffix = LABELS.frequency[f] || ''
  return suffix ? `${amount} ${suffix}` : amount
}
export function deadlineInfo(o) {
  if (o.is_rolling && !o.deadline) return { text: o.deadline_note || 'Rolling deadline', tone: '' }
  if (!o.deadline) return { text: 'No deadline listed', tone: '' }
  const d = o.days_left
  if (d < 0) return { text: `Closed ${formatDate(o.deadline)}`, tone: '' }
  if (d === 0) return { text: 'Closes today', tone: 'urgent' }
  if (d === 1) return { text: 'Closes tomorrow', tone: 'urgent' }
  if (d <= 7) return { text: `${d} days left`, tone: 'urgent' }
  if (d <= 21) return { text: `${d} days left`, tone: 'soon' }
  return { text: `Closes ${formatDate(o.deadline)}`, tone: '' }
}
export function bytes(n) {
  if (n < 1024) return `${n} B`
  if (n < 1024 * 1024) return `${(n / 1024).toFixed(0)} KB`
  return `${(n / 1024 / 1024).toFixed(1)} MB`
}
export function initials(name) {
  return (name || '?').split(' ').filter(Boolean).slice(0, 2).map((s) => s[0].toUpperCase()).join('')
}
export function downloadText(filename, text) {
  const a = document.createElement('a')
  a.href = URL.createObjectURL(new Blob([text], { type: 'text/plain;charset=utf-8' }))
  a.download = filename
  a.click()
  setTimeout(() => URL.revokeObjectURL(a.href), 1000)
}
