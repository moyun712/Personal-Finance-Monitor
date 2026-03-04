<script setup lang="ts">
/**
 * LoginView — standalone layout (no TabBar, no sidebar).
 * Centered card with max-width 420px.
 */
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { showToast } from 'vant'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const username = ref('')
const password = ref('')
const loading = ref(false)

async function handleLogin() {
  if (!username.value || !password.value) {
    showToast('请输入用户名和密码')
    return
  }
  loading.value = true
  try {
    await authStore.login(username.value, password.value)
    router.replace('/')
  } catch (err: any) {
    const msg = err?.response?.data?.detail || '登录失败，请重试'
    showToast(msg)
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="login-page">
    <div class="login-card">
      <h1>💰 智能财务管理系统</h1>
      <p class="subtitle">登录你的账号</p>

      <van-form @submit="handleLogin">
        <van-cell-group inset>
          <van-field
            v-model="username"
            label="用户名"
            placeholder="请输入用户名"
            :rules="[{ required: true, message: '请输入用户名' }]"
          />
          <van-field
            v-model="password"
            type="password"
            label="密码"
            placeholder="请输入密码"
            :rules="[{ required: true, message: '请输入密码' }]"
          />
        </van-cell-group>

        <div class="actions">
          <van-button
            type="primary"
            block
            round
            native-type="submit"
            :loading="loading"
            loading-text="登录中..."
          >
            登录
          </van-button>
        </div>
      </van-form>

      <router-link to="/register" class="link">没有账号？立即注册</router-link>
    </div>
  </div>
</template>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-bg);
}

.login-card {
  width: 100%;
  max-width: 420px;
  margin: 0 16px;
  padding: 40px 24px;
  background: var(--color-surface);
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  text-align: center;
}

.login-card h1 {
  font-size: 22px;
  margin-bottom: 8px;
  color: var(--color-text-primary);
}

.subtitle {
  color: var(--color-text-secondary);
  font-size: 14px;
  margin-bottom: 24px;
}

.actions {
  margin: 24px 16px 16px;
}

.link {
  display: inline-block;
  margin-top: 12px;
  color: #3b82f6;
  font-size: 14px;
  text-decoration: none;
}

.link:hover {
  text-decoration: underline;
}
</style>
