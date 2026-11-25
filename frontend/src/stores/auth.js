import { defineStore } from 'pinia'
import api from '@/api'

export const useAuth = defineStore('auth', {
  state: () => ({ user: null, ready: false }),
  getters: {
    isLoggedIn: (s) => !!s.user,
    isAdmin: (s) => s.user?.role === 'admin',
    profile: (s) => s.user?.profile || {},
    firstName: (s) => (s.user?.profile?.full_name || '').split(' ')[0] || 'there',
  },
  actions: {
    async init() {
      if (this.ready) return
      try {
        this.user = (await api.get('/auth/me')).user
      } catch {
        this.user = null
      } finally {
        this.ready = true
      }
    },
    async login(email, password) {
      this.user = (await api.post('/auth/login', { email, password })).user
      return this.user
    },
    async register(payload) {
      this.user = (await api.post('/auth/register', payload)).user
      return this.user
    },
    async logout() {
      try { await api.post('/auth/logout') } finally { this.user = null }
    },
    async updateProfile(patch) {
      this.user = (await api.put('/profile', patch)).user
      return this.user
    },
    async refresh() {
      this.user = (await api.get('/auth/me')).user
    },
    setUser(user) { this.user = user },
  },
})
