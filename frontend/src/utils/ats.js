// ATS readiness checks and job-keyword matching for the resume builder.
// Deterministic and transparent: every check says what it looked at and why it matters.
// There is no hidden "ATS score" — real applicant tracking systems differ, so we report
// concrete, checkable signals that recruiters and ATS parsers commonly rely on.

export const ACTION_VERBS = new Set(`accelerated achieved analysed analyzed architected assessed audited authored automated balanced
benchmarked boosted built calculated championed classified coached collaborated compiled completed composed configured consolidated
constructed containerized contributed converted coordinated created cut debugged decreased defined delivered deployed designed
detected developed devised diagnosed directed documented drove eliminated enabled engineered enhanced established evaluated executed
expanded extracted facilitated finalized forecasted formulated founded generated grew guided handled identified implemented improved
increased initiated innovated instrumented integrated introduced investigated launched led leveraged maintained managed mapped
mentored merged migrated minimized modeled modelled monitored negotiated optimized orchestrated organized organised outperformed
overhauled owned partnered piloted planned predicted presented prioritized processed produced programmed prototyped published raised
ranked re-architected rebuilt recommended redesigned reduced refactored resolved restructured revamped scaled scheduled scoped
secured shipped simplified solved spearheaded standardized streamlined strengthened structured supervised supported surfaced
synthesized taught tested tracked trained transformed translated troubleshot tuned unified upgraded validated visualized won wrote`
  .split(/\s+/).filter(Boolean))

const WEAK_STARTS = ['responsible for', 'worked on', 'helped', 'assisted', 'involved in', 'participated in', 'tasked with', 'duties included', 'in charge of']
const FIRST_PERSON = /\b(i|me|my|mine|myself)\b/i
const NUMBER = /(\d|%|₹|\$|\blakh\b|\bcrore\b|\bk\b)/i

const STOPWORDS = new Set(`a about above after again against all also am an and any are as at be because been before being below between both
but by can could did do does doing down during each etc few for from further had has have having he her here hers him his how i if in
into is it its itself just like may me might more most must my no nor not now of off on once only or other our ours out over own per
same she should so some such than that the their theirs them then there these they this those through to too under until up upon us
very via was we were what when where which while who whom why will with within without would you your yours
able across along among apply applicant applicants application applications candidate candidates complete completed course courses
current currently date day days details different eligible eligibility ensure etc every excellent experience following full give good
great high including including ideal india indian join knowledge least level looking make member members minimum month months must
need needed new number one opportunity opportunities part please preferred program programme programmes provide related relevant
required requirement requirements responsibilities role roles scheme selected selection should skills strong student students
support team time two under using well work working year years
january february march april may june july august september october november december jan feb mar apr jun jul aug sep sept oct nov dec
summer winter monsoon season period periods duration discretion stipend stipends placement placements internship internships intern
interns trainee trainees fellowship fellowships scholarship scholarships accommodation arrange arrangement outstation citizen citizens
city cities studying study penultimate integrated reserve receipt previous next start starting starts begin begins online offline
form forms portal deadline last open opens opened round phase notification notice official website government ministry department
monthly annual annually lakh lakhs crore rupees rs amount family income age below above upto equivalent recognised recognized
institution institutions university universities college colleges degree degrees programme program details information
bank's india's s`.split(/\s+/).filter(Boolean))

// Short terms that matter despite being under 3 letters.
const SHORT_TERMS = new Set(['ai', 'ml', 'ui', 'ux', 'qa', 'go', 'r', 'c', 'bi', 'hr', 'pr', 'ca', 'cs', 'it'])
// Multi-word terms we keep as one keyword when they appear in the job text.
const PHRASES = ['machine learning', 'deep learning', 'data science', 'data analysis', 'data analytics', 'data structures',
  'computer science', 'natural language processing', 'computer vision', 'power bi', 'google analytics', 'project management',
  'product management', 'public policy', 'financial modelling', 'financial modeling', 'risk management', 'supply chain',
  'customer service', 'digital marketing', 'content writing', 'social media', 'rest api', 'rest apis', 'web development',
  'full stack', 'full-stack', 'react native', 'spring boot', 'node.js', 'next.js', 'vue.js', 'ms excel', 'microsoft excel',
  'problem solving', 'communication skills', 'research methodology', 'statistical analysis', 'version control', 'unit testing',
  'cloud computing', 'big data', 'business analysis', 'market research', 'policy research', 'field work']

