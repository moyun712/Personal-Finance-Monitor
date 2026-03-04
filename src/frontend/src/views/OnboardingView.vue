<script setup lang="ts">
/**
 * OnboardingView — post-registration profile setup.
 * Standalone layout (no TabBar / sidebar).
 * Allows users to set monthly_income, payday, and nickname.
 */
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { showToast } from 'vant'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const nickname = ref('')
const monthlyIncome = ref<string>('')
const payday = ref<string>('')
const loading = ref(false)

// Payday picker columns (1-31)
const paydayColumns = Array.from({ length: 31 }, (_, i) => ({
  text: `${i + 1} 号`,
  value: i + 1,
}))
const showPaydayPicker = ref(false)
const paydayDisplay = ref('')

function onPaydayConfirm({ selectedOptions }: any) {
  const selected = selectedOptions[0]
  payday.value = String(selected.value)
  paydayDisplay.value = selected.text
  showPaydayPicker.value = false
}

async function handleSave() {
  loading.value = true
  try {
    const payload: Record<string, any> = {}
    if (nickname.value.trim()) {
      payload.nickname = nickname.value.trim()
    }
    if (monthlyIncome.value) {
      const income = parseFloat(monthlyIncome.value)
      if (isNaN(income) || income < 0) {
        showToast('请输入有效的月收入')
        loading.value = false
        return
      }
      payload.monthly_income = income
    }
    if (payday.value) {
      payload.payday = parseInt(payday.value)
    }

    if (Object.keys(payload).length > 0) {
      await authStore.updateProfile(payload)
    }

    authStore.needsOnboarding = false
    showToast('设置成功')
    router.replace('/')
  } catch (err: any) {
    const msg = err?.response?.data?.detail || '保存失败，请重试'
    showToast(msg)
  } finally {
    loading.value = false
  }
}

function handleSkip() {
  authStore.needsOnboarding = false
  router.replace('/')
}
</script>

<template>
  <div class="onboarding-page">
    <div class="onboarding-card">
      <h1>👋 完善你的财务信息</h1>
      <p class="subtitle">这些信息将帮助 AI 更好地为你提供财务建议</p>

      <van-cell-group inset>
        <van-field
          v-model="nickname"
          label="昵称"
          placeholder="你想怎么被称呼？"
        />
        <van-field
          v-model="monthlyIncome"
          type="number"
          label="月收入"
          placeholder="用于智能预算推荐"
        >
          <template #button>
            <span class="unit">元</span>
          </template>
        </van-field>
        <van-field
          v-model="paydayDisplay"
          readonly
          clickable
          label="发薪日"
          placeholder="选择发薪日"
          @click="showPaydayPicker = true"
        />
      </van-cell-group>

      <van-popup v-model:show="showPaydayPicker" round position="bottom">
        <van-picker
          :columns="paydayColumns"
          @confirm="onPaydayConfirm"
          @cancel="showPaydayPicker = false"
        />
      </van-popup>

      <div class="actions">
        <van-button
          type="primary"
          block
          round
          :loading="loading"
          loading-text="保存中..."
          @click="handleSave"
        >
          保存并进入
        </van-button>
        <van-button
          plain
          block
          round
          class="skip-btn"
          @click="handleSkip"
        >
          跳过，稍后设置
        </van-button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.onboarding-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-bg);
}

.onboarding-card {
  width: 100%;
  max-width: 420px;
  margin: 0 16px;
  padding: 40px 24px;
  background: var(--color-surface);
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  text-align: center;
}

.onboarding-card h1 {
  font-size: 22px;
  margin-bottom: 8px;
  color: var(--color-text-primary);
}

.subtitle {
  color: var(--color-text-secondary);
  font-size: 14px;
  margin-bottom: 24px;
}

.unit {
  color: var(--color-text-secondary);
  font-size: 14px;
}

.actions {
  margin: 24px 16px 0;
}

.skip-btn {
  margin-top: 12px;
  color: var(--color-text-secondary);
  border-color: var(--color-border);
}
</style>
