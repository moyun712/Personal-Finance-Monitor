<script setup lang="ts">
/**
 * RegisterView — standalone layout (no TabBar, no sidebar).
 * Centered card with max-width 420px.
 */
</script>

<template>
  <div class="register-page">
    <div class="register-card">
      <h1>💰 创建账号</h1>
      <p class="subtitle">注册页面开发中…</p>
      <router-link to="/login" class="link">已有账号？去登录</router-link>
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
  padding: 40px 32px;
  background: var(--color-surface);
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  text-align: center;
}

.register-card h1 {
  font-size: 22px;
  margin-bottom: 12px;
  color: var(--color-text-primary);
}

.subtitle {
  color: var(--color-text-secondary);
  font-size: 14px;
  margin-bottom: 20px;
}

.link {
  color: #3b82f6;
  font-size: 14px;
  text-decoration: none;
}

.link:hover {
  text-decoration: underline;
}
</style>