const clean = (s) => (s || '').toString().trim()
const words = (s) => clean(s).split(/\s+/).filter(Boolean)

export function allBullets(data) {
  const out = []
  ;(data.experience || []).forEach((e, i) => (e.bullets || []).forEach((b, j) => clean(b) && out.push({ section: 'experience', i, j, text: clean(b) })))
  ;(data.projects || []).forEach((p, i) => (p.bullets || []).forEach((b, j) => clean(b) && out.push({ section: 'projects', i, j, text: clean(b) })))
  return out
}

export function startsWithActionVerb(text) {
  const first = clean(text).toLowerCase().replace(/^[^a-z]+/, '').split(/[\s,;:]+/)[0] || ''
  return ACTION_VERBS.has(first)
}

export function bulletIssues(text) {
  const t = clean(text), lower = t.toLowerCase(), issues = []
  if (WEAK_STARTS.some((w) => lower.startsWith(w))) issues.push({ code: 'weak_start', label: 'Starts with a weak phrase — begin with an action verb (Built, Led, Reduced…)' })
  else if (!startsWithActionVerb(t)) issues.push({ code: 'no_verb', label: 'Start with a past-tense action verb' })
  if (!NUMBER.test(t)) issues.push({ code: 'no_number', label: 'Add a number if you have one (users, %, time saved, rank)' })
  const n = words(t).length
  if (n > 35) issues.push({ code: 'too_long', label: `Long (${n} words) — aim for under 30` })
  if (n < 5) issues.push({ code: 'too_short', label: 'Too short — say what you did and the result' })
  if (FIRST_PERSON.test(t)) issues.push({ code: 'first_person', label: 'Avoid “I / my” on a resume' })
  return issues
}

/** Plain-text version of the resume, in reading order. Used for word counts, keyword matching and .txt export. */
export function resumeText(d) {
  const b = d.basics || {}
  const lines = [clean(b.name), clean(b.headline), [b.email, b.phone, b.location].map(clean).filter(Boolean).join(' | '),
    (b.links || []).map((l) => [clean(l.label), clean(l.url)].filter(Boolean).join(': ')).filter(Boolean).join(' | ')]
  const section = (title, body) => { if (body.filter(Boolean).length) lines.push('', title.toUpperCase(), ...body) }
  section('Summary', [clean(d.summary)])
  section('Experience', (d.experience || []).flatMap((e) => [
    [clean(e.role), clean(e.org)].filter(Boolean).join(' — ') + (clean(e.start) || clean(e.end) ? ` (${[clean(e.start), clean(e.end)].filter(Boolean).join(' – ')})` : '') + (clean(e.location) ? `, ${clean(e.location)}` : ''),
    ...(e.bullets || []).map(clean).filter(Boolean).map((x) => `• ${x}`)]))
  section('Projects', (d.projects || []).flatMap((p) => [
    [clean(p.name), clean(p.tech)].filter(Boolean).join(' | ') + (clean(p.link) ? ` (${clean(p.link)})` : ''),
    ...(p.bullets || []).map(clean).filter(Boolean).map((x) => `• ${x}`)]))
  section('Education', (d.education || []).flatMap((e) => [
    [clean(e.school), clean(e.degree)].filter(Boolean).join(' — ') + (clean(e.start) || clean(e.end) ? ` (${[clean(e.start), clean(e.end)].filter(Boolean).join(' – ')})` : ''),
    clean(e.score), clean(e.details)].filter(Boolean)))
  section('Skills', (d.skills || []).map((s) => [clean(s.group), clean(s.items)].filter(Boolean).join(': ')))
  section('Achievements', (d.achievements || []).map(clean).filter(Boolean).map((x) => `• ${x}`))
  section('Certifications', (d.certifications || []).map(clean).filter(Boolean).map((x) => `• ${x}`))
  return lines.filter((l, i, a) => !(l === '' && a[i - 1] === '')).join('\n').trim()
}

