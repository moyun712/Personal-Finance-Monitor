<script setup lang="ts">
/**
 * PCLayout — sidebar + top bar for ≥768px viewports.
 * Sidebar (220px): Logo + nav menu (总览/分析/沙盘推演/设置).
 * AI 助手通过全局悬浮窗进入，不在侧边栏导航中。
 * Right: top bar (user info + logout) + content area (max-width 1200px).
 */
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()

const navItems = [
  { path: '/', label: '总览', icon: '📊' },
  { path: '/analysis', label: '分析', icon: '📈' },
  { path: '/sandbox', label: '沙盘推演', icon: '🎯' },
  { path: '/settings', label: '设置', icon: '⚙️' },
]

const activePath = computed(() => route.path)

function navigateTo(path: string) {
  router.push(path)
}

function handleLogout() {
  localStorage.removeItem('token')
  router.push('/login')
}
</script>

<template>
  <div class="pc-layout">
    <!-- Sidebar -->
    <aside class="pc-sidebar">
      <div class="pc-logo">
        <h2>💰 智能财务</h2>
      </div>
      <nav class="pc-nav">
        <a
          v-for="item in navItems"
          :key="item.path"
          class="pc-nav-item"
          :class="{ active: activePath === item.path }"
          @click="navigateTo(item.path)"
        >
          <span class="pc-nav-icon">{{ item.icon }}</span>
          <span class="pc-nav-label">{{ item.label }}</span>
        </a>
      </nav>
    </aside>

    <!-- Main area -->
    <div class="pc-main">
      <header class="pc-topbar">
        <div class="pc-topbar-title" />
        <div class="pc-topbar-actions">
          <span class="pc-user-info">用户</span>
          <button class="pc-logout-btn" @click="handleLogout">退出</button>
        </div>
      </header>
      <main class="pc-content">
        <slot />
      </main>
    </div>
  </div>
</template>

<style scoped>
.pc-layout {
  display: flex;
  min-height: 100vh;
  background: var(--color-bg);
}

/* ── Sidebar ────────────────────────────────────────── */
.pc-sidebar {
  width: 220px;
  background: var(--color-surface);
  border-right: 1px solid var(--color-border);
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
}

.pc-logo {
  padding: 24px 20px;
  border-bottom: 1px solid var(--color-border);
}

.pc-logo h2 {
  margin: 0;
  font-size: 18px;
  color: var(--color-text-primary);
}

.pc-nav {
  flex: 1;
  padding: 12px 0;
}

.pc-nav-item {
  display: flex;
  align-items: center;
  padding: 12px 20px;
  cursor: pointer;
  color: var(--color-text-secondary);
  transition: all 0.2s;
  text-decoration: none;
  user-select: none;
}

.pc-nav-item:hover {
  background: rgba(0, 0, 0, 0.04);
  color: var(--color-text-primary);
}

.pc-nav-item.active {
  background: rgba(59, 130, 246, 0.08);
  color: #3b82f6;
  font-weight: 600;
}

.pc-nav-icon {
  margin-right: 12px;
  font-size: 18px;
}

.pc-nav-label {
  font-size: 14px;
}

/* ── Main area ──────────────────────────────────────── */
.pc-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.pc-topbar {
  height: 56px;
  background: var(--color-surface);
  border-bottom: 1px solid var(--color-border);
  display: flex;
  align-items: center;
  justify-content: flex-end;
  padding: 0 24px;
  flex-shrink: 0;
}

.pc-topbar-actions {
  display: flex;
  align-items: center;
  gap: 16px;
}

.pc-user-info {
  font-size: 14px;
  color: var(--color-text-secondary);
}

.pc-logout-btn {
  padding: 6px 16px;
  border: 1px solid var(--color-border);
  border-radius: 4px;
  background: var(--color-surface);
  color: var(--color-text-secondary);
  cursor: pointer;
  font-size: 13px;
  transition: all 0.2s;
}

.pc-logout-btn:hover {
  color: var(--color-expense);
  border-color: var(--color-expense);
}

.pc-content {
  flex: 1;
  padding: 24px;
  max-width: 1200px;
  width: 100%;
  margin: 0 auto;
  box-sizing: border-box;
}
</style>
