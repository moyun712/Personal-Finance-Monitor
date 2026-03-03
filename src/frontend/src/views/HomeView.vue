<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Button as VanButton } from 'vant'
import apiClient from '@/api'

const healthStatus = ref<string>('')

onMounted(async () => {
  try {
    const { data } = await apiClient.get('/health')
    healthStatus.value = JSON.stringify(data)
    console.log('Health check:', data)
  } catch (e) {
    healthStatus.value = '后端未启动'
    console.warn('Health check failed:', e)
  }
})
</script>

<template>
  <div class="page">
    <h1>资产总览</h1>
    <p class="subtitle">智能财务管理系统 — 开发中</p>
    <p class="health">Health: {{ healthStatus || '检查中...' }}</p>
    <van-button type="primary" size="small">Vant 测试按钮</van-button>
  </div>
</template>

<style scoped>
.page {
  padding: 16px;
}

.page h1 {
  font-size: 20px;
  margin-bottom: 4px;
  color: var(--color-text-primary);
}

.subtitle {
  color: var(--color-text-secondary);
  font-size: 14px;
  margin-bottom: 16px;
}

.health {
  color: var(--color-text-secondary);
  font-size: 13px;
  margin-bottom: 12px;
}
</style>