export function skillCount(d) {
  return (d.skills || []).flatMap((s) => clean(s.items).split(/[,;|]/)).map(clean).filter(Boolean).length
}

/** Run all readiness checks. status: pass | warn | fail. */
export function analyze(d) {
  const b = d.basics || {}
  const bullets = allBullets(d)
  const text = resumeText(d)
  const totalWords = words(text).length
  const verbShare = bullets.length ? bullets.filter((x) => startsWithActionVerb(x.text)).length / bullets.length : 0
  const numShare = bullets.length ? bullets.filter((x) => NUMBER.test(x.text)).length / bullets.length : 0
  const longOnes = bullets.filter((x) => words(x.text).length > 35).length
  const summaryWords = words(d.summary).length
  const entries = [...(d.experience || []).map((e) => ({ name: e.role || e.org, bullets: (e.bullets || []).filter((x) => clean(x)).length })),
    ...(d.projects || []).map((p) => ({ name: p.name, bullets: (p.bullets || []).filter((x) => clean(x)).length }))]
  const thinEntries = entries.filter((e) => e.bullets < 2 || e.bullets > 5)
  const skills = skillCount(d)
  const missingDates = [...(d.experience || []), ...(d.education || [])].filter((e) => !clean(e.start) && !clean(e.end)).length
  const firstPerson = FIRST_PERSON.test([d.summary, ...bullets.map((x) => x.text)].join(' '))
  const emailOk = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(clean(b.email))
  const pct = (x) => `${Math.round(x * 100)}%`

  const checks = [
    { id: 'contact', label: 'Name and email', status: clean(b.name) && emailOk ? 'pass' : 'fail',
      detail: clean(b.name) && emailOk ? 'Recruiters can reach you.' : 'Add your full name and a valid email address.' },
    { id: 'phone', label: 'Phone number', status: clean(b.phone) ? 'pass' : 'warn', detail: clean(b.phone) ? 'Included.' : 'Most Indian recruiters call first — add a phone number.' },
    { id: 'links', label: 'Profile links', status: (b.links || []).some((l) => clean(l.url)) ? 'pass' : 'warn',
      detail: (b.links || []).some((l) => clean(l.url)) ? 'LinkedIn / GitHub / portfolio included.' : 'Add LinkedIn, GitHub or a portfolio link.' },
    { id: 'summary', label: 'Professional summary', status: summaryWords >= 20 && summaryWords <= 80 ? 'pass' : 'warn',
      detail: !summaryWords ? 'Add 2–3 lines on who you are and what you build.' : summaryWords > 80 ? `${summaryWords} words — keep it under 80.` : summaryWords < 20 ? `${summaryWords} words — a little short; aim for 20–80.` : `${summaryWords} words.` },
    { id: 'experience', label: 'Experience or projects', status: entries.length ? 'pass' : 'fail',
      detail: entries.length ? `${entries.length} entr${entries.length === 1 ? 'y' : 'ies'}.` : 'Add at least one internship, job or project.' },
    { id: 'bullets_per_entry', label: '2–5 bullets per entry', status: !entries.length ? 'warn' : thinEntries.length ? 'warn' : 'pass',
      detail: thinEntries.length ? `Check: ${thinEntries.map((e) => e.name || 'untitled').slice(0, 3).join(', ')}.` : 'Each entry has a healthy number of bullets.' },
    { id: 'action_verbs', label: 'Bullets start with action verbs', status: !bullets.length ? 'warn' : verbShare >= 0.7 ? 'pass' : verbShare >= 0.4 ? 'warn' : 'fail',
      detail: bullets.length ? `${pct(verbShare)} of bullets (aim for 70%+).` : 'No bullets yet.' },
    { id: 'quantified', label: 'Results are quantified', status: !bullets.length ? 'warn' : numShare >= 0.4 ? 'pass' : numShare >= 0.2 ? 'warn' : 'fail',
      detail: bullets.length ? `${pct(numShare)} of bullets have a number (aim for 40%+). Only use real numbers.` : 'No bullets yet.' },
    { id: 'bullet_length', label: 'Bullets are concise', status: longOnes ? 'warn' : 'pass', detail: longOnes ? `${longOnes} bullet(s) over 35 words.` : 'All bullets under 35 words.' },
    { id: 'education', label: 'Education', status: (d.education || []).some((e) => clean(e.school)) ? 'pass' : 'fail',
      detail: (d.education || []).some((e) => clean(e.school)) ? 'Included.' : 'Add your college or school.' },
    { id: 'skills', label: 'Skills section', status: skills >= 6 ? 'pass' : skills ? 'warn' : 'fail',
      detail: skills ? `${skills} skills listed${skills < 6 ? ' — add the tools you actually use (aim for 6+).' : '.'}` : 'ATS systems match skills by keyword — add your skills.' },
    { id: 'dates', label: 'Dates on experience and education', status: missingDates ? 'warn' : 'pass', detail: missingDates ? `${missingDates} entr${missingDates === 1 ? 'y has' : 'ies have'} no dates.` : 'All entries dated.' },
    { id: 'first_person', label: 'No “I / my”', status: firstPerson ? 'warn' : 'pass', detail: firstPerson ? 'Write in resume style without first person.' : 'Resume style throughout.' },
    { id: 'length', label: 'Length fits one page', status: totalWords > 850 ? 'warn' : totalWords < 180 ? 'warn' : 'pass',
      detail: totalWords > 850 ? `${totalWords} words — likely more than one page for a student resume.` : totalWords < 180 ? `${totalWords} words — add more detail.` : `${totalWords} words.` },
    { id: 'format', label: 'ATS-safe layout', status: 'pass', detail: 'Single column, standard headings, real selectable text — no tables, images or icons.' },
  ]
  const tips = bullets.map((x) => ({ ...x, issues: bulletIssues(x.text) })).filter((x) => x.issues.length)
  return { checks, passed: checks.filter((c) => c.status === 'pass').length, total: checks.length, tips,
    stats: { words: totalWords, bullets: bullets.length, skills } }
}

