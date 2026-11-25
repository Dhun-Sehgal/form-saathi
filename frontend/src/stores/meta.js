import { defineStore } from 'pinia'
import api from '@/api'

export const useMeta = defineStore('meta', {
  state: () => ({ loaded: false, categories: [], states: [], document_types: [], enums: {}, portals: [], features: { ai: false, email: false, preview: false } }),
  getters: {
    stateName: (s) => (code) => s.states.find((x) => x.code === code)?.name || code,
    category: (s) => (slug) => s.categories.find((c) => c.slug === slug),
  },
  actions: {
    async load() {
      if (this.loaded) return
      const data = await api.get('/meta')
      Object.assign(this, data, { loaded: true })
    },
  },
})
