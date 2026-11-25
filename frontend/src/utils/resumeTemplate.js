// Renders a resume to an HTML string for the on-screen preview and for PDF export.
// ATS-safe by design: one column, standard section headings, real text, no tables/images/icons.
// Every user value is HTML-escaped; links are limited to http(s) and mailto.

const esc = (s) => (s ?? '').toString().replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]))
const t = (s) => (s ?? '').toString().trim()
const safeUrl = (u) => {
  const v = t(u)
  if (!v) return ''
  if (/^mailto:/i.test(v)) return v
  if (/^https?:\/\//i.test(v)) return v
  if (/^[\w.-]+\.[a-z]{2,}(\/.*)?$/i.test(v)) return `https://${v}`
  return ''
}
const dates = (a, b) => [t(a), t(b)].filter(Boolean).join(' – ')
const bullets = (list) => {
  const items = (list || []).map(t).filter(Boolean)
  return items.length ? `<ul>${items.map((x) => `<li>${esc(x)}</li>`).join('')}</ul>` : ''
}
const row = (left, right) => `<div class="rs-row"><div class="rs-left">${left}</div>${right ? `<div class="rs-right">${right}</div>` : ''}</div>`

export function renderResumeHTML(d, template = 'classic') {
  const b = d.basics || {}
  const contact = [esc(t(b.location)), esc(t(b.phone)), t(b.email) ? `<a href="mailto:${esc(t(b.email))}">${esc(t(b.email))}</a>` : '']
    .filter(Boolean).join(' <span class="rs-sep">|</span> ')
  const links = (b.links || []).filter((l) => t(l.url)).map((l) => {
    const url = safeUrl(l.url)
    const label = esc(t(l.label) || t(l.url))
    return url ? `<a href="${esc(url)}">${label}</a>` : label
  }).join(' <span class="rs-sep">|</span> ')

  const sections = []
  const add = (title, html) => { if (html) sections.push(`<section><h2>${title}</h2>${html}</section>`) }

  add('Professional Summary', t(d.summary) ? `<p>${esc(t(d.summary))}</p>` : '')
  add('Experience', (d.experience || []).filter((e) => t(e.role) || t(e.org)).map((e) =>
    `<div class="rs-entry">${row(`<strong>${esc(t(e.role))}</strong>${t(e.org) ? ` <span class="rs-sep">|</span> ${esc(t(e.org))}` : ''}`, esc(dates(e.start, e.end)))}${t(e.location) ? row('', `<em>${esc(t(e.location))}</em>`) : ''}${bullets(e.bullets)}</div>`).join(''))
  add('Projects', (d.projects || []).filter((p) => t(p.name)).map((p) => {
    const url = safeUrl(p.link)
    const link = t(p.link) ? (url ? `<a href="${esc(url)}">${esc(/github/i.test(p.link) ? 'GitHub' : 'Link')}</a>` : esc(t(p.link))) : ''
    return `<div class="rs-entry">${row(`<strong>${esc(t(p.name))}</strong>${t(p.tech) ? ` <span class="rs-sep">|</span> <em>${esc(t(p.tech))}</em>` : ''}`, link)}${bullets(p.bullets)}</div>`
  }).join(''))
  add('Education', (d.education || []).filter((e) => t(e.school)).map((e) =>
    `<div class="rs-entry">${row(`<strong>${esc(t(e.school))}</strong>`, esc(dates(e.start, e.end)))}${(t(e.degree) || t(e.score)) ? row(`<em>${esc([t(e.degree), t(e.score)].filter(Boolean).join(' | '))}</em>`, '') : ''}${t(e.details) ? `<p class="rs-details">${esc(t(e.details))}</p>` : ''}</div>`).join(''))
  add('Technical Skills', (d.skills || []).filter((s) => t(s.items)).map((s) =>
    `<p class="rs-skill">${t(s.group) ? `<strong>${esc(t(s.group))}:</strong> ` : ''}${esc(t(s.items))}</p>`).join(''))
  add('Achievements', bullets(d.achievements))
  add('Certifications', bullets(d.certifications))

  return `<article class="resume-doc rs-${template === 'modern' ? 'modern' : 'classic'}">
<header><h1>${esc(t(b.name) || 'Your Name')}</h1>${t(b.headline) ? `<div class="rs-headline">${esc(t(b.headline))}</div>` : ''}${contact ? `<div class="rs-contact">${contact}</div>` : ''}${links ? `<div class="rs-contact">${links}</div>` : ''}</header>
${sections.join('\n')}
</article>`
}

export const RESUME_CSS = `
.resume-doc { color: #111; background: #fff; font-size: 10.5pt; line-height: 1.38; text-align: left; }
.resume-doc a { color: inherit; text-decoration: underline; }
.resume-doc header { text-align: center; margin-bottom: 6pt; }
.resume-doc h1 { font-size: 21pt; margin: 0 0 2pt; letter-spacing: .02em; font-weight: 700; }
.resume-doc .rs-headline { font-size: 10.5pt; font-weight: 600; margin-bottom: 2pt; }
.resume-doc .rs-contact { font-size: 9.5pt; }
.resume-doc .rs-sep { color: #666; padding: 0 2pt; }
.resume-doc section { margin-top: 7pt; }
.resume-doc h2 { font-size: 11.5pt; margin: 0 0 3pt; padding-bottom: 1.5pt; border-bottom: 1px solid #333; text-transform: uppercase; letter-spacing: .06em; font-weight: 700; }
.resume-doc .rs-entry { margin-bottom: 4pt; }
.resume-doc .rs-row { display: flex; justify-content: space-between; gap: 10pt; }
.resume-doc .rs-left { min-width: 0; }
.resume-doc .rs-right { white-space: nowrap; flex-shrink: 0; font-size: 9.5pt; }
.resume-doc ul { margin: 1.5pt 0 0; padding-left: 14pt; }
.resume-doc li { margin: 0 0 1pt; }
.resume-doc p { margin: 0 0 2pt; }
.resume-doc .rs-details, .resume-doc .rs-skill { font-size: 10pt; }
.rs-classic { font-family: Georgia, 'Times New Roman', Cambria, serif; }
.rs-classic h1 { font-variant: small-caps; }
.rs-modern { font-family: Inter, Calibri, Arial, sans-serif; }
.rs-modern h1 { color: #735a41; letter-spacing: -.01em; }
.rs-modern h2 { color: #735a41; border-bottom: 1.5px solid #735a41; }
`

/** Print the resume through a hidden iframe so only the resume is printed (Save as PDF in the dialog). */
export function printResume(d, template, fileTitle) {
  const iframe = document.createElement('iframe')
  iframe.setAttribute('aria-hidden', 'true')
  iframe.style.cssText = 'position:fixed;right:0;bottom:0;width:0;height:0;border:0'
  document.body.appendChild(iframe)
  const doc = iframe.contentDocument
  doc.open()
  doc.write(`<!doctype html><html lang="en"><head><meta charset="utf-8"><title>${esc(fileTitle || 'Resume')}</title>
<style>@page { size: A4; margin: 12mm 13mm; } html, body { margin: 0; background: #fff; } ${RESUME_CSS}</style></head>
<body>${renderResumeHTML(d, template)}</body></html>`)
  doc.close()
  const done = () => setTimeout(() => iframe.remove(), 1000)
  iframe.contentWindow.addEventListener('afterprint', done)
  setTimeout(() => { iframe.contentWindow.focus(); iframe.contentWindow.print(); setTimeout(done, 60000) }, 250)
}
