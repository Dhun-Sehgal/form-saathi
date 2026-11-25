// Browser-only implementation of the FormSaathi API for the GitHub Pages preview.
// Mirrors backend/app/api/*.py response shapes. Data lives in this browser only (localStorage + IndexedDB).
import { ApiError } from '../index.js'
import { evaluate, templateExplanation } from './eligibility.js'
import reference from '@shared/reference.json'
import official from '@shared/opportunities.json'

// v2: real, source-checked opportunities (v1 held sample data — bumping the key discards it).
const KEY = 'formsaathi_preview_v2'
const PRE_APPLY = ['interested', 'saved', 'preparing_documents', 'ready_to_apply']
const STATUSES = ['interested', 'saved', 'preparing_documents', 'ready_to_apply', 'applied', 'under_review', 'approved', 'rejected']
export const PREVIEW_ADMIN = { email: 'admin@formsaathi.demo', password: 'admin1234' }

// ------------------------------------------------------------------ storage
const pad = (n) => String(n).padStart(2, '0')
const ymd = (d) => `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`
const today = () => ymd(new Date())
const addDays = (n, from = new Date()) => { const d = new Date(from); d.setDate(d.getDate() + n); return ymd(d) }
const daysUntil = (s) => s ? Math.round((new Date(s + 'T00:00:00') - new Date(today() + 'T00:00:00')) / 86400000) : null
const now = () => new Date().toISOString()
const err = (status, code, message, fields) => { throw new ApiError(status, code, message, fields) }

async function sha(text) {
  const buf = await crypto.subtle.digest('SHA-256', new TextEncoder().encode('fs-preview:' + text))
  return [...new Uint8Array(buf)].map((b) => b.toString(16).padStart(2, '0')).join('')
}

let S = null
function load() {
  if (S) return S
  try { S = JSON.parse(localStorage.getItem(KEY)) } catch { S = null }
  if (!S || S.version !== 2) S = null
  return S
}
function save() { localStorage.setItem(KEY, JSON.stringify(S)) }
const nextId = (table) => { S.seq[table] = (S.seq[table] || 0) + 1; return S.seq[table] }
const stateCode = (name) => name.toLowerCase().replace(/ and /g, '-').replace(/ /g, '-')

async function init() {
  if (load()) return S
  S = { version: 2, seq: {}, session: null, users: [], profiles: {}, prefs: {}, saved: [], collections: [], applications: [],
    history: [], notes: [], reminders: [], notifications: [], documents: [], chats: [], messages: [], corrections: [],
    announcements: [], feedback: [], logs: [], orgs: [], opportunities: [] }
  S.states = reference.states.map(([name, kind]) => ({ code: stateCode(name), name, kind })).sort((a, b) => a.name.localeCompare(b.name))
  S.categories = reference.categories.map((c, i) => ({ id: i + 1, sort_order: i, is_active: true, ...c }))
  S.docTypes = reference.document_types.map((d, i) => ({ id: i + 1, ...d }))
  S.seq.categories = S.categories.length
  const orgKey = {}
  for (const o of official.organizations) { const id = nextId('orgs'); S.orgs.push({ id, name: o.name, org_type: o.org_type, website: o.website }); orgKey[o.key] = id }
  const verifiedAt = `${official.verified_on}T12:00:00.000Z`
  official.opportunities.forEach((item, idx) => {
    const id = nextId('opportunities')
    const deadline = item.deadline || null
    const crit = item.criteria.map((c, i) => ({ id: nextId('criteria'), criterion_type: c.type, value: c.value || {}, description: c.description, source_excerpt: c.excerpt || null, is_mandatory: c.mandatory !== false, sort_order: i }))
    const ceilings = crit.filter((c) => c.criterion_type === 'income_max' && c.is_mandatory).map((c) => c.value.amount)
    const created = new Date(Date.parse(verifiedAt) - (official.opportunities.length - idx) * 60e3).toISOString()
    const status = deadline && deadline < today() ? 'expired' : 'verified'
    S.opportunities.push({
      id, slug: item.slug, title: item.title, summary: item.summary, description: item.description,
      category_id: S.categories.find((c) => c.slug === item.category).id, organization_id: orgKey[item.org], scope: item.scope || 'national',
      eligibility_summary: item.eligibility_summary, benefits: item.benefits, benefit_amount_min: item.benefit_amount_min ?? null,
      benefit_amount_max: item.benefit_amount_max ?? null, benefit_frequency: item.benefit_frequency || null,
      income_ceiling: ceilings.length ? Math.min(...ceilings) : null,
      application_mode: item.application_mode || 'online', how_to_apply: item.how_to_apply || null,
      official_url: item.official_url || null, apply_url: item.apply_url || null, source_url: item.source_url,
      opens_on: item.opens_on || null, deadline, is_rolling: !!item.rolling, deadline_note: item.deadline_note || null,
      verification_status: status, publication_status: 'published', data_origin: 'official',
      last_verified_at: verifiedAt, is_featured: !!item.featured, featured_rank: item.featured || null, created_at: created, updated_at: created,
      states: [...new Set(crit.filter((c) => c.criterion_type === 'state_domicile').flatMap((c) => c.value.any_of))],
      education_levels: [...new Set(crit.filter((c) => c.criterion_type === 'education_level').flatMap((c) => c.value.any_of))],
      criteria: crit,
      required_documents: item.documents.map((d) => ({ document_type_id: S.docTypes.find((t) => t.slug === d.type).id, is_mandatory: d.mandatory !== false, notes: d.notes || null })),
      dates: item.dates.map((d) => ({ label: d.label, date: d.date, note: d.note || null })),
    })
    S.logs.push({ id: nextId('logs'), opportunity_id: id, action: 'verified', from_status: null, to_status: status, notes: `Checked against the official source on ${official.verified_on} while setting up FormSaathi.`, actor: 'system', created_at: verifiedAt })
  })
  await createUser(PREVIEW_ADMIN.email, PREVIEW_ADMIN.password, 'Demo Admin', 'admin', true)
  S.announcements.push({ id: nextId('announcements'), title: 'Welcome to the FormSaathi preview', body: 'Your account and everything you do here is stored only in this browser. Opportunities are real and were checked against official sources — always confirm dates on the official site before applying.', audience: 'all', level: 'info', starts_at: null, ends_at: null, is_active: true, created_at: now() })
  save()
  return S
}

async function createUser(email, password, fullName, role = 'user', onboarded = false) {
  const id = nextId('users')
  S.users.push({ id, email, password_hash: await sha(password), role, is_active: true, created_at: now(), last_login_at: null })
  S.profiles[id] = { full_name: fullName, date_of_birth: null, gender: null, state_code: null, city: null, education_level: null, institution: null,
    course: null, stream: null, current_year: null, marks_type: null, marks_value: null, income_range: null, social_category: null, has_disability: null,
    skills: [], career_interests: [], interests: [], preferred_language: 'en', onboarding_step: onboarded ? 5 : 0, onboarding_completed_at: onboarded ? now() : null }
  S.prefs[id] = { email_enabled: true, deadline_reminders: true, deadline_days_before: 7, document_reminders: true, status_reminders: true, opportunity_updates: true, weekly_digest: false }
  return id
}

// ------------------------------------------------------------------ serializers (same shapes as backend/app/serializers.py)
const CORE = [['full_name', 'Full name'], ['date_of_birth', 'Date of birth'], ['state_code', 'State'], ['city', 'City'], ['education_level', 'Education level'], ['institution', 'College / institution'], ['course', 'Course'], ['current_year', 'Year of study'], ['marks_value', 'Marks / CGPA'], ['interests', 'Interested categories'], ['skills', 'Skills']]
const OPTIONAL = [['income_range', 'Family income range'], ['social_category', 'Social category'], ['gender', 'Gender'], ['has_disability', 'Disability status']]
function completion(p) {
  const filled = (f) => Array.isArray(p[f]) ? p[f].length > 0 : p[f] !== null && p[f] !== undefined && p[f] !== ''
  const missing = CORE.filter(([f]) => !filled(f)).map(([, l]) => l)
  return { percent: Math.round(100 * (CORE.length - missing.length) / CORE.length), missing, optional_missing: OPTIONAL.filter(([f]) => p[f] == null).map(([, l]) => l) }
}
function userDict(u) {
  const p = S.profiles[u.id]
  return { id: u.id, email: u.email, role: u.role, is_active: u.is_active, email_verified: false, created_at: u.created_at, profile: { ...p }, profile_completion: completion(p), onboarding_completed: !!p.onboarding_completed_at }
}
const cat = (id) => S.categories.find((c) => c.id === id)
const org = (id) => S.orgs.find((o) => o.id === id)
const docType = (id) => { const d = S.docTypes.find((t) => t.id === id); return { id: d.id, slug: d.slug, name: d.name, description: d.description, sensitivity: d.sensitivity } }
const isOpen = (o) => o.publication_status === 'published' && !['expired', 'archived'].includes(o.verification_status) && (!o.deadline || o.deadline >= today())

