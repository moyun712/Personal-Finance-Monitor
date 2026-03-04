<script setup lang="ts">
/**
 * RegisterView — standalone layout (no TabBar, no sidebar).
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
const confirmPassword = ref('')
const loading = ref(false)

async function handleRegister() {
  if (!username.value || !password.value) {
    showToast('请输入用户名和密码')
    return
  }
  if (password.value !== confirmPassword.value) {
    showToast('两次密码输入不一致')
    return
  }
  if (username.value.length < 3) {
    showToast('用户名至少 3 个字符')
    return
  }
  if (password.value.length < 6) {
    showToast('密码至少 6 个字符')
    return
  }

  loading.value = true
  try {
    await authStore.register(username.value, password.value)
    // Auto-login after successful registration
    await authStore.login(username.value, password.value)
    authStore.needsOnboarding = true
    router.replace('/onboarding')
  } catch (err: any) {
    const msg = err?.response?.data?.detail || '注册失败，请重试'
    showToast(msg)
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="register-page">
    <div class="register-card">
      <h1>💰 创建账号</h1>
      <p class="subtitle">注册你的财务管理账号</p>

      <van-form @submit="handleRegister">
        <van-cell-group inset>
          <van-field
            v-model="username"
            label="用户名"
            placeholder="3-50 个字符"
            :rules="[{ required: true, message: '请输入用户名' }]"
          />
          <van-field
            v-model="password"
            type="password"
            label="密码"
            placeholder="至少 6 个字符"
            :rules="[{ required: true, message: '请输入密码' }]"
          />
          <van-field
            v-model="confirmPassword"
            type="password"
            label="确认密码"
            placeholder="再次输入密码"
            :rules="[{ required: true, message: '请确认密码' }]"
          />
        </van-cell-group>

        <div class="actions">
          <van-button
            type="primary"
            block
            round
            native-type="submit"
            :loading="loading"
            loading-text="注册中..."
          >
            注册
          </van-button>
        </div>
      </van-form>

      <router-link to="/login" class="link">已有账号？立即登录</router-link>
    </div>
  </div>
</template>

<style scoped>
.register-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-bg);
}

.register-card {
  width: 100%;
  max-width: 420px;
  margin: 0 16px;
  padding: 40px 24px;
  background: var(--color-surface);
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  text-align: center;
}

.register-card h1 {
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
