import { describe, expect, it } from 'vitest'
import { analyze, bulletIssues, extractKeywords, matchKeywords, resumeText, startsWithActionVerb } from './ats.js'

const good = {
  basics: { name: 'Asha Patil', email: 'asha@example.com', phone: '+91 90000 00000', location: 'Pune', links: [{ label: 'GitHub', url: 'https://github.com/asha' }] },
  summary: 'Data science student who builds Flask and Vue applications with automated tests and deploys them on the cloud for real users across India.',
  experience: [{ role: 'Data Intern', org: 'Acme', start: 'Jun 2026', end: 'Aug 2026', bullets: ['Built a Python dashboard used by 12 analysts', 'Reduced report time by 40% with SQL views'] }],
  projects: [{ name: 'Tracker', tech: 'Flask, Vue.js', bullets: ['Designed a 7-table schema for bookings', 'Automated reminders with Celery workers'] }],
  education: [{ school: 'IIT Madras', degree: 'B.S. Data Science', start: '2024', end: '2028' }],
  skills: [{ group: 'Languages', items: 'Python, SQL, JavaScript' }, { group: 'Web', items: 'Flask, Vue.js, Bootstrap' }],
  achievements: [], certifications: [],
}

describe('ATS resume checks', () => {
  it('detects action verbs', () => {
    expect(startsWithActionVerb('Built a dashboard')).toBe(true)
    expect(startsWithActionVerb('Responsible for the dashboard')).toBe(false)
  })
  it('flags weak, unquantified, first-person bullets', () => {
    const codes = bulletIssues('Responsible for making my website').map((i) => i.code)
    expect(codes).toEqual(expect.arrayContaining(['weak_start', 'no_number', 'first_person']))
    expect(bulletIssues('Reduced report time by 40% with SQL views')).toEqual([])
  })
  it('passes a solid resume on the key checks', () => {
    const r = analyze(good)
    const status = Object.fromEntries(r.checks.map((c) => [c.id, c.status]))
    expect(status).toMatchObject({ contact: 'pass', phone: 'pass', links: 'pass', experience: 'pass', action_verbs: 'pass', quantified: 'pass', education: 'pass', skills: 'pass', dates: 'pass' })
    expect(r.passed).toBeGreaterThanOrEqual(12)
  })
  it('fails an empty resume clearly', () => {
    const r = analyze({ basics: {}, experience: [], projects: [], education: [], skills: [] })
    const status = Object.fromEntries(r.checks.map((c) => [c.id, c.status]))
    expect(status).toMatchObject({ contact: 'fail', experience: 'fail', education: 'fail', skills: 'fail' })
  })
  it('builds plain text in reading order', () => {
    const t = resumeText(good)
    expect(t.indexOf('EXPERIENCE')).toBeLessThan(t.indexOf('EDUCATION'))
    expect(t).toContain('• Built a Python dashboard used by 12 analysts')
  })
})

describe('job keyword matching', () => {
  const jd = 'We need students with Python, SQL and machine learning experience. Knowledge of Flask is a plus. Python is required.'
  it('extracts meaningful keywords and phrases, not filler words', () => {
    const kw = extractKeywords(jd)
    expect(kw).toEqual(expect.arrayContaining(['python', 'sql', 'machine learning', 'flask']))
    expect(kw).not.toContain('students')
    expect(kw).not.toContain('need')
    expect(kw[0]).toBe('machine learning')
  })
  it('ignores dates, money and admin words in opportunity text', () => {
    const kw = extractKeywords('Students in the penultimate year of a 3-year law or 5-year integrated course in economics or finance. Stipend of Rs 25,000 per month from April. Outstation trainees arrange their own accommodation.')
    expect(kw).toEqual(expect.arrayContaining(['law', 'economics', 'finance']))
    for (const junk of ['stipend', 'april', 'accommodation', 'penultimate', '3-year', 'arrange', 'trainees']) expect(kw).not.toContain(junk)
  })
  it('matches on whole words and reports what is missing', () => {
    const m = matchKeywords(good, jd)
    expect(m.matched).toEqual(expect.arrayContaining(['python', 'sql', 'flask']))
    expect(m.missing).toContain('machine learning')
    expect(m.percent).toBeGreaterThan(0)
  })
})
