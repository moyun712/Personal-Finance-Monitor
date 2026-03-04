/**
 * Auth store — manages JWT token, user info, and authentication state.
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import apiClient from '@/api'

export interface UserInfo {
  id: number
  username: string
  nickname: string | null
  monthly_income: number | null
  payday: number | null
  created_at: string
}

export const useAuthStore = defineStore('auth', () => {
  // ── State ──────────────────────────────────────────────────
  const token = ref<string | null>(localStorage.getItem('token'))
  const userInfo = ref<UserInfo | null>(null)
  const needsOnboarding = ref(false)

  // ── Getters ────────────────────────────────────────────────
  const isLoggedIn = computed(() => !!token.value)

  // ── Actions ────────────────────────────────────────────────

  function setToken(newToken: string) {
    token.value = newToken
    localStorage.setItem('token', newToken)
  }

  function clearAuth() {
    token.value = null
    userInfo.value = null
    needsOnboarding.value = false
    localStorage.removeItem('token')
  }

  async function register(username: string, password: string, nickname?: string) {
    const { data } = await apiClient.post('/auth/register', {
      username,
      password,
      nickname: nickname || undefined,
    })
    return data as UserInfo
  }

  async function login(username: string, password: string) {
    const { data } = await apiClient.post('/auth/login', { username, password })
    setToken(data.access_token)
    // Fetch user info after login
    await fetchUserInfo()
    return data
  }

  async function fetchUserInfo() {
    try {
      const { data } = await apiClient.get('/auth/me')
      userInfo.value = data as UserInfo
    } catch {
      clearAuth()
      throw new Error('获取用户信息失败')
    }
  }

  async function updateProfile(payload: {
    nickname?: string
    monthly_income?: number
    payday?: number
  }) {
    const { data } = await apiClient.put('/auth/profile', payload)
    userInfo.value = data as UserInfo
    return data
  }

  function logout() {
    clearAuth()
  }

  return {
    token,
    userInfo,
    needsOnboarding,
    isLoggedIn,
    setToken,
    clearAuth,
    register,
    login,
    fetchUserInfo,
    updateProfile,
    logout,
  }
})
