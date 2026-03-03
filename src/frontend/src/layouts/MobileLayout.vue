<script setup lang="ts">
/**
 * MobileLayout — bottom TabBar navigation for <768px viewports.
 * Tabs: 总览 / 分析 / 我的 （无独立记账 Tab，记账入口在总览页快捷操作区）
 */
import { ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Tabbar as VanTabbar, TabbarItem as VanTabbarItem } from 'vant'

const route = useRoute()
const router = useRouter()

const tabs = [
  { path: '/', label: '总览', icon: 'home-o' },
  { path: '/analysis', label: '分析', icon: 'chart-trending-o' },
  { path: '/profile', label: '我的', icon: 'user-o' },
]

const activeTab = ref(0)

// Keep active tab in sync with current route
watch(
  () => route.path,
  (path) => {
    const idx = tabs.findIndex((t) => t.path === path)
    if (idx !== -1) activeTab.value = idx
  },
  { immediate: true },
)

function onTabChange(index: number | string) {
  const idx = typeof index === 'string' ? parseInt(index) : index
  const tab = tabs[idx]
  if (tab) router.push(tab.path)
}
</script>

<template>
  <div class="mobile-layout">
    <main class="mobile-content">
      <slot />
    </main>
    <van-tabbar v-model="activeTab" fixed placeholder @change="onTabChange">
      <van-tabbar-item v-for="tab in tabs" :key="tab.path" :icon="tab.icon">
        {{ tab.label }}
      </van-tabbar-item>
    </van-tabbar>
  </div>
</template>

<style scoped>
.mobile-layout {
  min-height: 100vh;
  background: var(--color-bg);
}

.mobile-content {
  /* Enough bottom padding so content doesn't sit behind the fixed tabbar */
  padding-bottom: 50px;
}
</style>