function ctx(user) {
  if (!user) return [new Set(), {}]
  return [new Set(S.saved.filter((s) => s.user_id === user.id).map((s) => s.opportunity_id)),
    Object.fromEntries(S.applications.filter((a) => a.user_id === user.id).map((a) => [a.opportunity_id, a.status]))]
}
function card(o, user) {
  const [saved, apps] = ctx(user)
  const c = cat(o.category_id), g = org(o.organization_id)
  return { id: o.id, slug: o.slug, title: o.title, summary: o.summary, category: { slug: c.slug, name: c.name, icon: c.icon, color: c.color },
    organization: { name: g.name, org_type: g.org_type }, scope: o.scope, eligibility_summary: o.eligibility_summary, benefits: o.benefits,
    benefit_amount_min: o.benefit_amount_min, benefit_amount_max: o.benefit_amount_max, benefit_frequency: o.benefit_frequency,
    deadline: o.deadline, is_rolling: o.is_rolling, deadline_note: o.deadline_note, days_left: daysUntil(o.deadline), is_open: isOpen(o),
    official_url: o.official_url, apply_url: o.apply_url, source_url: o.source_url, verification_status: o.verification_status,
    publication_status: o.publication_status, data_origin: o.data_origin, last_verified_at: o.last_verified_at, is_featured: o.is_featured,
    created_at: o.created_at, states: [...o.states], saved: saved.has(o.id), application_status: apps[o.id] || null }
}
function detail(o, user) {
  return { ...card(o, user), description: o.description, how_to_apply: o.how_to_apply, application_mode: o.application_mode, opens_on: o.opens_on,
    income_ceiling: o.income_ceiling, organization: { ...org(o.organization_id) }, category_id: o.category_id, organization_id: o.organization_id,
    criteria: o.criteria.map((c) => ({ ...c })), required_documents: o.required_documents.map((r) => ({ document_type: docType(r.document_type_id), is_mandatory: r.is_mandatory, notes: r.notes })),
    dates: o.dates.map((d) => ({ ...d })), updated_at: o.updated_at, education_levels: [...o.education_levels] }
}
function appDict(a, full = false) {
  const o = S.opportunities.find((x) => x.id === a.opportunity_id)
  const d = { id: a.id, status: a.status, status_source: 'user', applied_on: a.applied_on, reference_number: a.reference_number, created_at: a.created_at, updated_at: a.updated_at, opportunity: card(o, userById(a.user_id)) }
  if (full) {
    d.history = S.history.filter((h) => h.application_id === a.id).map(({ from_status, to_status, note, created_at }) => ({ from_status, to_status, source: 'user', note, created_at }))
    d.notes = S.notes.filter((n) => n.application_id === a.id).sort((x, y) => y.id - x.id).map(({ id, body, created_at }) => ({ id, body, created_at }))
  }
  return d
}
function docDict(d) {
  const expired = d.expires_on && d.expires_on < today()
  return { id: d.id, document_type: docType(d.document_type_id), label: d.label, original_filename: d.original_filename, mime_type: d.mime_type, size_bytes: d.size_bytes, status: expired ? 'expired' : 'uploaded', issued_on: d.issued_on, expires_on: d.expires_on, created_at: d.created_at }
}
const userById = (id) => S.users.find((u) => u.id === id)
function me(required = true) {
  const u = S.session ? userById(S.session) : null
  if (!u && required) err(401, 'unauthorized', 'Please log in to continue.')
  return u
}
function admin() { const u = me(); if (u.role !== 'admin') err(403, 'forbidden', 'Admins only.'); return u }
const visible = (o) => o && o.publication_status === 'published' && o.verification_status !== 'archived'
function findOpp(id, slug) {
  const o = S.opportunities.find((x) => (id ? x.id === Number(id) : x.slug === slug))
  if (!visible(o)) err(404, 'not_found', 'Opportunity not found.')
  return o
}
function paginate(items, params, per = 12) {
  const page = Math.max(1, Number(params?.page) || 1), perPage = Math.min(48, Number(params?.per_page) || per)
  return { items: items.slice((page - 1) * perPage, page * perPage), page, per_page: perPage, total: items.length, pages: Math.max(1, Math.ceil(items.length / perPage)) }
}
const need = (cond, field, message) => { if (!cond) err(422, 'validation_error', 'Please check the highlighted fields.', { [field]: message }) }

