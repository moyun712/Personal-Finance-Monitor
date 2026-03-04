import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      component: () => import('@/layouts/LayoutSwitch.vue'),
      children: [
        { path: '', name: 'home', component: () => import('@/views/HomeView.vue') },
        { path: 'record', name: 'record', component: () => import('@/views/RecordView.vue') },
        { path: 'analysis', name: 'analysis', component: () => import('@/views/AnalysisView.vue') },
        { path: 'profile', name: 'profile', component: () => import('@/views/ProfileView.vue') },
        { path: 'sandbox', name: 'sandbox', component: () => import('@/views/SimulationView.vue') },
        { path: 'settings', name: 'settings', component: () => import('@/views/SettingsView.vue') },
      ],
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/LoginView.vue'),
      meta: { guest: true },
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('@/views/RegisterView.vue'),
      meta: { guest: true },
    },
    {
      path: '/onboarding',
      name: 'onboarding',
      component: () => import('@/views/OnboardingView.vue'),
    },
  ],
})

// ── Navigation guard: auth & onboarding redirect ─────────────
router.beforeEach((to, _from, next) => {
  const authStore = useAuthStore()

  // Pages that don't require authentication
  const isGuestPage = to.meta.guest === true
  const isOnboarding = to.name === 'onboarding'

  if (!authStore.isLoggedIn && !isGuestPage && !isOnboarding) {
    // Not logged in → redirect to login
    return next({ name: 'login' })
  }

  if (authStore.isLoggedIn && isGuestPage) {
    // Already logged in → redirect away from login/register
    return next({ name: 'home' })
  }

  if (authStore.isLoggedIn && authStore.needsOnboarding && !isOnboarding) {
    // Needs onboarding → force to onboarding page
    return next({ name: 'onboarding' })
  }

  next()
})

export default router
