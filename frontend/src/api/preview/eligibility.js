// Browser mirror of backend/app/services/eligibility.py (used only by the preview build).
// Keep the two in sync; backend tests cover the Python version, src/api/preview/eligibility.test.js this one.
export const INCOME_BANDS = {
  below_1l: [0, 100000], '1l_to_2_5l': [100000, 250000], '2_5l_to_5l': [250000, 500000],
  '5l_to_8l': [500000, 800000], above_8l: [800000, null],
}
const LABELS = {
  class_10: 'Class 10', class_12: 'Class 12', diploma: 'Diploma', iti: 'ITI', undergraduate: 'Undergraduate',
  postgraduate: 'Postgraduate', doctorate: 'Doctorate', not_studying: 'Not currently studying', other: 'Other',
  general: 'General', ews: 'EWS', obc: 'OBC', sc: 'SC', st: 'ST', female: 'Female', male: 'Male',
}
const label = (v) => LABELS[v] || v.replace(/_/g, ' ')
const titleCase = (s) => s.replace(/-/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase())

export function ageOn(dob, on = new Date()) {
  if (!dob) return null
  const d = new Date(dob)
  let age = on.getFullYear() - d.getFullYear()
  if (on.getMonth() < d.getMonth() || (on.getMonth() === d.getMonth() && on.getDate() < d.getDate())) age--
  return age
}

export function check(type, value = {}, p = {}) {
  if (type === 'age_min' || type === 'age_max') {
    const age = ageOn(p.date_of_birth, value.as_on ? new Date(value.as_on) : new Date())
    if (age === null) return ['unknown', 'Add your date of birth so we can check the age limit.', 'date_of_birth']
    const ok = type === 'age_min' ? age >= value.years : age <= value.years
    return [ok ? 'met' : 'not_met', `You are ${age}; the rule requires ${type === 'age_min' ? 'at least' : 'at most'} ${value.years}.`, null]
  }
  if (type === 'education_level') {
    const allowed = value.any_of || []
    if (!p.education_level) return ['unknown', 'Add your education level to check this.', 'education_level']
    if (allowed.includes(p.education_level)) return ['met', `Your education level (${label(p.education_level)}) is accepted.`, null]
    return ['not_met', `Accepted levels: ${allowed.map(label).join(', ')}. Yours: ${label(p.education_level)}.`, null]
  }
  if (type === 'course') {
    const course = [p.course, p.stream].filter(Boolean).join(' ').toLowerCase()
    if (!course.trim()) return ['unknown', 'Add your course and stream to check this.', 'course']
    if ((value.any_of || []).some((k) => course.includes(k.toLowerCase()))) return ['met', 'Your course matches the required field.', null]
    return ['needs_review', "We couldn't match your course name automatically. Check the official list of eligible courses.", null]
  }
  if (type === 'year_of_study') {
    if (p.current_year == null) return ['unknown', 'Add your current year of study.', 'current_year']
    const lo = value.min ?? 1, hi = value.max ?? 10
    return [p.current_year >= lo && p.current_year <= hi ? 'met' : 'not_met', `You are in year ${p.current_year}; accepted: year ${lo} to ${hi}.`, null]
  }
  if (type === 'marks_min_percentage' || type === 'marks_min_cgpa') {
    const want = type === 'marks_min_percentage' ? 'percentage' : 'cgpa'
    const unit = want === 'percentage' ? '%' : ' CGPA'
    if (p.marks_value == null || !p.marks_type) return ['unknown', 'Add your latest marks or CGPA.', 'marks_value']
    if (p.marks_type !== want) return ['needs_review', `The rule uses ${want} (minimum ${value.value}${unit}) but your profile has ${p.marks_type}. Conversion formulas differ by university, so please check with your institution.`, null]
    return [Number(p.marks_value) >= Number(value.value) ? 'met' : 'not_met', `Your score is ${p.marks_value}${unit}; minimum required is ${value.value}${unit}.`, null]
  }
  if (type === 'income_max') {
    const limit = `Rs ${Number(value.amount).toLocaleString('en-IN')}`
    if (!p.income_range || p.income_range === 'prefer_not_say') return ['unknown', `This needs family income up to ${limit}/year. Add your income range (optional) to check.`, 'income_range']
    const [lower, upper] = INCOME_BANDS[p.income_range]
    if (upper !== null && upper <= value.amount) return ['met', `Your family income band is within the ${limit} limit.`, null]
    if (lower > value.amount) return ['not_met', `Your income band is above the ${limit} limit.`, null]
    return ['unknown', `Your income band crosses the ${limit} limit; your exact income certificate decides.`, null]
  }
  if (type === 'state_domicile') {
    const allowed = value.any_of || []
    if (!p.state_code) return ['unknown', 'Add your state to check the residence rule.', 'state_code']
    if (allowed.includes(p.state_code)) return ['met', "Your state is eligible. You'll need a domicile certificate as proof.", null]
    return ['not_met', `This is only for residents of: ${allowed.map(titleCase).join(', ')}.`, null]
  }
  if (type === 'social_category' || type === 'gender') {
    const field = type, allowed = value.any_of || []
    const names = allowed.map(label).join(', ')
    if (!p[field] || p[field] === 'prefer_not_say') return ['unknown', `Open to: ${names}. Add your ${type === 'gender' ? 'gender' : 'category'} (optional) to check.`, field]
    if (allowed.includes(p[field])) return ['met', type === 'gender' ? 'Matches the gender criterion.' : `Your category (${label(p[field])}) is eligible.`, null]
    return ['not_met', `Open only to: ${names}.`, null]
  }
  if (type === 'disability') {
    if (p.has_disability == null) return ['unknown', 'This is for persons with disabilities. Update your profile (optional) to check.', 'has_disability']
    return p.has_disability ? ['met', 'Matches the disability criterion.', null] : ['not_met', 'Only for persons with disabilities.', null]
  }
  return ['needs_review', "This rule can't be checked automatically. Read it carefully and confirm it applies to you.", null]
}