// ------------------------------------------------------------------ domain helpers
const INCOME_LOWER = { below_1l: 0, '1l_to_2_5l': 100000, '2_5l_to_5l': 250000, '5l_to_8l': 500000, above_8l: 800000 }
function filterOpps(params = {}, user) {
  let list = S.opportunities.filter(visible)
  const q = (params.q || '').trim().toLowerCase()
  if (q) list = list.filter((o) => [o.title, o.summary, o.eligibility_summary, o.benefits, org(o.organization_id).name].some((t) => t.toLowerCase().includes(q)))
  if (params.category) { const slugs = params.category.split(','); list = list.filter((o) => slugs.includes(cat(o.category_id).slug)) }
  if (params.education) list = list.filter((o) => !o.education_levels.length || o.education_levels.includes(params.education))
  if (params.state) list = list.filter((o) => o.scope === 'national' || o.states.includes(params.state))
  if (params.income in INCOME_LOWER) list = list.filter((o) => o.income_ceiling == null || o.income_ceiling >= INCOME_LOWER[params.income])
  if (params.origin) list = list.filter((o) => o.data_origin === params.origin)
  if (params.verified === '1') list = list.filter((o) => o.verification_status === 'verified')
  const status = params.status || 'open'
  if (status === 'open') list = list.filter(isOpen)
  if (status === 'closing_soon') list = list.filter((o) => isOpen(o) && o.deadline && daysUntil(o.deadline) <= 14)
  if (status === 'closed') list = list.filter((o) => !isOpen(o))
  if (params.deadline_within) list = list.filter((o) => o.deadline && daysUntil(o.deadline) <= Number(params.deadline_within))
  if (user && params.mine) {
    const [saved, apps] = ctx(user)
    if (params.mine === 'saved') list = list.filter((o) => saved.has(o.id))
    if (params.mine === 'tracked') list = list.filter((o) => apps[o.id])
    if (params.mine === 'not_tracked') list = list.filter((o) => !apps[o.id])
  }
  const dl = (o) => o.deadline || '9999-12-31'
  if (params.sort === 'deadline') list.sort((a, b) => dl(a).localeCompare(dl(b)))
  else if (params.sort === 'recent') list.sort((a, b) => b.created_at.localeCompare(a.created_at))
  else list.sort((a, b) => (q ? (b.title.toLowerCase().includes(q) - a.title.toLowerCase().includes(q)) : 0) || (b.is_featured - a.is_featured) || ((a.featured_rank ?? 99) - (b.featured_rank ?? 99)) || dl(a).localeCompare(dl(b)))
  return list
}
function recommend(user, limit = 6) {
  const p = S.profiles[user.id]
  const [, apps] = ctx(user)
  const interestIds = S.categories.filter((c) => p.interests.includes(c.slug)).map((c) => c.id)
  const scored = []
  for (const o of S.opportunities.filter((x) => visible(x) && isOpen(x))) {
    if (apps[o.id]) continue
    const r = evaluate(p, o.criteria)
    if (r.verdict === 'not_eligible') continue
    let score = 0; const reasons = []
    if (r.verdict === 'eligible') { score += 4; reasons.push('You meet all checkable rules') } else score += 1
    if (interestIds.includes(o.category_id)) { score += 3; reasons.push(`You're interested in ${cat(o.category_id).name}`) }
    if (p.state_code && o.states.includes(p.state_code)) { score += 2; reasons.push('For your state') }
    const dl = daysUntil(o.deadline)
    if (dl !== null && dl >= 0 && dl <= 30) { score += 1; reasons.push('Deadline coming up') }
    if (o.is_featured) score += 1
    scored.push({ score, o, verdict: r.verdict, reasons: reasons.slice(0, 3) })
  }
  scored.sort((a, b) => b.score - a.score || (a.o.deadline || '9999').localeCompare(b.o.deadline || '9999'))
  return scored.slice(0, limit).map(({ o, verdict, reasons }) => ({ ...card(o, user), match: { verdict, reasons } }))
}
function activeDocs(uid) { return S.documents.filter((d) => d.user_id === uid && !d.deleted_at).sort((a, b) => b.id - a.id) }
function checklist(uid, o) {
  const byType = {}
  for (const d of activeDocs(uid)) byType[d.document_type_id] ??= d
  const items = o.required_documents.map((r) => {
    const have = byType[r.document_type_id]
    let status = 'ready'
    if (!have) status = 'missing'
    else if (have.expires_on && have.expires_on < today()) status = 'expired'
    else if (have.expires_on && o.deadline && have.expires_on < o.deadline) status = 'expiring'
    return { document_type: docType(r.document_type_id), is_mandatory: r.is_mandatory, notes: r.notes, status, document: have ? docDict(have) : null }
  })
  return { items, ready: items.filter((i) => i.status === 'ready').length, total: items.length, missing_mandatory: items.filter((i) => i.is_mandatory && ['missing', 'expired'].includes(i.status)).length }
}
function push(uid, type, title, body, link, key) {
  if (key && S.notifications.some((n) => n.user_id === uid && n.dedupe_key === key)) return
  S.notifications.push({ id: nextId('notifications'), user_id: uid, type, title, body, link, dedupe_key: key, is_read: false, created_at: now() })
}
function syncNotifications(user) {
  const prefs = S.prefs[user.id], uid = user.id
  if (prefs.deadline_reminders) {
    const ids = new Set([...S.saved.filter((s) => s.user_id === uid).map((s) => s.opportunity_id), ...S.applications.filter((a) => a.user_id === uid && PRE_APPLY.includes(a.status)).map((a) => a.opportunity_id)])
    for (const o of S.opportunities.filter((x) => ids.has(x.id) && x.deadline && !['expired', 'archived'].includes(x.verification_status))) {
      const d = daysUntil(o.deadline)
      if (d < 0 || d > prefs.deadline_days_before) continue
      const when = d === 0 ? 'today' : d === 1 ? 'tomorrow' : `in ${d} days`
      push(uid, 'deadline', `${o.title} closes ${when}`, `Deadline: ${o.deadline}. Finish your documents and apply on the official site.`, `/app/opportunities/${o.slug}`, `deadline:${o.id}:${d <= 1 ? '1d' : d <= 3 ? '3d' : 'window'}`)
    }
  }
  if (prefs.document_reminders) {
    const week = Math.floor(Date.now() / (7 * 864e5))
    for (const a of S.applications.filter((x) => x.user_id === uid && PRE_APPLY.includes(x.status))) {
      const o = S.opportunities.find((x) => x.id === a.opportunity_id)
      const missing = checklist(uid, o).missing_mandatory
      if (missing) push(uid, 'document_missing', `${missing} document(s) missing for ${o.title}`, "Upload them to your document vault so you're ready to apply.", `/app/tracker/${a.id}`, `docs:${a.id}:${week}`)
    }
  }
  for (const r of S.reminders.filter((x) => x.user_id === uid && !x.sent_at && !x.is_done && x.remind_at <= now())) {
    push(uid, 'reminder', r.title, 'Your personal reminder.', r.application_id ? `/app/tracker/${r.application_id}` : '/app/calendar', `reminder:${r.id}`)
    r.sent_at = now()
  }
}

// ------------------------------------------------------------------ IndexedDB for uploaded files
function idb() {
  return new Promise((resolve, reject) => {
    const req = indexedDB.open('formsaathi-preview', 1)
    req.onupgradeneeded = () => req.result.createObjectStore('files')
    req.onsuccess = () => resolve(req.result)
    req.onerror = () => reject(req.error)
  })
}
async function idbDo(mode, fn) {
  const db = await idb()
  return new Promise((resolve, reject) => {
    const tx = db.transaction('files', mode)
    const req = fn(tx.objectStore('files'))
    tx.oncomplete = () => resolve(req?.result)
    tx.onerror = () => reject(tx.error)
  })
}
async function sniff(file) {
  const b = new Uint8Array(await file.slice(0, 12).arrayBuffer())
  const s = String.fromCharCode(...b)
  if (s.startsWith('%PDF-')) return 'application/pdf'
  if (b[0] === 0x89 && s.slice(1, 4) === 'PNG') return 'image/png'
  if (b[0] === 0xff && b[1] === 0xd8 && b[2] === 0xff) return 'image/jpeg'
  if (s.startsWith('RIFF') && s.slice(8, 12) === 'WEBP') return 'image/webp'
  return null
}

// ------------------------------------------------------------------ routes
const routes = []
const on = (method, pattern, fn) => routes.push([method, new RegExp('^' + pattern.replace(/:(\w+)/g, '(?<$1>[^/]+)') + '$'), fn])

// auth
on('post', '/auth/register', async ({ data }) => {
  const email = (data.email || '').trim().toLowerCase()
  need(/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email), 'email', 'Enter a valid email.')
  need((data.password || '').length >= 8 && /[A-Za-z]/.test(data.password) && /\d/.test(data.password), 'password', 'Use at least 8 characters with letters and numbers.')
  need((data.full_name || '').trim().length >= 2, 'full_name', 'Enter your name.')
  need(data.accept_terms, 'accept_terms', 'Please accept the terms and privacy policy.')
  if (S.users.some((u) => u.email === email)) err(409, 'email_taken', 'An account with this email already exists. Try logging in.', { email: 'Already registered.' })
  S.session = await createUser(email, data.password, data.full_name.trim())
  return { user: userDict(userById(S.session)) }
})
on('post', '/auth/login', async ({ data }) => {
  const u = S.users.find((x) => x.email === (data.email || '').trim().toLowerCase())
  if (!u || u.password_hash !== await sha(data.password || '')) err(401, 'invalid_credentials', 'Email or password is incorrect.')
  if (!u.is_active) err(403, 'account_disabled', 'This account has been deactivated.')
  u.last_login_at = now(); S.session = u.id
  return { user: userDict(u) }
})
on('post', '/auth/logout', () => { S.session = null; return { ok: true } })
on('post', '/auth/refresh', () => ({ user: userDict(me()) }))
on('get', '/auth/me', () => ({ user: userDict(me()) }))
on('post', '/auth/forgot-password', async ({ data }) => {
  const u = S.users.find((x) => x.email === (data.email || '').trim().toLowerCase())
  const out = { message: "If an account exists for that email, we've sent a reset link.", email_configured: false }
  if (u) { const token = crypto.randomUUID().replace(/-/g, '') + crypto.randomUUID().replace(/-/g, ''); S.resetTokens = { ...(S.resetTokens || {}), [token]: { uid: u.id, exp: Date.now() + 30 * 60e3 } }; out.preview_reset_token = token }
  return out
})
on('post', '/auth/reset-password', async ({ data }) => {
  const t = (S.resetTokens || {})[data.token]
  if (!t || t.exp < Date.now()) err(400, 'invalid_token', 'This reset link is invalid or has expired. Please request a new one.')
  need((data.password || '').length >= 8 && /[A-Za-z]/.test(data.password) && /\d/.test(data.password), 'password', 'Use at least 8 characters with letters and numbers.')
  userById(t.uid).password_hash = await sha(data.password); delete S.resetTokens[data.token]
  return { message: 'Password updated. You can log in now.' }
})
on('post', '/auth/change-password', async ({ data }) => {
  const u = me()
  if (u.password_hash !== await sha(data.current_password || '')) err(422, 'validation_error', 'Current password is incorrect.', { current_password: 'Incorrect.' })
  need((data.new_password || '').length >= 8 && /[A-Za-z]/.test(data.new_password) && /\d/.test(data.new_password), 'new_password', 'Use at least 8 characters with letters and numbers.')
  u.password_hash = await sha(data.new_password)
  return { message: 'Password changed.' }
})

