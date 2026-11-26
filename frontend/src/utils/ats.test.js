import { describe, expect, it } from 'vitest'
import { analyze, analyzeText, bulletIssues, extractKeywords, matchKeywords, matchKeywordsText, resumeText, scoreOf, sectionOf, startsWithActionVerb } from './ats.js'

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

describe('ATS score', () => {
  it('is the checks added up: pass 1, warning ½, fail 0', () => {
    expect(scoreOf([{ status: 'pass' }, { status: 'warn' }, { status: 'fail' }, { status: 'pass' }])).toBe(63)
    expect(scoreOf([])).toBe(0)
  })
  it('is returned by the builder report', () => {
    const r = analyze(good)
    expect(r.score).toBe(scoreOf(r.checks))
  })
})

describe('checking an existing resume from its text', () => {
  const sample = `Riya Sharma
Pune, Maharashtra | +91 98765 43210 | riya.sharma@example.com | linkedin.com/in/riya
PROFESSIONAL SUMMARY
Final-year computer science student who builds data dashboards and web apps, with internship experience in analytics and a focus on measurable results for small businesses.
EXPERIENCE
Data Analyst Intern | Example Analytics Jun 2025 – Aug 2025
• Built a sales dashboard in Power BI used by 12 store managers to track weekly targets across
three regions.
• Reduced report preparation time by 40% by automating Excel exports with Python.
PROJECTS
Hospital Booking App | Flask, Vue.js 2024
• Designed a 7-table schema for appointments, doctors and patients with role-based access.
• Wrote 30 unit tests that run in GitHub Actions on every push.
EDUCATION
Savitribai Phule Pune University — B.E. Computer Engineering 2022 – 2026
CGPA 8.4
TECHNICAL SKILLS
Languages: Python, SQL, JavaScript
Tools: Power BI, Excel, Flask, Vue.js, Git, Pandas`

  it('finds the standard sections and rejoins wrapped bullets', () => {
    expect(sectionOf('TECHNICAL SKILLS')).toBe('skills')
    expect(sectionOf('Hospital Booking App | Flask')).toBeNull()
    const r = analyzeText(sample, { pages: 1 })
    expect(r.sections).toEqual(['summary', 'experience', 'projects', 'education', 'skills'])
    expect(r.stats.bullets).toBe(4)
    expect(r.checks.find((c) => c.id === 'contact').status).toBe('pass')
    expect(r.checks.find((c) => c.id === 'phone').status).toBe('pass')
    expect(r.checks.find((c) => c.id === 'skills').status).toBe('pass')
    expect(r.score).toBeGreaterThanOrEqual(85)
  })

  it('fails a resume whose text cannot be read (scanned image)', () => {
    const r = analyzeText('   ', { pages: 1 })
    expect(r.unreadable).toBe(true)
    expect(r.score).toBe(0)
    expect(r.checks[0].status).toBe('fail')
  })

  it('flags broken characters, missing sections and first person', () => {
    const messy = `Asha\nasha@example.com\n${'I built many things and my work was good. '.repeat(30)}\nWork\n� helped with the website\n� worked on reports`
    const r = analyzeText(messy)
    expect(r.checks.find((c) => c.id === 'headings').status).toBe('fail')
    expect(r.checks.find((c) => c.id === 'clean_chars').status).not.toBe('pass')
    expect(r.score).toBeLessThan(60)
  })

  it('does not treat roman numerals as first person', () => {
    expect(bulletIssues('Earned an A grade in MAD I and Part I & II').some((i) => i.code === 'first_person')).toBe(false)
    expect(bulletIssues('Built a tool I am proud of').some((i) => i.code === 'first_person')).toBe(true)
  })

  it('matches job keywords against the raw text', () => {
    const m = matchKeywordsText(sample, 'We need Python, SQL and Power BI skills for dashboards. Tableau is a plus.')
    expect(m.matched).toEqual(expect.arrayContaining(['python', 'sql', 'power bi']))
    expect(m.missing).toContain('tableau')
  })
})
