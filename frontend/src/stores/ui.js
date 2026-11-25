import { defineStore } from 'pinia'

let toastId = 0
export const useUi = defineStore('ui', {
  state: () => ({
    toasts: [],
    theme: localStorage.getItem('fs-theme') || (window.matchMedia?.('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'),
    sidebarCollapsed: localStorage.getItem('fs-sidebar') === '1',
    confirmState: null,
    unread: 0,
  }),
  actions: {
    toast(message, type = 'success', timeout = 3500) {
      const id = ++toastId
      this.toasts.push({ id, message, type })
      setTimeout(() => this.dismiss(id), timeout)
    },
    error(e) { this.toast(e?.message || 'Something went wrong.', 'error', 5000) },
    dismiss(id) { this.toasts = this.toasts.filter((t) => t.id !== id) },
    applyTheme() { document.documentElement.setAttribute('data-bs-theme', this.theme) },
    toggleTheme() {
      this.theme = this.theme === 'dark' ? 'light' : 'dark'
      localStorage.setItem('fs-theme', this.theme)
      this.applyTheme()
    },
    toggleSidebar() {
      this.sidebarCollapsed = !this.sidebarCollapsed
      localStorage.setItem('fs-sidebar', this.sidebarCollapsed ? '1' : '0')
    },
    /** Promise-based confirm dialog: await ui.confirm({title, message, confirmText, danger}) */
    confirm(opts) {
      return new Promise((resolve) => { this.confirmState = { confirmText: 'Confirm', ...opts, resolve } })
    },
    closeConfirm(result) {
      this.confirmState?.resolve(result)
      this.confirmState = null
    },
  },
})