// profile
on('get', '/profile', () => ({ user: userDict(me()) }))
on('put', '/profile', ({ data }) => {
  const u = me(), p = S.profiles[u.id]
  if (data.marks_value != null && data.marks_type === 'cgpa') need(data.marks_value <= 10, 'marks_value', 'CGPA must be between 0 and 10.')
  if (data.marks_value != null) need(data.marks_value >= 0 && data.marks_value <= 100, 'marks_value', 'Enter a value between 0 and 100.')
  if (data.full_name !== undefined) need((data.full_name || '').trim().length >= 2, 'full_name', 'Enter your name.')
  for (const [k, v] of Object.entries(data)) if (k in p) p[k] = typeof v === 'string' ? (v.trim() || null) : v
  return { user: userDict(u) }
})
on('post', '/profile/onboarding/complete', () => { const u = me(); const p = S.profiles[u.id]; p.onboarding_completed_at ||= now(); p.onboarding_step = 5; return { user: userDict(u) } })
on('get', '/profile/export', () => {
  const u = me()
  return { exported_at: now(), account: { email: u.email, role: u.role, created_at: u.created_at }, profile: S.profiles[u.id],
    saved_opportunities: S.saved.filter((s) => s.user_id === u.id).map((s) => S.opportunities.find((o) => o.id === s.opportunity_id).title),
    applications: S.applications.filter((a) => a.user_id === u.id).map((a) => appDict(a, true)), documents: activeDocs(u.id).map(docDict),
    reminders: S.reminders.filter((r) => r.user_id === u.id), notifications: S.notifications.filter((n) => n.user_id === u.id) }
})
on('delete', '/profile/account', async ({ data }) => {
  const u = me()
  if (u.password_hash !== await sha(data?.password || '')) err(422, 'validation_error', 'Password is incorrect.', { password: 'Incorrect.' })
  if (u.role === 'admin' && S.users.filter((x) => x.role === 'admin').length <= 1) err(409, 'last_admin', 'You are the only admin. Promote another admin before deleting this account.')
  for (const d of S.documents.filter((x) => x.user_id === u.id)) await idbDo('readwrite', (st) => st.delete(d.id))
  for (const t of ['saved', 'collections', 'applications', 'reminders', 'notifications', 'documents', 'chats', 'resumes']) S[t] = (S[t] || []).filter((x) => x.user_id !== u.id)
  S.users = S.users.filter((x) => x.id !== u.id); delete S.profiles[u.id]; delete S.prefs[u.id]; S.session = null
  return { message: 'Your account and personal data have been deleted.' }
})

// meta
on('get', '/health', () => ({ status: 'ok', ai_configured: false, email_configured: false, preview: true }))
on('get', '/meta', () => ({
  categories: S.categories.filter((c) => c.is_active).sort((a, b) => a.sort_order - b.sort_order), states: S.states, document_types: S.docTypes.map((d) => docType(d.id)),
  enums: { education_levels: ['class_10', 'class_12', 'diploma', 'iti', 'undergraduate', 'postgraduate', 'doctorate', 'not_studying', 'other'], income_ranges: ['below_1l', '1l_to_2_5l', '2_5l_to_5l', '5l_to_8l', 'above_8l', 'prefer_not_say'], social_categories: ['general', 'ews', 'obc', 'sc', 'st', 'prefer_not_say'], genders: ['female', 'male', 'other', 'prefer_not_say'], application_statuses: STATUSES, criterion_types: ['age_min', 'age_max', 'education_level', 'course', 'year_of_study', 'marks_min_percentage', 'marks_min_cgpa', 'income_max', 'state_domicile', 'social_category', 'gender', 'disability', 'custom'], org_types: ['central_government', 'state_government', 'university', 'psu', 'private', 'ngo', 'international', 'other'], benefit_frequencies: ['one_time', 'annual', 'monthly', 'stipend', 'other'], application_modes: ['online', 'offline', 'both'], opportunity_scopes: ['national', 'state', 'institution'], correction_fields: ['deadline', 'eligibility', 'benefits', 'documents', 'link', 'other'], feedback_kinds: ['bug', 'idea', 'praise', 'contact', 'other'] },
  portals: reference.portals, features: { ai: false, email: false, preview: true },
}))
on('get', '/announcements', () => ({ items: S.announcements.filter((a) => a.is_active).slice(-3).reverse() }))
on('post', '/feedback', ({ data }) => {
  need((data.message || '').trim().length >= 5, 'message', 'Please write at least a few words.')
  const u = me(false)
  S.feedback.push({ id: nextId('feedback'), user_id: u?.id || null, kind: data.kind || 'other', message: data.message.trim(), page: data.page || null, contact_email: u ? null : data.contact_email || null, status: 'new', created_at: now() })
  return { message: 'Thank you! Your feedback has been received.' }
})

// opportunities
on('get', '/opportunities', ({ params }) => { const u = me(false); return paginate(filterOpps(params, u).map((o) => card(o, u)), params) })
on('get', '/opportunities/featured', () => { const u = me(false); return { items: S.opportunities.filter((o) => visible(o) && isOpen(o) && o.is_featured).sort((a, b) => (a.featured_rank ?? 99) - (b.featured_rank ?? 99)).slice(0, 6).map((o) => card(o, u)) } })
on('get', '/opportunities/recommended', ({ params }) => ({ items: recommend(me(), Number(params?.limit) || 6) }))
on('get', '/opportunities/compare', ({ params }) => { const u = me(false); return { items: (params.ids || '').split(',').filter(Boolean).slice(0, 3).map((id) => detail(findOpp(id), u)) } })
on('get', '/opportunities/:slug', ({ slug }) => {
  const u = me(false), o = findOpp(null, slug)
  return { opportunity: { ...detail(o, u), similar: S.opportunities.filter((x) => visible(x) && isOpen(x) && x.category_id === o.category_id && x.id !== o.id).slice(0, 3).map((x) => card(x, u)) } }
})
on('post', '/opportunities/:id/corrections', ({ id, data }) => {
  const u = me(), o = findOpp(id)
  need((data.message || '').trim().length >= 10, 'message', 'Please describe the issue (at least 10 characters).')
  S.corrections.push({ id: nextId('corrections'), opportunity_id: o.id, user_id: u.id, field: data.field, message: data.message.trim(), suggested_source_url: data.suggested_source_url || null, status: 'open', admin_note: null, created_at: now(), reviewed_at: null })
  return { message: 'Thanks! Our team will review this and update the listing if needed.' }
})