export function evaluate(profile, criteria) {
  const results = criteria.map((c) => {
    const [outcome, reason, missing] = profile ? check(c.criterion_type, c.value, profile) : ['unknown', 'Complete your profile to check this.', null]
    return { criterion_id: c.id, criterion_type: c.criterion_type, description: c.description, source_excerpt: c.source_excerpt || null, is_mandatory: c.is_mandatory !== false, outcome, reason, missing_field: missing }
  })
  const mandatory = results.filter((r) => r.is_mandatory)
  let verdict = 'eligible'
  if (mandatory.some((r) => r.outcome === 'not_met')) verdict = 'not_eligible'
  else if (mandatory.some((r) => r.outcome === 'unknown' || r.outcome === 'needs_review')) verdict = 'possibly_eligible'
  const counts = { met: 0, not_met: 0, unknown: 0, needs_review: 0 }
  results.forEach((r) => counts[r.outcome]++)
  return { verdict, counts, results, missing_fields: [...new Set(results.map((r) => r.missing_field).filter(Boolean))].sort() }
}

export function templateExplanation(report, title) {
  const c = report.counts
  if (report.verdict === 'eligible') {
    return { summary: `Based on your profile, you meet all ${c.met} checkable rules for ${title}.`, next_steps: ['Gather the required documents.', 'Read the official notification once before applying.', 'Apply on the official portal before the deadline.'] }
  }
  if (report.verdict === 'possibly_eligible') {
    const steps = []
    if (report.missing_fields.length) steps.push('Complete the missing profile details highlighted below.')
    if (c.needs_review) steps.push("Read the rules marked 'Needs your review' in the official notification.")
    steps.push('Re-run this check after updating your profile.')
    return { summary: `You may be eligible for ${title}. ${c.met} rule(s) match, and ${c.unknown + c.needs_review} need more information or your review.`, next_steps: steps }
  }
  return { summary: `Based on your profile, you do not meet ${c.not_met} required rule(s) for ${title}.`, next_steps: ['Check the reasons below. If your profile is out of date, update it and check again.', 'Explore similar opportunities that match your profile.'] }
}
