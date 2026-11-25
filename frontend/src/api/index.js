// One API surface for the whole app.
//  - Normal build: talks to the Flask API (same origin, JWT in HttpOnly cookies + CSRF header).
//  - Preview build (VITE_PREVIEW=true, used on GitHub Pages): a browser-only implementation of the
//    same endpoints that stores data in localStorage. It is clearly labelled in the UI.
import axios from 'axios'

export const IS_PREVIEW = import.meta.env.VITE_PREVIEW === 'true'
const BASE = import.meta.env.VITE_API_BASE || '/api/v1'

export class ApiError extends Error {
  constructor(status, code, message, fields) {
    super(message)
    this.status = status
    this.code = code
    this.fields = fields || {}
  }
}

function readCookie(name) {
  const match = document.cookie.split('; ').find((c) => c.startsWith(name + '='))
  return match ? decodeURIComponent(match.split('=')[1]) : null
}

const http = axios.create({ baseURL: BASE, withCredentials: true, timeout: 60000 })

http.interceptors.request.use((config) => {
  if (config.method && config.method !== 'get') {
    const token = readCookie(config.url?.endsWith('/auth/refresh') ? 'csrf_refresh_token' : 'csrf_access_token')
    if (token) config.headers['X-CSRF-TOKEN'] = token
  }
  return config
})

let refreshing = null
async function realRequest(method, url, { params, data, raw } = {}, retried = false) {
  try {
    const res = await http.request({ method, url, params, data, responseType: raw ? 'blob' : 'json' })
    return res.data
  } catch (err) {
    const res = err.response
    const body = res?.data?.error
    if (res?.status === 401 && body?.code === 'token_expired' && !retried && !url.startsWith('/auth/')) {
      refreshing = refreshing || http.post('/auth/refresh').finally(() => { refreshing = null })
      try {
        await refreshing
        return realRequest(method, url, { params, data, raw }, true)
      } catch { /* fall through to the original error */ }
    }
    if (!res) throw new ApiError(0, 'network_error', 'Could not reach FormSaathi. Check your connection and try again.')
    throw new ApiError(res.status, body?.code || 'error', body?.message || 'Something went wrong. Please try again.', body?.fields)
  }
}

let previewModule = null
async function request(method, url, opts = {}) {
  if (IS_PREVIEW) {
    if (!previewModule) previewModule = await import('./preview/server.js')
    return previewModule.handle(method, url, opts)
  }
  return realRequest(method, url, opts)
}

export const api = {
  /**
   * Best-effort PUT while the page is closing (reload, tab close, app switch).
   * Real server: a keepalive fetch that finishes even after the page unloads.
   * Preview build: a synchronous write to this browser's storage.
   */
  putNow(url, data) {
    if (IS_PREVIEW) { previewModule?.handleSync('put', url, { data }); return }
    const token = readCookie('csrf_access_token')
    try {
      fetch(BASE + url, {
        method: 'PUT', keepalive: true, credentials: 'include',
        headers: { 'Content-Type': 'application/json', ...(token ? { 'X-CSRF-TOKEN': token } : {}) },
        body: JSON.stringify(data),
      })
    } catch { /* best effort: the page is going away */ }
  },
  get: (url, params) => request('get', url, { params }),
  post: (url, data) => request('post', url, { data }),
  put: (url, data) => request('put', url, { data }),
  patch: (url, data) => request('patch', url, { data }),
  delete: (url, data) => request('delete', url, { data }),
  upload: (url, formData) => request('post', url, { data: formData }),
  /** Open a stored document in a new tab (authenticated). */
  async openDocument(id, download = false) {
    const blob = await request('get', `/documents/${id}/file`, { params: download ? { download: 1 } : {}, raw: true })
    const href = URL.createObjectURL(blob)
    window.open(href, '_blank', 'noopener')
    setTimeout(() => URL.revokeObjectURL(href), 60000)
  },
}

export default api