// saved & collections
on('get', '/saved', ({ params }) => {
  const u = me()
  return { items: S.saved.filter((s) => s.user_id === u.id && (!params?.collection_id || s.collection_id === Number(params.collection_id))).sort((a, b) => b.id - a.id)
    .map((s) => ({ ...card(S.opportunities.find((o) => o.id === s.opportunity_id), u), saved_at: s.created_at, collection_id: s.collection_id })) }
})
on('post', '/saved', ({ data }) => {
  const u = me(), o = findOpp(data.opportunity_id)
  let row = S.saved.find((s) => s.user_id === u.id && s.opportunity_id === o.id)
  if (!row) S.saved.push(row = { id: nextId('saved'), user_id: u.id, opportunity_id: o.id, collection_id: data.collection_id || null, created_at: now() })
  else row.collection_id = data.collection_id || null
  return { saved: true, opportunity_id: o.id, collection_id: row.collection_id }
})
on('delete', '/saved/:id', ({ id }) => { const u = me(); S.saved = S.saved.filter((s) => !(s.user_id === u.id && s.opportunity_id === Number(id))); return { saved: false, opportunity_id: Number(id) } })
on('get', '/collections', () => {
  const u = me(), mine = S.saved.filter((s) => s.user_id === u.id)
  return { items: S.collections.filter((c) => c.user_id === u.id).sort((a, b) => a.name.localeCompare(b.name)).map((c) => ({ id: c.id, name: c.name, count: mine.filter((s) => s.collection_id === c.id).length })), uncategorised: mine.filter((s) => !s.collection_id).length }
})
on('post', '/collections', ({ data }) => {
  const u = me(), name = (data.name || '').trim()
  need(name, 'name', 'Enter a name.')
  if (S.collections.some((c) => c.user_id === u.id && c.name === name)) err(409, 'duplicate', 'You already have a collection with this name.', { name: 'Already exists.' })
  const c = { id: nextId('collections'), user_id: u.id, name }; S.collections.push(c)
  return { collection: { id: c.id, name, count: 0 } }
})
on('patch', '/collections/:id', ({ id, data }) => { const c = S.collections.find((x) => x.id === Number(id) && x.user_id === me().id) || err(404, 'not_found', 'Collection not found.'); c.name = data.name.trim(); return { collection: { id: c.id, name: c.name } } })
on('delete', '/collections/:id', ({ id }) => { const u = me(); S.collections = S.collections.filter((c) => !(c.id === Number(id) && c.user_id === u.id)); S.saved.forEach((s) => { if (s.collection_id === Number(id)) s.collection_id = null }); return { ok: true } })

// eligibility & AI
on('post', '/eligibility/:id', ({ id }) => {
  const u = me(), o = findOpp(id), report = evaluate(S.profiles[u.id], o.criteria)
  return { opportunity: { id: o.id, slug: o.slug, title: o.title, data_origin: o.data_origin, verification_status: o.verification_status, source_url: o.source_url }, report, explanation: templateExplanation(report, o.title), explanation_source: 'template', ai_configured: false }
})
const AI_OFF = () => err(503, 'ai_not_configured', 'Saathi AI needs the FormSaathi server with an AI key. This browser-only preview has no AI server, so chat is switched off here. Eligibility checks still work.')
on('get', '/ai/status', () => ({ configured: false }))
on('get', '/ai/sessions', () => { const u = me(); return { items: S.chats.filter((c) => c.user_id === u.id).sort((a, b) => b.updated_at.localeCompare(a.updated_at)), configured: false } })
on('post', '/ai/sessions', ({ data }) => {
  const u = me(), o = data.opportunity_id ? findOpp(data.opportunity_id) : null
  const s = { id: crypto.randomUUID(), user_id: u.id, title: o ? o.title : 'New conversation', language: data.language || 'en', opportunity_id: o?.id || null, created_at: now(), updated_at: now() }
  S.chats.push(s)
  return { session: { ...s, messages: [], opportunity: o ? { id: o.id, slug: o.slug, title: o.title } : null } }
})
on('get', '/ai/sessions/:id', ({ id }) => {
  const s = S.chats.find((c) => c.id === id && c.user_id === me().id) || err(404, 'not_found', 'Conversation not found.')
  const o = s.opportunity_id ? S.opportunities.find((x) => x.id === s.opportunity_id) : null
  return { session: { ...s, messages: S.messages.filter((m) => m.session_id === id), opportunity: o ? { id: o.id, slug: o.slug, title: o.title } : null }, configured: false }
})
on('delete', '/ai/sessions/:id', ({ id }) => { const u = me(); S.chats = S.chats.filter((c) => !(c.id === id && c.user_id === u.id)); S.messages = S.messages.filter((m) => m.session_id !== id); return { ok: true } })
on('post', '/ai/sessions/:id/messages', () => AI_OFF())

// documents
on('get', '/documents', () => ({ items: activeDocs(me().id).map(docDict) }))
on('post', '/documents', async ({ data }) => {
  const u = me(), file = data.get('file'), typeId = Number(data.get('document_type_id'))
  need(S.docTypes.some((t) => t.id === typeId), 'document_type_id', 'Choose a document type.')
  if (!file || !file.size) err(422, 'validation_error', 'Choose a file to upload.', { file: 'Required.' })
  if (file.size > 3 * 1024 * 1024) err(413, 'file_too_large', 'In the browser preview, files can be up to 3 MB.')
  const mime = await sniff(file)
  if (!mime) err(422, 'unsupported_file', "This file doesn't look like a valid PDF or image.")
  const d = { id: nextId('documents'), user_id: u.id, document_type_id: typeId, label: data.get('label') || null, original_filename: file.name, mime_type: mime, size_bytes: file.size, issued_on: data.get('issued_on') || null, expires_on: data.get('expires_on') || null, created_at: now(), deleted_at: null }
  const blob = new Blob([await file.arrayBuffer()], { type: mime })
  await idbDo('readwrite', (st) => st.put(blob, d.id))
  S.documents.push(d)
  return { document: docDict(d) }
})
const ownDoc = (id) => S.documents.find((d) => d.id === Number(id) && d.user_id === me().id && !d.deleted_at) || err(404, 'not_found', 'Document not found.')
on('get', '/documents/:id/file', async ({ id }) => { const d = ownDoc(id); const blob = await idbDo('readonly', (st) => st.get(d.id)); if (!blob) err(410, 'file_missing', 'The file is missing. Please upload it again.'); return blob })
on('patch', '/documents/:id', ({ id, data }) => { const d = ownDoc(id); for (const k of ['label', 'document_type_id', 'issued_on', 'expires_on']) if (k in data) d[k] = data[k] || null; return { document: docDict(d) } })
on('delete', '/documents/:id', async ({ id }) => { const d = ownDoc(id); await idbDo('readwrite', (st) => st.delete(d.id)); d.deleted_at = now(); d.original_filename = 'deleted'; return { ok: true } })
on('get', '/documents/checklist/:id', ({ id }) => { const o = findOpp(id); return { ...checklist(me().id, o), opportunity: { id: o.id, slug: o.slug, title: o.title, deadline: o.deadline } } })