/** Important words and phrases from a job description or opportunity, most frequent first. */
export function extractKeywords(jobText, limit = 25) {
  const text = ` ${clean(jobText).toLowerCase().replace(/[“”"'’()[\]{}<>]/g, ' ')} `
  const counts = new Map()
  const bump = (k, n = 1) => counts.set(k, (counts.get(k) || 0) + n)
  for (const ph of PHRASES) {
    const n = text.split(ph).length - 1
    if (n) bump(ph, n * 2)
  }
  const stripped = PHRASES.reduce((t, ph) => t.split(ph).join(' '), text)
  for (const raw of stripped.split(/[\s,;:/!?|•·–—]+/)) {
    const w = raw.replace(/^[^a-z0-9+#]+|[^a-z0-9+#]+$/g, '')
    if (!w || /^\d/.test(w) || STOPWORDS.has(w)) continue
    if (w.length < 3 && !SHORT_TERMS.has(w)) continue
    bump(w)
  }
  return [...counts.entries()].sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0])).slice(0, limit).map(([k]) => k)
}

export function containsKeyword(haystackLower, kw) {
  const escaped = kw.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
  return new RegExp(`(^|[^a-z0-9])${escaped}($|[^a-z0-9])`, 'i').test(haystackLower)
}

export function matchKeywords(d, jobText) {
  const keywords = extractKeywords(jobText)
  const hay = resumeText(d).toLowerCase()
  const matched = keywords.filter((k) => containsKeyword(hay, k))
  const missing = keywords.filter((k) => !matched.includes(k))
  return { keywords, matched, missing, percent: keywords.length ? Math.round((matched.length / keywords.length) * 100) : 0 }
}

export function opportunityText(o) {
  return [o.title, o.summary, o.eligibility_summary, o.description, o.benefits, ...(o.criteria || []).map((c) => c.description)].filter(Boolean).join('\n')
}

export function emptyResume() {
  return { basics: { name: '', headline: '', email: '', phone: '', location: '', links: [] }, summary: '', experience: [], projects: [], education: [], skills: [], achievements: [], certifications: [] }
}
