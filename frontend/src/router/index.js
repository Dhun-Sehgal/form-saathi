import { createRouter, createWebHashHistory, createWebHistory } from 'vue-router'
import { IS_PREVIEW } from '@/api'
import { useAuth } from '@/stores/auth'

const pub = (path, name, loader, meta = {}) => ({ path, name, component: loader, meta: { layout: 'public', ...meta } })
const app = (path, name, loader, meta = {}) => ({ path, name, component: loader, meta: { layout: 'app', auth: true, ...meta } })
const adm = (path, name, loader, meta = {}) => ({ path, name, component: loader, meta: { layout: 'admin', auth: true, admin: true, ...meta } })

const routes = [
  pub('/', 'home', () => import('@/views/public/HomeView.vue'), { title: 'Never Miss an Opportunity You Deserve' }),
  pub('/explore', 'explore', () => import('@/views/shared/ExploreView.vue'), { title: 'Explore opportunities' }),
  pub('/opportunities/:slug', 'opportunity', () => import('@/views/shared/OpportunityView.vue'), { title: 'Opportunity' }),
  pub('/how-it-works', 'how', () => import('@/views/public/HowItWorksView.vue'), { title: 'How it works' }),
  pub('/about', 'about', () => import('@/views/public/AboutView.vue'), { title: 'About' }),
  pub('/help', 'help', () => import('@/views/public/HelpView.vue'), { title: 'Help centre' }),
  pub('/privacy', 'privacy', () => import('@/views/public/LegalView.vue'), { title: 'Privacy policy', doc: 'privacy' }),
  pub('/terms', 'terms', () => import('@/views/public/LegalView.vue'), { title: 'Terms of use', doc: 'terms' }),
  pub('/contact', 'contact', () => import('@/views/public/ContactView.vue'), { title: 'Contact' }),
  pub('/login', 'login', () => import('@/views/auth/LoginView.vue'), { title: 'Log in', guest: true, bare: true }),
  pub('/register', 'register', () => import('@/views/auth/RegisterView.vue'), { title: 'Create account', guest: true, bare: true }),
  pub('/forgot-password', 'forgot', () => import('@/views/auth/ForgotPasswordView.vue'), { title: 'Forgot password', bare: true }),
  pub('/reset-password/:token', 'reset', () => import('@/views/auth/ResetPasswordView.vue'), { title: 'Reset password', bare: true }),
  { path: '/onboarding', name: 'onboarding', component: () => import('@/views/auth/OnboardingView.vue'), meta: { layout: 'bare', auth: true, title: 'Set up your profile' } },

  app('/app', 'dashboard', () => import('@/views/app/DashboardView.vue'), { title: 'Dashboard' }),
  app('/app/discover', 'discover', () => import('@/views/shared/ExploreView.vue'), { title: 'Discover' }),
  app('/app/opportunities/:slug', 'app-opportunity', () => import('@/views/shared/OpportunityView.vue'), { title: 'Opportunity' }),
  app('/app/eligibility/:id', 'eligibility', () => import('@/views/app/EligibilityView.vue'), { title: 'Eligibility check' }),
  app('/app/compare', 'compare', () => import('@/views/app/CompareView.vue'), { title: 'Compare' }),
  app('/app/saved', 'saved', () => import('@/views/app/SavedView.vue'), { title: 'Saved' }),
  app('/app/tracker', 'tracker', () => import('@/views/app/TrackerView.vue'), { title: 'Application tracker' }),
  app('/app/tracker/:id', 'application', () => import('@/views/app/ApplicationView.vue'), { title: 'Application' }),
  app('/app/calendar', 'calendar', () => import('@/views/app/CalendarView.vue'), { title: 'Calendar' }),
  app('/app/documents', 'documents', () => import('@/views/app/DocumentsView.vue'), { title: 'Documents' }),
  app('/app/saathi', 'saathi', () => import('@/views/app/SaathiView.vue'), { title: 'Saathi AI' }),
  app('/app/notifications', 'notifications', () => import('@/views/app/NotificationsView.vue'), { title: 'Notifications' }),
  app('/app/profile', 'profile', () => import('@/views/app/ProfileView.vue'), { title: 'Profile' }),
  app('/app/settings', 'settings', () => import('@/views/app/SettingsView.vue'), { title: 'Settings' }),

  adm('/admin', 'admin', () => import('@/views/admin/AdminDashboard.vue'), { title: 'Admin' }),
  adm('/admin/opportunities', 'admin-opportunities', () => import('@/views/admin/AdminOpportunities.vue'), { title: 'Opportunities' }),
  adm('/admin/opportunities/new', 'admin-new', () => import('@/views/admin/AdminEditor.vue'), { title: 'New opportunity' }),
  adm('/admin/opportunities/:id', 'admin-edit', () => import('@/views/admin/AdminEditor.vue'), { title: 'Edit opportunity' }),
  adm('/admin/corrections', 'admin-corrections', () => import('@/views/admin/AdminCorrections.vue'), { title: 'Corrections' }),
  adm('/admin/categories', 'admin-categories', () => import('@/views/admin/AdminCategories.vue'), { title: 'Categories' }),
  adm('/admin/users', 'admin-users', () => import('@/views/admin/AdminUsers.vue'), { title: 'Users' }),
  adm('/admin/announcements', 'admin-announcements', () => import('@/views/admin/AdminAnnouncements.vue'), { title: 'Announcements' }),
  adm('/admin/feedback', 'admin-feedback', () => import('@/views/admin/AdminFeedback.vue'), { title: 'Feedback' }),

  pub('/:pathMatch(.*)*', 'not-found', () => import('@/views/public/NotFoundView.vue'), { title: 'Page not found' }),
]

const router = createRouter({
  // GitHub Pages has no server-side rewrites, so its preview build uses hash URLs.
  // Vercel rewrites every path to index.html, so that build keeps clean URLs (VITE_HASH_ROUTER=false).
  history: IS_PREVIEW && import.meta.env.VITE_HASH_ROUTER !== 'false' ? createWebHashHistory(import.meta.env.BASE_URL) : createWebHistory(import.meta.env.BASE_URL),
  routes,
  scrollBehavior(to, from, saved) {
    if (saved) return saved
    if (to.hash) return { el: to.hash, top: 80 }
    if (to.path === from.path) return false
    return { top: 0 }
  },
})

router.beforeEach(async (to) => {
  const auth = useAuth()
  await auth.init()
  if (to.meta.auth && !auth.isLoggedIn) return { name: 'login', query: { next: to.fullPath } }
  if (to.meta.admin && !auth.isAdmin) return { name: 'dashboard' }
  if (to.meta.guest && auth.isLoggedIn) return { path: to.query.next || '/app' }
  if (auth.isLoggedIn && !auth.user.onboarding_completed && to.meta.layout === 'app' && !auth.isAdmin) return { name: 'onboarding' }
  return true
})

router.afterEach((to) => {
  document.title = to.meta.title ? `${to.meta.title} · FormSaathi` : 'FormSaathi'
})

export default router