// resumes (ATS resume builder) — same shapes as backend/app/api/resumes.py
const RESUME_LIMIT = 10
const ownResume = (id) => (S.resumes || []).find((x) => x.id === Number(id) && x.user_id === me().id) || err(404, 'not_found', 'Resume not found.')
const resumeDict = (x, full = true) => ({ id: x.id, title: x.title, target_role: x.target_role, template: x.template, created_at: x.created_at, updated_at: x.updated_at, ...(full ? { data: JSON.parse(JSON.stringify(x.data || {})) } : {}) })
function profilePrefill(u) {
  const p = S.profiles[u.id] || {}
  const labels = { class_10: 'Class 10', class_12: 'Class 12', diploma: 'Diploma', iti: 'ITI', undergraduate: "Bachelor's degree", postgraduate: "Master's degree", doctorate: 'PhD' }
  const education = []
  if (p.institution || p.course) {
    const degree = [p.course, p.stream ? `(${p.stream})` : null].filter(Boolean).join(' ') || labels[p.education_level] || ''
    const score = p.marks_value == null ? '' : p.marks_type === 'cgpa' ? `CGPA: ${p.marks_value}` : `${p.marks_value}%`
    education.push({ school: p.institution || '', degree, start: '', end: '', score, details: '' })
  }
  const state = S.states.find((x) => x.code === p.state_code)?.name
  return { basics: { name: p.full_name || '', headline: '', email: u.email, phone: '', location: [p.city, state].filter(Boolean).join(', '), links: [] },
    summary: '', experience: [], projects: [], education, skills: (p.skills || []).length ? [{ group: 'Skills', items: p.skills.join(', ') }] : [], achievements: [], certifications: [] }
}
function checkResume(data) {
  need((data.title || '').trim().length >= 1 && data.title.length <= 120, 'title', 'Enter a name for this resume.')
  if (data.template) need(['classic', 'modern'].includes(data.template), 'template', 'Choose classic or modern.')
  const d = data.data || {}
  for (const k of ['experience', 'projects']) for (const it of d[k] || []) need((it.bullets || []).length <= 8, k, 'Keep it to 8 bullets or fewer.')
}
on('get', '/resumes', () => { const u = me(); return { items: (S.resumes || []).filter((x) => x.user_id === u.id).sort((a, b) => b.updated_at.localeCompare(a.updated_at)).map((x) => resumeDict(x, false)), ai_configured: false } })
on('post', '/resumes', ({ data }) => {
  const u = me(); checkResume(data); S.resumes ||= []
  if (S.resumes.filter((x) => x.user_id === u.id).length >= RESUME_LIMIT) err(409, 'limit_reached', `You can keep up to ${RESUME_LIMIT} resumes. Delete one to create another.`)
  const x = { id: nextId('resumes'), user_id: u.id, title: data.title.trim(), target_role: data.target_role || null, template: data.template || 'classic', data: data.from_profile ? profilePrefill(u) : (data.data || {}), created_at: now(), updated_at: now() }
  S.resumes.push(x); return { resume: resumeDict(x) }
})
on('post', '/resumes/improve-bullet', () => err(503, 'ai_not_configured', 'Saathi AI needs the FormSaathi server with an AI key. This browser-only preview has no AI server — the ATS checks still work.'))
on('get', '/resumes/:id', ({ id }) => ({ resume: resumeDict(ownResume(id)), ai_configured: false }))
on('put', '/resumes/:id', ({ id, data }) => { const x = ownResume(id); checkResume(data); Object.assign(x, { title: data.title.trim(), target_role: data.target_role || null, template: data.template || 'classic', data: data.data || {}, updated_at: now() }); return { resume: resumeDict(x) } })
on('post', '/resumes/:id/duplicate', ({ id }) => {
  const src = ownResume(id), u = me()
  if (S.resumes.filter((x) => x.user_id === u.id).length >= RESUME_LIMIT) err(409, 'limit_reached', `You can keep up to ${RESUME_LIMIT} resumes. Delete one to create another.`)
  const x = { ...JSON.parse(JSON.stringify(src)), id: nextId('resumes'), title: `${src.title} (copy)`.slice(0, 120), created_at: now(), updated_at: now() }
  S.resumes.push(x); return { resume: resumeDict(x) }
})
on('delete', '/resumes/:id', ({ id }) => { const x = ownResume(id); S.resumes = S.resumes.filter((y) => y.id !== x.id); return { ok: true } })

// applications
const ownApp = (id) => S.applications.find((a) => a.id === Number(id) && a.user_id === me().id) || err(404, 'not_found', 'Application not found.')
on('get', '/applications', () => { const u = me(); return { items: S.applications.filter((a) => a.user_id === u.id).sort((a, b) => b.updated_at.localeCompare(a.updated_at)).map((a) => { const c = checklist(u.id, S.opportunities.find((o) => o.id === a.opportunity_id)); delete c.items; return { ...appDict(a), checklist: c } }) } })
on('post', '/applications', ({ data }) => {
  const u = me(), o = findOpp(data.opportunity_id)
  const existing = S.applications.find((a) => a.user_id === u.id && a.opportunity_id === o.id)
  if (existing) return { application: appDict(existing, true), created: false }
  const a = { id: nextId('applications'), user_id: u.id, opportunity_id: o.id, status: data.status || 'interested', applied_on: null, reference_number: null, created_at: now(), updated_at: now() }
  S.applications.push(a); S.history.push({ id: nextId('history'), application_id: a.id, from_status: null, to_status: a.status, note: 'Added to tracker', created_at: now() })
  return { application: appDict(a, true), created: true }
})
on('get', '/applications/:id', ({ id }) => {
  const a = ownApp(id)
  return { application: { ...appDict(a, true), checklist: checklist(a.user_id, S.opportunities.find((o) => o.id === a.opportunity_id)), reminders: S.reminders.filter((r) => r.application_id === a.id) } }
})
on('patch', '/applications/:id', ({ id, data }) => {
  const a = ownApp(id)
  if (data.applied_on) need(data.applied_on <= today(), 'applied_on', "Application date can't be in the future.")
  if (data.status && data.status !== a.status) { S.history.push({ id: nextId('history'), application_id: a.id, from_status: a.status, to_status: data.status, note: data.note || null, created_at: now() }); a.status = data.status }
  for (const k of ['applied_on', 'reference_number']) if (k in data) a[k] = data[k] || null
  a.updated_at = now()
  return { application: appDict(a, true) }
})
on('delete', '/applications/:id', ({ id }) => { const a = ownApp(id); S.applications = S.applications.filter((x) => x.id !== a.id); return { ok: true } })
on('post', '/applications/:id/notes', ({ id, data }) => { const a = ownApp(id); need((data.body || '').trim(), 'body', 'Write a note.'); const n = { id: nextId('notes'), application_id: a.id, body: data.body.trim(), created_at: now() }; S.notes.push(n); return { note: n } })
on('delete', '/applications/:id/notes/:nid', ({ id, nid }) => { ownApp(id); S.notes = S.notes.filter((n) => n.id !== Number(nid)); return { ok: true } })

// reminders & calendar
on('get', '/reminders', () => ({ items: S.reminders.filter((r) => r.user_id === me().id).sort((a, b) => a.remind_at.localeCompare(b.remind_at)) }))
on('post', '/reminders', ({ data }) => {
  const u = me(); need((data.title || '').trim(), 'title', 'Enter a title.'); need(data.remind_at, 'remind_at', 'Pick a date and time.')
  const r = { id: nextId('reminders'), user_id: u.id, title: data.title.trim(), remind_at: new Date(data.remind_at).toISOString(), channel: data.channel || 'in_app', application_id: data.application_id || null, opportunity_id: data.opportunity_id || null, sent_at: null, is_done: false }
  S.reminders.push(r); return { reminder: r, email_configured: false }
})
on('patch', '/reminders/:id', ({ id, data }) => { const r = S.reminders.find((x) => x.id === Number(id) && x.user_id === me().id) || err(404, 'not_found', 'Reminder not found.'); Object.assign(r, data); if (data.remind_at) { r.remind_at = new Date(data.remind_at).toISOString(); r.sent_at = null } return { reminder: r } })
on('delete', '/reminders/:id', ({ id }) => { const u = me(); S.reminders = S.reminders.filter((r) => !(r.id === Number(id) && r.user_id === u.id)); return { ok: true } })
on('get', '/calendar', ({ params }) => {
  const u = me(), start = params.start, end = params.end
  const [saved, apps] = ctx(u)
  const ids = new Set([...saved, ...Object.keys(apps).map(Number)])
  const events = []
  for (const o of S.opportunities.filter((x) => ids.has(x.id))) {
    if (o.deadline && o.deadline >= start && o.deadline <= end) events.push({ type: 'deadline', date: o.deadline, title: `Deadline: ${o.title}`, link: `/app/opportunities/${o.slug}`, tracked: !!apps[o.id] })
    for (const d of o.dates) if (d.date >= start && d.date <= end) events.push({ type: 'date', date: d.date, title: `${d.label}: ${o.title}`, link: `/app/opportunities/${o.slug}` })
  }
  for (const a of S.applications.filter((x) => x.user_id === u.id && x.applied_on && x.applied_on >= start && x.applied_on <= end)) events.push({ type: 'applied', date: a.applied_on, title: `Applied: ${S.opportunities.find((o) => o.id === a.opportunity_id).title}`, link: `/app/tracker/${a.id}` })
  for (const r of S.reminders.filter((x) => x.user_id === u.id)) { const d = ymd(new Date(r.remind_at)); if (d >= start && d <= end) events.push({ type: 'reminder', date: d, title: r.title, link: r.application_id ? `/app/tracker/${r.application_id}` : null, id: r.id, is_done: r.is_done, remind_at: r.remind_at }) }
  return { start, end, events: events.sort((a, b) => a.date.localeCompare(b.date)) }
})

