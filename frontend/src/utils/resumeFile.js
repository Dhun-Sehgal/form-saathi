// Read an existing resume file into plain text, entirely in the browser (nothing is uploaded).
// PDF via Mozilla pdf.js (loaded only when needed), Word .docx by unzipping document.xml, and .txt as is.
// The result is roughly what an applicant tracking system's parser sees.

export const MAX_RESUME_BYTES = 5 * 1024 * 1024
export const ACCEPTED_RESUME_TYPES = '.pdf,.docx,.txt,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document,text/plain'

export class ResumeFileError extends Error {}

function kindOf(file) {
  const name = (file.name || '').toLowerCase()
  if (name.endsWith('.pdf') || file.type === 'application/pdf') return 'pdf'
  if (name.endsWith('.docx') || file.type.includes('wordprocessingml')) return 'docx'
  if (name.endsWith('.txt') || file.type === 'text/plain') return 'txt'
  if (name.endsWith('.doc')) return 'doc'
  if (/\.(png|jpe?g|webp|heic|gif)$/.test(name) || file.type.startsWith('image/')) return 'image'
  return 'other'
}

/** @returns {Promise<{ text: string, pages: number|null, kind: string, fileName: string }>} */
export async function readResumeFile(file) {
  if (!file) throw new ResumeFileError('Choose a file first.')
  if (file.size > MAX_RESUME_BYTES) throw new ResumeFileError('This file is larger than 5 MB. Resumes are usually well under 1 MB — export it again as a PDF.')
  const kind = kindOf(file)
  if (kind === 'image') throw new ResumeFileError('This is an image. Applicant tracking systems cannot read text inside images — upload the PDF or Word file instead.')
  if (kind === 'doc') throw new ResumeFileError('Old .doc files are not supported. Save it as .docx or PDF and upload that.')
  if (kind === 'other') throw new ResumeFileError('Upload a PDF, Word (.docx) or plain text (.txt) file.')
  const base = { kind, fileName: file.name }
  if (kind === 'txt') return { ...base, text: normalise(await file.text()), pages: null }
  const buffer = await file.arrayBuffer()
  if (kind === 'docx') return { ...base, text: normalise(await docxText(buffer)), pages: null }
  const { text, pages } = await pdfText(buffer)
  return { ...base, text: normalise(text), pages }
}

function normalise(text) {
  return (text || '').replace(/\r\n?/g, '\n').replace(/[ \t ]+/g, ' ').replace(/ *\n */g, '\n').replace(/\n{3,}/g, '\n\n').trim()
}

// ---- PDF -----------------------------------------------------------------------------------
async function pdfText(buffer) {
  const pdfjs = await import('pdfjs-dist/legacy/build/pdf.mjs')
  const { default: workerSrc } = await import('pdfjs-dist/legacy/build/pdf.worker.min.mjs?url')
  pdfjs.GlobalWorkerOptions.workerSrc = workerSrc
  let doc
  try {
    doc = await pdfjs.getDocument({ data: new Uint8Array(buffer), isEvalSupported: false }).promise
  } catch (e) {
    if (e?.name === 'PasswordException') throw new ResumeFileError('This PDF is password-protected. Applicant tracking systems cannot open it either — save a copy without a password.')
    throw new ResumeFileError('We could not open this PDF. It may be damaged — try exporting it again.')
  }
  const pageTexts = []
  for (let n = 1; n <= doc.numPages; n++) {
    const page = await doc.getPage(n)
    const { items } = await page.getTextContent()
    pageTexts.push(linesFromItems(items.filter((it) => typeof it.str === 'string')))
  }
  return { text: pageTexts.join('\n\n'), pages: doc.numPages }
}

// Group text pieces into lines by their vertical position, then read each line left to right.
function linesFromItems(items) {
  const rows = []
  for (const it of items) {
    if (!it.str && !it.hasEOL) continue
    const x = it.transform[4], y = it.transform[5], h = Math.abs(it.transform[3]) || 10
    let row = rows.find((r) => Math.abs(r.y - y) <= Math.max(2, h * 0.35))
    if (!row) { row = { y, parts: [] }; rows.push(row) }
    row.parts.push({ x, w: it.width || 0, str: it.str })
  }
  rows.sort((a, b) => b.y - a.y)
  return rows.map((r) => {
    r.parts.sort((a, b) => a.x - b.x)
    let line = '', end = null
    for (const p of r.parts) {
      if (end !== null && p.x - end > 1.5 && !line.endsWith(' ') && !p.str.startsWith(' ')) line += ' '
      line += p.str
      end = p.x + p.w
    }
    return line.trim()
  }).filter(Boolean).join('\n')
}

// ---- Word .docx ------------------------------------------------------------------------------
async function docxText(buffer) {
  const { unzipSync, strFromU8 } = await import('fflate')
  let files
  try { files = unzipSync(new Uint8Array(buffer), { filter: (f) => f.name === 'word/document.xml' }) } catch {
    throw new ResumeFileError('We could not open this Word file. Save it again as .docx or export a PDF.')
  }
  const xml = files['word/document.xml'] ? strFromU8(files['word/document.xml']) : ''
  if (!xml) throw new ResumeFileError('This Word file has no readable text.')
  const body = xml.split(/<w:body[^>]*>/)[1] || xml
  return body.split(/<\/w:p>/).map((p) => {
    const isListItem = /<w:numPr>/.test(p)
    const text = p
      .replace(/<w:tab\/>/g, '<w:t> </w:t>').replace(/<w:br[^>]*\/>/g, '<w:t>\n</w:t>')
      .replace(/<w:t(?:\s[^>]*)?>([\s\S]*?)<\/w:t>/g, (_, t) => `\u0000${t}\u0000`)
      .split('\u0000').filter((_, i) => i % 2 === 1).join('')
    const clean = decodeXml(text).trim()
    return clean ? (isListItem ? `• ${clean}` : clean) : ''
  }).filter(Boolean).join('\n')
}

function decodeXml(s) {
  return s.replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&quot;/g, '"').replace(/&apos;/g, "'")
    .replace(/&#(\d+);/g, (_, d) => String.fromCodePoint(Number(d))).replace(/&#x([0-9a-f]+);/gi, (_, h) => String.fromCodePoint(parseInt(h, 16)))
    .replace(/&amp;/g, '&')
}