// notifications
on('get', '/notifications', ({ params }) => {
  const u = me(); syncNotifications(u)
  let list = S.notifications.filter((n) => n.user_id === u.id).sort((a, b) => b.id - a.id)
  if (params?.unread === '1') list = list.filter((n) => !n.is_read)
  return { items: list.slice(0, Number(params?.limit) || 50), unread: S.notifications.filter((n) => n.user_id === u.id && !n.is_read).length }
})
on('post', '/notifications/read-all', () => { const u = me(); S.notifications.forEach((n) => { if (n.user_id === u.id) n.is_read = true }); return { ok: true } })
on('post', '/notifications/:id/read', ({ id }) => { const n = S.notifications.find((x) => x.id === Number(id) && x.user_id === me().id); if (n) n.is_read = true; return { ok: true } })
on('get', '/notifications/preferences', () => ({ preferences: S.prefs[me().id], email_configured: false }))
on('put', '/notifications/preferences', ({ data }) => { const p = S.prefs[me().id]; Object.assign(p, data); return { preferences: p, email_configured: false } })

// dashboard
on('get', '/dashboard', () => {
  const u = me(); syncNotifications(u)
  const [saved, apps] = ctx(u), mine = S.applications.filter((a) => a.user_id === u.id)
  const byStatus = Object.fromEntries(STATUSES.map((s) => [s, mine.filter((a) => a.status === s).length]))
  const watch = new Set([...saved, ...Object.keys(apps).map(Number)])
  const upcoming = S.opportunities.filter((o) => watch.has(o.id) && visible(o) && o.deadline && o.deadline >= today() && !['expired', 'archived'].includes(o.verification_status)).sort((a, b) => a.deadline.localeCompare(b.deadline)).slice(0, 5)
  const pending = []
  for (const a of mine.filter((x) => PRE_APPLY.includes(x.status))) {
    const o = S.opportunities.find((x) => x.id === a.opportunity_id)
    for (const i of checklist(u.id, o).items) if (i.is_mandatory && ['missing', 'expired'].includes(i.status)) pending.push({ application_id: a.id, opportunity_title: o.title, document_type: i.document_type, status: i.status })
  }
  const days = [...Array(7)].map((_, i) => addDays(i - 6))
  const stamps = [...S.saved.filter((s) => s.user_id === u.id).map((s) => s.created_at), ...S.history.filter((h) => mine.some((a) => a.id === h.application_id)).map((h) => h.created_at), ...activeDocs(u.id).map((d) => d.created_at)]
  const p = S.profiles[u.id]
  return {
    name: (p.full_name || '').split(' ')[0], profile_completion: completion(p),
    stats: { saved: saved.size, tracked: mine.length, applied: ['applied', 'under_review', 'approved', 'rejected'].reduce((n, s) => n + byStatus[s], 0), deadlines_this_week: upcoming.filter((o) => daysUntil(o.deadline) <= 7).length, documents: activeDocs(u.id).length, documents_missing: pending.length },
    recommended: recommend(u, 4),
    recent: S.opportunities.filter((o) => visible(o) && isOpen(o)).sort((a, b) => b.created_at.localeCompare(a.created_at)).slice(0, 4).map((o) => card(o, u)),
    saved: S.saved.filter((s) => s.user_id === u.id).sort((a, b) => b.id - a.id).slice(0, 4).map((s) => card(S.opportunities.find((o) => o.id === s.opportunity_id), u)),
    upcoming_deadlines: upcoming.map((o) => card(o, u)), applications_by_status: byStatus, pending_documents: pending.slice(0, 8),
    notifications: S.notifications.filter((n) => n.user_id === u.id && !n.is_read).sort((a, b) => b.id - a.id).slice(0, 5),
    weekly_activity: days.map((d) => ({ date: d, count: stamps.filter((s) => ymd(new Date(s)) === d).length })),
    announcements: S.announcements.filter((a) => a.is_active && a.audience !== 'admins').slice(-2),
  }
})

// admin
on('get', '/admin/stats', () => {
  admin()
  const by = (list, f) => list.reduce((m, x) => ((m[x[f]] = (m[x[f]] || 0) + 1), m), {})
  const top = Object.entries(by(S.saved, 'opportunity_id')).sort((a, b) => b[1] - a[1]).slice(0, 5).map(([id, count]) => ({ title: S.opportunities.find((o) => o.id === Number(id))?.title, count }))
  return { users: { total: S.users.length, new_7d: S.users.filter((u) => u.created_at >= addDays(-7)).length, admins: S.users.filter((u) => u.role === 'admin').length },
    opportunities: { total: S.opportunities.length, published: S.opportunities.filter((o) => o.publication_status === 'published').length, by_verification: by(S.opportunities, 'verification_status'), stale_verification: 0, demo: S.opportunities.filter((o) => o.data_origin === 'demo').length },
    applications: { total: S.applications.length, by_status: by(S.applications, 'status') }, saved: S.saved.length, documents: S.documents.filter((d) => !d.deleted_at).length,
    ai_messages: 0, open_corrections: S.corrections.filter((c) => c.status === 'open').length, new_feedback: S.feedback.filter((f) => f.status === 'new').length, top_saved: top }
})
on('get', '/admin/opportunities', ({ params }) => {
  admin()
  let list = [...S.opportunities]
  if (params.q) list = list.filter((o) => o.title.toLowerCase().includes(params.q.toLowerCase()))
  for (const f of ['verification_status', 'publication_status', 'data_origin']) if (params[f]) list = list.filter((o) => o[f] === params[f])
  list.sort((a, b) => b.updated_at.localeCompare(a.updated_at))
  return paginate(list.map((o) => card(o, null)), params, 20)
})
const adminOpp = (id) => S.opportunities.find((o) => o.id === Number(id)) || err(404, 'not_found', 'Opportunity not found.')
const log = (o, action, from, to, notes) => S.logs.push({ id: nextId('logs'), opportunity_id: o.id, action, from_status: from, to_status: to, notes: notes || null, actor: me().email, created_at: now() })
on('get', '/admin/opportunities/:id', ({ id }) => { admin(); const o = adminOpp(id); return { opportunity: { ...detail(o, null), logs: S.logs.filter((l) => l.opportunity_id === o.id).sort((a, b) => b.id - a.id) } } })
function applyOpp(o, d) {
  const required = { title: 'Enter a title.', summary: 'Enter a summary.', description: 'Enter a description.', eligibility_summary: 'Enter an eligibility summary.', benefits: 'Describe the benefits.', source_url: 'Official source URL is required.' }
  for (const [k, m] of Object.entries(required)) need((d[k] || '').toString().trim(), k, m)
  need(/^https?:\/\//.test(d.source_url), 'source_url', 'Enter a valid http(s) URL.')
  need(d.deadline || d.is_rolling, 'deadline', 'Enter a deadline or mark it as rolling.')
  need(d.organization_id || (d.organization_name || '').trim(), 'organization_id', 'Choose an organisation or enter a new one.')
  let orgId = d.organization_id
  if (!orgId) { const name = d.organization_name.trim(); orgId = S.orgs.find((g) => g.name === name)?.id; if (!orgId) { orgId = nextId('orgs'); S.orgs.push({ id: orgId, name, org_type: d.organization_type || 'other', website: null }) } }
  const slug = d.slug || d.title.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '').slice(0, 150)
  if (S.opportunities.some((x) => x.slug === slug && x.id !== o.id)) err(409, 'duplicate', 'Another opportunity already uses this URL slug.', { slug: 'Already used.' })
  const crit = (d.criteria || []).map((c, i) => ({ id: nextId('criteria'), ...c, sort_order: i }))
  Object.assign(o, { ...d, slug, organization_id: orgId, criteria: crit, required_documents: d.required_documents || [], dates: (d.dates || []).map((x) => ({ label: x.label, date: x.date, note: x.note || null })),
    states: [...new Set(crit.filter((c) => c.criterion_type === 'state_domicile').flatMap((c) => c.value.any_of || []))],
    education_levels: [...new Set(crit.filter((c) => c.criterion_type === 'education_level').flatMap((c) => c.value.any_of || []))],
    income_ceiling: crit.filter((c) => c.criterion_type === 'income_max').map((c) => c.value.amount).sort((a, b) => a - b)[0] ?? null, updated_at: now() })
  delete o.organization_name; delete o.organization_type
}
on('post', '/admin/opportunities', ({ data }) => {
  admin()
  const o = { id: nextId('opportunities'), verification_status: 'pending_verification', publication_status: 'draft', last_verified_at: null, featured_rank: null, created_at: now(), data_origin: 'official' }
  applyOpp(o, data); S.opportunities.push(o); log(o, 'marked_pending', null, 'pending_verification', 'Created')
  return { opportunity: detail(o, null) }
})
on('put', '/admin/opportunities/:id', ({ id, data }) => { admin(); const o = adminOpp(id); applyOpp(o, data); return { opportunity: detail(o, null) } })
on('post', '/admin/opportunities/:id/status', ({ id, data }) => {
  admin(); const o = adminOpp(id), before = o.verification_status
  switch (data.action) {
    case 'verify': if (o.data_origin === 'demo') err(409, 'demo_not_verifiable', "Demo data can't be marked as verified."); Object.assign(o, { verification_status: 'verified', last_verified_at: now() }); log(o, 'verified', before, 'verified', data.notes); break
    case 'mark_pending': o.verification_status = 'pending_verification'; log(o, 'marked_pending', before, 'pending_verification', data.notes); break
    case 'expire': o.verification_status = 'expired'; log(o, 'marked_expired', before, 'expired', data.notes); break
    case 'archive': Object.assign(o, { verification_status: 'archived', publication_status: 'unpublished' }); log(o, 'archived', before, 'archived', data.notes); break
    case 'publish': if (o.data_origin === 'official' && o.verification_status !== 'verified') err(409, 'needs_verification', 'Verify the official source before publishing.'); o.publication_status = 'published'; log(o, 'published', before, before, data.notes); break
    case 'unpublish': o.publication_status = 'unpublished'; log(o, 'unpublished', before, before, data.notes); break
  }
  o.updated_at = now()
  return { opportunity: card(o, null) }
})
on('delete', '/admin/opportunities/:id', ({ id }) => {
  admin(); const o = adminOpp(id)
  if (S.saved.some((s) => s.opportunity_id === o.id) || S.applications.some((a) => a.opportunity_id === o.id)) err(409, 'in_use', 'Users have saved or tracked this opportunity. Archive it instead of deleting.')
  S.opportunities = S.opportunities.filter((x) => x.id !== o.id); return { ok: true }
})
on('put', '/admin/featured', ({ data }) => { admin(); S.opportunities.forEach((o) => { const r = data.ids.indexOf(o.id); o.is_featured = r >= 0; o.featured_rank = r >= 0 ? r + 1 : null }); return { ok: true } })
on('get', '/admin/organizations', () => { admin(); return { items: [...S.orgs].sort((a, b) => a.name.localeCompare(b.name)) } })
on('get', '/admin/categories', () => { admin(); return { items: S.categories.map((c) => ({ ...c, count: S.opportunities.filter((o) => o.category_id === c.id).length })) } })
on('post', '/admin/categories', ({ data }) => { admin(); need(/^[a-z0-9-]{2,60}$/.test(data.slug || ''), 'slug', 'Use lowercase letters, numbers and dashes.'); if (S.categories.some((c) => c.slug === data.slug || c.name === data.name)) err(409, 'duplicate', 'A category with this name or slug exists.'); const c = { id: nextId('categories'), icon: 'sparkles', color: 'lavender', sort_order: S.categories.length, is_active: true, ...data }; S.categories.push(c); return { category: c } })
on('put', '/admin/categories/:id', ({ id, data }) => { admin(); const c = S.categories.find((x) => x.id === Number(id)) || err(404, 'not_found', 'Category not found.'); Object.assign(c, data); return { category: c } })
on('delete', '/admin/categories/:id', ({ id }) => { admin(); if (S.opportunities.some((o) => o.category_id === Number(id))) err(409, 'in_use', 'This category has opportunities. Deactivate it instead.'); S.categories = S.categories.filter((c) => c.id !== Number(id)); return { ok: true } })
on('get', '/admin/users', ({ params }) => { admin(); let list = [...S.users]; if (params.q) list = list.filter((u) => u.email.includes(params.q.toLowerCase())); if (params.role) list = list.filter((u) => u.role === params.role); return paginate(list.reverse().map((u) => ({ id: u.id, email: u.email, role: u.role, is_active: u.is_active, full_name: S.profiles[u.id]?.full_name, created_at: u.created_at, last_login_at: u.last_login_at, onboarding_completed: !!S.profiles[u.id]?.onboarding_completed_at })), params, 20) })
on('patch', '/admin/users/:id', ({ id, data }) => { const a = admin(); const u = userById(Number(id)) || err(404, 'not_found', 'User not found.'); if (u.id === a.id && (data.role === 'user' || data.is_active === false)) err(409, 'self_change', "You can't demote or deactivate your own account."); Object.assign(u, data); return { ok: true } })
const corrDict = (c) => { const o = S.opportunities.find((x) => x.id === c.opportunity_id); return { ...c, opportunity: { id: o.id, slug: o.slug, title: o.title } } }
on('get', '/admin/corrections', ({ params }) => { admin(); return paginate(S.corrections.filter((c) => !params.status || c.status === params.status).reverse().map(corrDict), params, 20) })
on('patch', '/admin/corrections/:id', ({ id, data }) => {
  admin(); const c = S.corrections.find((x) => x.id === Number(id)) || err(404, 'not_found', 'Correction not found.')
  Object.assign(c, { status: data.status, admin_note: data.admin_note || null, reviewed_at: now() })
  if (c.user_id && data.status !== 'open') { const o = S.opportunities.find((x) => x.id === c.opportunity_id); push(c.user_id, 'correction_update', `Your correction for ${o.title} was ${data.status === 'accepted' ? 'accepted — thank you!' : 'reviewed'}`, data.admin_note || null, `/app/opportunities/${o.slug}`, `correction:${c.id}:${data.status}`) }
  return { correction: corrDict(c) }
})
on('get', '/admin/feedback', ({ params }) => { admin(); return paginate([...S.feedback].reverse(), params, 20) })
on('patch', '/admin/feedback/:id', ({ id, data }) => { admin(); const f = S.feedback.find((x) => x.id === Number(id)); if (f) f.status = data.status; return { ok: true } })
on('get', '/admin/announcements', () => { admin(); return { items: [...S.announcements].reverse() } })
on('post', '/admin/announcements', ({ data }) => { admin(); need((data.title || '').trim().length >= 3, 'title', 'Enter a title.'); need((data.body || '').trim().length >= 3, 'body', 'Enter a message.'); const a = { id: nextId('announcements'), audience: 'all', level: 'info', is_active: true, created_at: now(), ...data }; S.announcements.push(a); return { announcement: a } })
on('put', '/admin/announcements/:id', ({ id, data }) => { admin(); const a = S.announcements.find((x) => x.id === Number(id)) || err(404, 'not_found', 'Announcement not found.'); Object.assign(a, data); return { announcement: a } })
on('delete', '/admin/announcements/:id', ({ id }) => { admin(); S.announcements = S.announcements.filter((a) => a.id !== Number(id)); return { ok: true } })

// ------------------------------------------------------------------ entry point
export async function handle(method, url, { params = {}, data = {}, raw } = {}) {
  await init()
  await new Promise((r) => setTimeout(r, 120)) // small delay so loading states are visible, like a real network
  const path = url.split('?')[0]
  for (const [m, re, fn] of routes) {
    const match = m === method && path.match(re)
    if (match) {
      const result = await fn({ ...(match.groups || {}), params: params || {}, data: data || {}, raw })
      save()
      return result
    }
  }
  err(404, 'not_found', 'Endpoint not found.')
}

/** Synchronous variant for saves while the page closes (no artificial delay; sync routes only). */
export function handleSync(method, url, { params = {}, data = {} } = {}) {
  if (!load()) return
  const path = url.split('?')[0]
  for (const [m, re, fn] of routes) {
    const match = m === method && path.match(re)
    if (match) {
      try {
        const result = fn({ ...(match.groups || {}), params, data })
        if (!(result instanceof Promise)) save()
        return result
      } catch { return undefined }
    }
  }
}

export function resetPreview() { localStorage.removeItem(KEY); S = null; indexedDB.deleteDatabase('formsaathi-preview') }
